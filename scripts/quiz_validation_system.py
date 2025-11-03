"""
Quiz Validation and Storage System

Purpose:
1. Store all quiz questions and system answers
2. Allow user validation (mark if system was correct/incorrect)
3. Track error patterns for system improvement
4. Build clean training dataset for future use

Usage:
  # Store quiz results
  python quiz_validation_system.py store \
    --dataset "Module Quiz" \
    --questions quiz_data.json

  # Validate answers
  python quiz_validation_system.py validate \
    --dataset "Module Quiz"

  # Show error patterns
  python quiz_validation_system.py analyze
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import sys


class QuizValidationSystem:
    """Manages quiz storage, validation, and error analysis."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)

    def close(self):
        """Close connection."""
        if self.conn:
            self.conn.close()

    def init_tables(self):
        """Create validation tracking tables."""
        self.conn.executescript('''
        -- Quiz datasets
        CREATE TABLE IF NOT EXISTS quiz_datasets (
            dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_name TEXT UNIQUE NOT NULL,
            date_taken DATE,
            total_questions INTEGER,
            reported_score REAL,      -- What you got on the quiz
            validated BOOLEAN DEFAULT 0,  -- Has user reviewed all answers?
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Individual questions with full context
        CREATE TABLE IF NOT EXISTS quiz_questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id INTEGER NOT NULL,
            question_number INTEGER,
            question_text TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            your_answer TEXT,                -- What you selected (A/B/C/D)
            correct_answer TEXT,             -- Official correct answer
            system_answer TEXT,              -- What our database suggested
            system_reasoning TEXT,           -- How system found the answer
            bia_sections_used TEXT,          -- JSON: ["50.4", "13.3"]
            study_material_sections_used TEXT, -- JSON: ["1.8.3"]
            retrieval_time_ms REAL,          -- How long to find answer

            -- User validation
            user_validated BOOLEAN DEFAULT 0,
            system_was_correct BOOLEAN,      -- Did system get it right?
            validation_notes TEXT,           -- User's notes on this question
            validation_date TIMESTAMP,

            FOREIGN KEY (dataset_id) REFERENCES quiz_datasets(dataset_id)
        );

        -- Error pattern tracking
        CREATE TABLE IF NOT EXISTS system_errors (
            error_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            error_type TEXT,  -- 'wrong_section', 'wrong_interpretation', 'missing_data', 'french_confusion'
            expected_result TEXT,
            actual_result TEXT,
            root_cause TEXT,
            fix_applied TEXT,
            fix_date TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES quiz_questions(question_id)
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_quiz_questions_dataset ON quiz_questions(dataset_id);
        CREATE INDEX IF NOT EXISTS idx_quiz_questions_validated ON quiz_questions(user_validated);
        CREATE INDEX IF NOT EXISTS idx_system_errors_type ON system_errors(error_type);

        -- Validation status view
        CREATE VIEW IF NOT EXISTS v_validation_status AS
        SELECT
            d.dataset_name,
            d.total_questions,
            COUNT(q.question_id) AS questions_stored,
            SUM(CASE WHEN q.user_validated = 1 THEN 1 ELSE 0 END) AS questions_validated,
            SUM(CASE WHEN q.system_was_correct = 1 THEN 1 ELSE 0 END) AS system_correct_count,
            ROUND(100.0 * SUM(CASE WHEN q.system_was_correct = 1 THEN 1 ELSE 0 END) /
                  NULLIF(SUM(CASE WHEN q.user_validated = 1 THEN 1 ELSE 0 END), 0), 1) AS system_accuracy_pct
        FROM quiz_datasets d
        LEFT JOIN quiz_questions q ON d.dataset_id = q.dataset_id
        GROUP BY d.dataset_name;

        -- Error pattern summary
        CREATE VIEW IF NOT EXISTS v_error_patterns AS
        SELECT
            error_type,
            COUNT(*) AS occurrences,
            COUNT(DISTINCT dataset_id) AS datasets_affected,
            GROUP_CONCAT(DISTINCT d.dataset_name) AS appeared_in
        FROM system_errors e
        JOIN quiz_questions q ON e.question_id = q.question_id
        JOIN quiz_datasets d ON q.dataset_id = d.dataset_id
        GROUP BY error_type
        ORDER BY occurrences DESC;
        ''')

        self.conn.commit()
        print('✓ Quiz validation tables initialized')

    def store_quiz(self, dataset_name: str, questions: list, date_taken: str = None, score: float = None):
        """Store a complete quiz with all questions and answers."""
        if date_taken is None:
            date_taken = datetime.now().strftime('%Y-%m-%d')

        # Create dataset
        cursor = self.conn.execute('''
            INSERT OR REPLACE INTO quiz_datasets (dataset_name, date_taken, total_questions, reported_score)
            VALUES (?, ?, ?, ?)
        ''', (dataset_name, date_taken, len(questions), score))

        dataset_id = cursor.lastrowid

        # Store each question
        for q in questions:
            self.conn.execute('''
                INSERT INTO quiz_questions
                (dataset_id, question_number, question_text, option_a, option_b, option_c, option_d,
                 your_answer, correct_answer, system_answer, system_reasoning,
                 bia_sections_used, study_material_sections_used, retrieval_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dataset_id,
                q.get('number'),
                q.get('question'),
                q.get('option_a'),
                q.get('option_b'),
                q.get('option_c'),
                q.get('option_d'),
                q.get('your_answer'),
                q.get('correct_answer'),
                q.get('system_answer'),
                q.get('system_reasoning'),
                json.dumps(q.get('bia_sections', [])),
                json.dumps(q.get('study_material_sections', [])),
                q.get('retrieval_time_ms')
            ))

        self.conn.commit()
        print(f'✓ Stored {len(questions)} questions for dataset: {dataset_name}')

    def interactive_validation(self, dataset_name: str):
        """Interactive validation of quiz answers."""
        cursor = self.conn.execute('''
            SELECT question_id, question_number, question_text, system_answer, correct_answer,
                   system_reasoning, your_answer, user_validated
            FROM quiz_questions q
            JOIN quiz_datasets d ON q.dataset_id = d.dataset_id
            WHERE d.dataset_name = ?
            ORDER BY question_number
        ''', (dataset_name,))

        questions = cursor.fetchall()

        print(f'\n{"="*70}')
        print(f'VALIDATING: {dataset_name}')
        print(f'{"="*70}\n')

        validated_count = 0

        for q in questions:
            qid, qnum, qtext, sys_answer, correct_answer, reasoning, your_answer, already_validated = q

            if already_validated:
                validated_count += 1
                continue

            print(f'\n{"="*70}')
            print(f'Question {qnum}: {qtext[:100]}...')
            print(f'{"="*70}')
            print(f'Your answer:    {your_answer}')
            print(f'Correct answer: {correct_answer}')
            print(f'System answer:  {sys_answer}')
            print(f'\nSystem reasoning: {reasoning[:200]}...' if reasoning else '\nNo reasoning recorded')

            # Ask user validation
            print(f'\nDid the SYSTEM get this correct?')
            validation = input('  (y/n/s=skip): ').lower()

            if validation == 's':
                continue

            system_correct = (validation == 'y')

            # If incorrect, ask for error details
            error_notes = None
            error_type = None

            if not system_correct:
                print('\nWhat went wrong?')
                print('  1. Wrong section searched')
                print('  2. Wrong interpretation of provision')
                print('  3. Missing data in database')
                print('  4. French confusion')
                print('  5. Other')

                error_choice = input('Select (1-5): ')
                error_types = {
                    '1': 'wrong_section',
                    '2': 'wrong_interpretation',
                    '3': 'missing_data',
                    '4': 'french_confusion',
                    '5': 'other'
                }
                error_type = error_types.get(error_choice, 'other')

                error_notes = input('Notes on this error: ')

                # Record error
                self.conn.execute('''
                    INSERT INTO system_errors (question_id, error_type, expected_result, actual_result, root_cause)
                    VALUES (?, ?, ?, ?, ?)
                ''', (qid, error_type, correct_answer, sys_answer, error_notes))

            # Mark as validated
            self.conn.execute('''
                UPDATE quiz_questions
                SET user_validated = 1,
                    system_was_correct = ?,
                    validation_notes = ?,
                    validation_date = ?
                WHERE question_id = ?
            ''', (system_correct, error_notes, datetime.now().isoformat(), qid))

            self.conn.commit()
            validated_count += 1

        # Mark dataset as validated if all questions done
        if validated_count == len(questions):
            self.conn.execute('''
                UPDATE quiz_datasets SET validated = 1 WHERE dataset_name = ?
            ''', (dataset_name,))
            self.conn.commit()

        print(f'\n✓ Validated {validated_count}/{len(questions)} questions')

    def show_validation_status(self):
        """Show validation status across all datasets."""
        cursor = self.conn.execute('SELECT * FROM v_validation_status')

        print('\n' + '='*70)
        print('QUIZ VALIDATION STATUS')
        print('='*70 + '\n')

        for row in cursor.fetchall():
            name, total, stored, validated, correct, accuracy = row
            print(f'{name}:')
            print(f'  Stored: {stored}/{total} questions')
            print(f'  Validated: {validated}/{stored} questions')
            if validated > 0:
                print(f'  System Accuracy: {accuracy}% ({correct}/{validated} correct)')
            print()

    def analyze_errors(self):
        """Analyze error patterns."""
        cursor = self.conn.execute('SELECT * FROM v_error_patterns')
        results = cursor.fetchall()

        if not results:
            print('\n✓ No errors detected! System performing perfectly.')
            return

        print('\n' + '='*70)
        print('ERROR PATTERN ANALYSIS')
        print('='*70 + '\n')

        for row in results:
            error_type, count, datasets, appeared_in = row
            print(f'{error_type:25s}: {count} occurrences across {datasets} dataset(s)')
            print(f'  Appeared in: {appeared_in}')
            print()

        # Show specific errors
        print('\nDetailed Errors:')
        print('-'*70)

        cursor = self.conn.execute('''
            SELECT
                d.dataset_name,
                q.question_text,
                e.error_type,
                e.root_cause
            FROM system_errors e
            JOIN quiz_questions q ON e.question_id = q.question_id
            JOIN quiz_datasets d ON q.dataset_id = d.dataset_id
            ORDER BY e.error_id DESC
            LIMIT 10
        ''')

        for row in cursor.fetchall():
            dataset, question, err_type, cause = row
            print(f'\n[{dataset}] {err_type}')
            print(f'  Q: {question[:80]}...')
            print(f'  Cause: {cause}')

    def export_training_data(self, output_file: Path):
        """Export validated questions as clean training data."""
        cursor = self.conn.execute('''
            SELECT
                d.dataset_name,
                q.question_text,
                q.option_a, q.option_b, q.option_c, q.option_d,
                q.correct_answer,
                q.bia_sections_used,
                q.study_material_sections_used,
                q.system_reasoning,
                q.system_was_correct
            FROM quiz_questions q
            JOIN quiz_datasets d ON q.dataset_id = d.dataset_id
            WHERE q.user_validated = 1
            ORDER BY d.dataset_name, q.question_number
        ''')

        training_data = []
        for row in cursor.fetchall():
            training_data.append({
                'dataset': row[0],
                'question': row[1],
                'options': {'A': row[2], 'B': row[3], 'C': row[4], 'D': row[5]},
                'correct_answer': row[6],
                'bia_sections': json.loads(row[7]) if row[7] else [],
                'study_material_sections': json.loads(row[8]) if row[8] else [],
                'reasoning': row[9],
                'system_correct': row[10]
            })

        with open(output_file, 'w') as f:
            json.dump(training_data, f, indent=2)

        print(f'✓ Exported {len(training_data)} validated questions to {output_file}')


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description='Quiz Validation System')
    parser.add_argument('command', choices=['init', 'store', 'validate', 'status', 'analyze', 'export'])
    parser.add_argument('--dataset', type=str, help='Dataset name')
    parser.add_argument('--questions', type=str, help='JSON file with questions')
    parser.add_argument('--output', type=str, help='Output file for export')

    args = parser.parse_args()

    db_path = Path('data/output/insolvency_knowledge.db')
    system = QuizValidationSystem(db_path)
    system.connect()

    if args.command == 'init':
        system.init_tables()

    elif args.command == 'store':
        if not args.dataset or not args.questions:
            print('Error: --dataset and --questions required')
            sys.exit(1)

        with open(args.questions, 'r') as f:
            questions = json.load(f)

        system.store_quiz(args.dataset, questions)

    elif args.command == 'validate':
        if not args.dataset:
            print('Error: --dataset required')
            sys.exit(1)

        system.interactive_validation(args.dataset)

    elif args.command == 'status':
        system.show_validation_status()

    elif args.command == 'analyze':
        system.analyze_errors()

    elif args.command == 'export':
        output = Path(args.output) if args.output else Path('data/output/validated_training_data.json')
        system.export_training_data(output)

    system.close()


if __name__ == '__main__':
    main()

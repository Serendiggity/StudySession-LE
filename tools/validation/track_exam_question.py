"""
Exam Question Tracker - Build exam intelligence from actual test data.

Usage:
  python track_exam_question.py --dataset "Module Quiz" \
    --question "What are extension limits?" \
    --sections "50.4" \
    --correct True

This builds up real exam frequency data over time.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

db_path = Path('data/output/insolvency_knowledge.db')


def init_exam_tracking():
    """Create exam tracking tables."""
    conn = sqlite3.connect(db_path)

    conn.executescript('''
    -- Track exam/quiz datasets
    CREATE TABLE IF NOT EXISTS exam_datasets (
        dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_name TEXT UNIQUE NOT NULL,  -- "Module Quiz", "2022 Past Questions IA"
        date_completed DATE,
        total_questions INTEGER,
        score_percentage REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Track individual questions
    CREATE TABLE IF NOT EXISTS exam_questions (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        question_number INTEGER,
        correct BOOLEAN,
        bia_sections TEXT,              -- JSON array: ["50.4", "50"]
        study_material_sections TEXT,   -- JSON array: ["1.8.3"]
        topic_category TEXT,            -- "Proposals", "Trustee Duties", etc.
        notes TEXT,
        FOREIGN KEY (dataset_id) REFERENCES exam_datasets(dataset_id)
    );

    -- Note: Section frequency analysis done via queries, not views (simpler)

    CREATE INDEX IF NOT EXISTS idx_exam_questions_dataset ON exam_questions(dataset_id);
    CREATE INDEX IF NOT EXISTS idx_exam_questions_correct ON exam_questions(correct);
    ''')

    conn.commit()
    conn.close()
    print('✓ Exam tracking tables initialized')


def add_dataset(dataset_name: str, date_completed: str = None,
                total_questions: int = None, score_percentage: float = None):
    """Register a new exam/quiz dataset."""
    conn = sqlite3.connect(db_path)

    if date_completed is None:
        date_completed = datetime.now().strftime('%Y-%m-%d')

    cursor = conn.execute('''
        INSERT OR IGNORE INTO exam_datasets (dataset_name, date_completed, total_questions, score_percentage)
        VALUES (?, ?, ?, ?)
    ''', (dataset_name, date_completed, total_questions, score_percentage))

    dataset_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return dataset_id


def add_question(dataset_name: str, question_text: str,
                bia_sections: list = None, study_material_sections: list = None,
                correct: bool = True, topic_category: str = None, question_number: int = None):
    """Add a question to tracking database."""
    conn = sqlite3.connect(db_path)

    # Get dataset_id
    cursor = conn.execute('SELECT dataset_id FROM exam_datasets WHERE dataset_name = ?', (dataset_name,))
    result = cursor.fetchone()

    if not result:
        print(f'Dataset "{dataset_name}" not found. Creating...')
        add_dataset(dataset_name)
        cursor = conn.execute('SELECT dataset_id FROM exam_datasets WHERE dataset_name = ?', (dataset_name,))
        result = cursor.fetchone()

    dataset_id = result[0]

    # Add question
    conn.execute('''
        INSERT INTO exam_questions
        (dataset_id, question_text, question_number, correct, bia_sections, study_material_sections, topic_category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        dataset_id,
        question_text,
        question_number,
        correct,
        json.dumps(bia_sections or []),
        json.dumps(study_material_sections or []),
        topic_category
    ))

    conn.commit()
    conn.close()

    print(f'✓ Added question to {dataset_name}')


def show_frequency_report(dataset_filter: str = None):
    """Show section frequency report."""
    conn = sqlite3.connect(db_path)

    if dataset_filter:
        print(f'\n=== Exam Pattern Analysis: {dataset_filter} ===\n')

        # Get all questions from this dataset
        cursor = conn.execute('''
            SELECT bia_sections, study_material_sections, correct, topic_category
            FROM exam_questions q
            JOIN exam_datasets d ON q.dataset_id = d.dataset_id
            WHERE d.dataset_name = ?
        ''', (dataset_filter,))

        results = cursor.fetchall()

        # Manual frequency counting (simpler than JSON parsing in SQL)
        bia_freq = {}
        sm_freq = {}

        for row in results:
            bia_sections_json, sm_sections_json, correct, topic = row

            # Parse BIA sections
            bia_sections = json.loads(bia_sections_json) if bia_sections_json else []
            for section in bia_sections:
                if section not in bia_freq:
                    bia_freq[section] = {'tested': 0, 'correct': 0, 'incorrect': 0}
                bia_freq[section]['tested'] += 1
                if correct:
                    bia_freq[section]['correct'] += 1
                else:
                    bia_freq[section]['incorrect'] += 1

            # Parse SM sections
            sm_sections = json.loads(sm_sections_json) if sm_sections_json else []
            for section in sm_sections:
                if section not in sm_freq:
                    sm_freq[section] = {'tested': 0, 'correct': 0, 'incorrect': 0}
                sm_freq[section]['tested'] += 1
                if correct:
                    sm_freq[section]['correct'] += 1
                else:
                    sm_freq[section]['incorrect'] += 1

        print('BIA Sections - Frequency:')
        print('-' * 80)
        for section in sorted(bia_freq.items(), key=lambda x: x[1]['tested'], reverse=True):
            name, stats = section
            print(f'BIA s. {name:10s}: {stats["tested"]} questions '
                  f'({stats["correct"]} correct, {stats["incorrect"]} incorrect)')

        if sm_freq:
            print('\nStudy Material Sections - Frequency:')
            print('-' * 80)
            for section in sorted(sm_freq.items(), key=lambda x: x[1]['tested'], reverse=True):
                name, stats = section
                print(f'SM {name:10s}: {stats["tested"]} questions '
                      f'({stats["correct"]} correct, {stats["incorrect"]} incorrect)')

    else:
        print('\n=== Exam Pattern Analysis: ALL DATASETS ===\n')
        cursor = conn.execute('SELECT * FROM exam_datasets')
        datasets = cursor.fetchall()

        for dataset in datasets:
            dataset_id, name, date, total, score, notes, created = dataset
            print(f'{name}: {total} questions, {score}% score ({date})')

    conn.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Track exam questions for pattern analysis')
    parser.add_argument('--init', action='store_true', help='Initialize tracking tables')
    parser.add_argument('--dataset', type=str, help='Dataset name (e.g., "Module Quiz")')
    parser.add_argument('--load-sample', action='store_true', help='Load Module Quiz data')
    parser.add_argument('--report', type=str, help='Show frequency report for dataset')

    args = parser.parse_args()

    if args.init:
        init_exam_tracking()

    elif args.load_sample:
        # Load the Module Quiz data we already have
        print('Loading Module Quiz data...')
        init_exam_tracking()
        add_dataset('Module Quiz', '2025-11-02', 10, 100.0)

        # Add each question
        questions = [
            ('Q1: Proposal extension time limits', ['50.4'], [], True, 'Proposals'),
            ('Q2: Trustee qualification - related to director', ['13.3'], [], True, 'Trustee Qualifications'),
            ('Q3: Trustee confidentiality obligations', [], ['1.8.3'], True, 'Professional Standards'),
            ('Q4: Material adverse change reporting', ['50.4', '50'], [], True, 'Proposals'),
            ('Q5: Receiver disclosure requirements', ['13.3'], [], True, 'Trustee Duties'),
            ('Q8: Insolvent person definition', ['2'], [], True, 'Definitions'),
            ('Q9: Estate fund separate accounts', ['25'], [], True, 'Estate Administration'),
            ('Q10: CAIRP standards source', [], ['1.7.1', '1.2'], True, 'Professional Standards'),
            ('Q11: Trustee can act - 3 years ago director', ['13.3'], [], True, 'Trustee Qualifications'),
            ('Q15: Who can inspect books', ['26'], [], True, 'Trustee Duties'),
        ]

        for q in questions:
            add_question('Module Quiz', q[0], q[1], q[2], q[3], q[4], question_number=None)

        print(f'✓ Loaded {len(questions)} questions')
        show_frequency_report('Module Quiz')

    elif args.report:
        show_frequency_report(args.report if args.report != 'ALL' else None)

    else:
        parser.print_help()

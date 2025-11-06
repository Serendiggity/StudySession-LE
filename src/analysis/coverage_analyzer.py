#!/usr/bin/env python3
"""
Coverage Analyzer Module

Analyzes study guide completeness by checking coverage of database entities.
Identifies gaps and missing content to ensure comprehensive study guides.
"""

import sqlite3
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """Coverage metrics for a single entity type."""
    entity_type: str
    total_relevant: int
    mentioned: int
    missing: int
    coverage_percentage: float
    sample_missing: List[str]


@dataclass
class CoverageReport:
    """Complete coverage analysis report."""
    topic: str
    overall_score: float
    entity_coverage: Dict[str, CoverageMetrics]
    cross_reference_coverage: Dict[str, any]
    timeline_coverage: Dict[str, any]
    form_coverage: Dict[str, any]
    gaps: List[str]
    recommendations: List[str]


class CoverageAnalyzer:
    """
    Analyzes study guide coverage against database entities.

    Checks whether study guide mentions all relevant:
    - Concepts
    - Procedures
    - Deadlines
    - Documents/Forms
    - Actors
    - Consequences
    - Statutory references
    - Cross-references
    """

    def __init__(self, db_path: Path):
        """
        Initialize coverage analyzer.

        Args:
            db_path: Path to SQLite knowledge database
        """
        self.db_path = db_path

    def _get_relevant_entities(
        self,
        table_name: str,
        topic: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get entities relevant to a topic from database.

        Args:
            table_name: Entity table to query
            topic: Topic to search for
            limit: Maximum entities to return

        Returns:
            List of entity dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            """, (table_name,))

            if not cursor.fetchone():
                logger.warning(f"Table {table_name} not found")
                return []

            # Get table columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]

            # Build query based on available columns
            if 'extraction_text' in columns:
                text_col = 'extraction_text'
            elif 'full_text' in columns:
                text_col = 'full_text'
            elif 'relationship_text' in columns:
                text_col = 'relationship_text'
            else:
                logger.warning(f"No text column found in {table_name}")
                return []

            # Search for relevant entities
            fts_table = f"{table_name}_fts"
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            """, (fts_table,))

            if cursor.fetchone():
                # Use FTS search
                select_cols = ', '.join(columns)
                cursor.execute(f"""
                    SELECT {select_cols}
                    FROM {table_name}
                    WHERE rowid IN (
                        SELECT rowid FROM {fts_table}
                        WHERE {text_col} MATCH ?
                    )
                    LIMIT ?
                """, (topic, limit))
            else:
                # Fallback to LIKE search
                select_cols = ', '.join(columns)
                cursor.execute(f"""
                    SELECT {select_cols}
                    FROM {table_name}
                    WHERE {text_col} LIKE ?
                    LIMIT ?
                """, (f'%{topic}%', limit))

            rows = cursor.fetchall()

            # Convert to dictionaries
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            return results

        finally:
            conn.close()

    def _extract_section_references(self, text: str) -> Set[str]:
        """
        Extract section references from text.

        Patterns:
        - Section 123
        - §123
        - s.123
        - sec. 123

        Args:
            text: Text to extract from

        Returns:
            Set of section numbers
        """
        patterns = [
            r'[Ss]ection\s+(\d+(?:\.\d+)?)',
            r'§\s*(\d+(?:\.\d+)?)',
            r's\.\s*(\d+(?:\.\d+)?)',
            r'sec\.\s*(\d+(?:\.\d+)?)',
            r'BIA\s+(\d+(?:\.\d+)?)',
        ]

        references = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            references.update(matches)

        return references

    def _check_mentioned(
        self,
        entity_text: str,
        study_guide_text: str,
        fuzzy: bool = True
    ) -> bool:
        """
        Check if entity is mentioned in study guide.

        Args:
            entity_text: Text from entity to find
            study_guide_text: Study guide text to search in
            fuzzy: Allow fuzzy matching (word stemming)

        Returns:
            True if mentioned
        """
        # Normalize both texts
        entity_lower = entity_text.lower()
        guide_lower = study_guide_text.lower()

        # Exact substring match
        if entity_lower in guide_lower:
            return True

        if not fuzzy:
            return False

        # Fuzzy: check if key words are present
        # Extract meaningful words (> 3 chars, not common)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could',
            'may', 'might', 'must', 'can', 'that', 'this', 'these',
            'those', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
        }

        entity_words = [
            w for w in entity_lower.split()
            if len(w) > 3 and w not in stop_words
        ]

        if not entity_words:
            return False

        # Check if majority of key words are present
        found_count = sum(1 for word in entity_words if word in guide_lower)
        threshold = 0.6  # 60% of words must be present

        return (found_count / len(entity_words)) >= threshold

    def analyze_entity_coverage(
        self,
        topic: str,
        study_guide_text: str,
        entity_tables: List[str] = None
    ) -> Dict[str, CoverageMetrics]:
        """
        Analyze coverage of all entity types.

        Args:
            topic: Topic being studied
            study_guide_text: Study guide content
            entity_tables: List of tables to check (default: all)

        Returns:
            Dictionary mapping entity type to coverage metrics
        """
        if entity_tables is None:
            entity_tables = [
                'concepts',
                'procedures',
                'deadlines',
                'documents',
                'actors',
                'consequences',
                'statutory_references',
            ]

        coverage = {}

        for table in entity_tables:
            # Get relevant entities
            entities = self._get_relevant_entities(table, topic)

            if not entities:
                continue

            # Check which are mentioned
            mentioned_count = 0
            missing_examples = []

            for entity in entities:
                # Get text to check
                text_to_find = (
                    entity.get('extraction_text') or
                    entity.get('term') or
                    entity.get('step_name') or
                    entity.get('role_canonical') or
                    str(entity.get('id', ''))
                )

                if self._check_mentioned(text_to_find, study_guide_text):
                    mentioned_count += 1
                else:
                    # Add to missing examples (limit to 5)
                    if len(missing_examples) < 5:
                        missing_examples.append(text_to_find[:100])

            total = len(entities)
            missing = total - mentioned_count
            percentage = (mentioned_count / total * 100) if total > 0 else 0

            coverage[table] = CoverageMetrics(
                entity_type=table,
                total_relevant=total,
                mentioned=mentioned_count,
                missing=missing,
                coverage_percentage=percentage,
                sample_missing=missing_examples
            )

        return coverage

    def analyze_cross_references(
        self,
        topic: str,
        study_guide_text: str
    ) -> Dict[str, any]:
        """
        Analyze cross-reference coverage.

        Checks if all referenced sections are actually retrieved/included.

        Args:
            topic: Topic being studied
            study_guide_text: Study guide content

        Returns:
            Cross-reference coverage metrics
        """
        # Extract references from study guide
        guide_refs = self._extract_section_references(study_guide_text)

        # Get references from database for this topic
        db_refs = set()

        # Check statutory_references table
        statutory_entities = self._get_relevant_entities('statutory_references', topic)
        for entity in statutory_entities:
            section_num = entity.get('section_number', '')
            if section_num:
                db_refs.add(str(section_num))

        # Check BIA sections mentioned in relationships
        relationships = self._get_relevant_entities('relationships', topic)
        for rel in relationships:
            text = rel.get('relationship_text', '')
            refs = self._extract_section_references(text)
            db_refs.update(refs)

        # Calculate coverage
        if not db_refs:
            return {
                'total_db_refs': 0,
                'mentioned_in_guide': 0,
                'missing_refs': [],
                'coverage_percentage': 100.0
            }

        mentioned_refs = guide_refs & db_refs
        missing_refs = list(db_refs - guide_refs)

        coverage_pct = (len(mentioned_refs) / len(db_refs) * 100) if db_refs else 100.0

        return {
            'total_db_refs': len(db_refs),
            'mentioned_in_guide': len(mentioned_refs),
            'missing_refs': missing_refs[:10],  # Limit to 10
            'coverage_percentage': coverage_pct
        }

    def analyze_timeline_coverage(
        self,
        topic: str,
        study_guide_text: str
    ) -> Dict[str, any]:
        """
        Analyze timeline/deadline coverage.

        Args:
            topic: Topic being studied
            study_guide_text: Study guide content

        Returns:
            Timeline coverage metrics
        """
        deadlines = self._get_relevant_entities('deadlines', topic)

        if not deadlines:
            return {
                'total_deadlines': 0,
                'mentioned': 0,
                'missing': 0,
                'coverage_percentage': 100.0,
                'sample_missing': []
            }

        mentioned_count = 0
        missing_examples = []

        for deadline in deadlines:
            text = deadline.get('extraction_text', '')
            timeframe = deadline.get('timeframe', '')

            # Check if deadline or timeframe is mentioned
            if (self._check_mentioned(text, study_guide_text) or
                self._check_mentioned(timeframe, study_guide_text)):
                mentioned_count += 1
            else:
                if len(missing_examples) < 5:
                    missing_examples.append(f"{timeframe}: {text[:80]}")

        total = len(deadlines)
        missing = total - mentioned_count
        coverage_pct = (mentioned_count / total * 100) if total > 0 else 100.0

        return {
            'total_deadlines': total,
            'mentioned': mentioned_count,
            'missing': missing,
            'coverage_percentage': coverage_pct,
            'sample_missing': missing_examples
        }

    def analyze_form_coverage(
        self,
        topic: str,
        study_guide_text: str
    ) -> Dict[str, any]:
        """
        Analyze form/document coverage.

        Args:
            topic: Topic being studied
            study_guide_text: Study guide content

        Returns:
            Form coverage metrics
        """
        documents = self._get_relevant_entities('documents', topic)

        if not documents:
            return {
                'total_forms': 0,
                'mentioned': 0,
                'missing': 0,
                'coverage_percentage': 100.0,
                'sample_missing': []
            }

        mentioned_count = 0
        missing_examples = []

        for doc in documents:
            text = doc.get('extraction_text', '')

            if self._check_mentioned(text, study_guide_text):
                mentioned_count += 1
            else:
                if len(missing_examples) < 5:
                    missing_examples.append(text[:80])

        total = len(documents)
        missing = total - mentioned_count
        coverage_pct = (mentioned_count / total * 100) if total > 0 else 100.0

        return {
            'total_forms': total,
            'mentioned': mentioned_count,
            'missing': missing,
            'coverage_percentage': coverage_pct,
            'sample_missing': missing_examples
        }

    def analyze(
        self,
        topic: str,
        study_guide_text: str
    ) -> CoverageReport:
        """
        Comprehensive coverage analysis.

        Args:
            topic: Topic being analyzed
            study_guide_text: Study guide content

        Returns:
            Complete coverage report
        """
        # Analyze entity coverage
        entity_coverage = self.analyze_entity_coverage(topic, study_guide_text)

        # Analyze cross-references
        cross_ref_coverage = self.analyze_cross_references(topic, study_guide_text)

        # Analyze timelines
        timeline_coverage = self.analyze_timeline_coverage(topic, study_guide_text)

        # Analyze forms
        form_coverage = self.analyze_form_coverage(topic, study_guide_text)

        # Calculate overall score (weighted average)
        scores = []
        weights = []

        for metrics in entity_coverage.values():
            scores.append(metrics.coverage_percentage)
            weights.append(metrics.total_relevant)

        if cross_ref_coverage['total_db_refs'] > 0:
            scores.append(cross_ref_coverage['coverage_percentage'])
            weights.append(cross_ref_coverage['total_db_refs'])

        if timeline_coverage['total_deadlines'] > 0:
            scores.append(timeline_coverage['coverage_percentage'])
            weights.append(timeline_coverage['total_deadlines'])

        if form_coverage['total_forms'] > 0:
            scores.append(form_coverage['coverage_percentage'])
            weights.append(form_coverage['total_forms'])

        # Weighted average
        if scores:
            overall_score = sum(s*w for s,w in zip(scores, weights)) / sum(weights)
        else:
            overall_score = 0.0

        # Identify gaps
        gaps = []

        for entity_type, metrics in entity_coverage.items():
            if metrics.coverage_percentage < 80:
                gaps.append(
                    f"Low {entity_type} coverage: {metrics.coverage_percentage:.1f}% "
                    f"({metrics.missing} of {metrics.total_relevant} missing)"
                )

        if cross_ref_coverage['coverage_percentage'] < 80:
            gaps.append(
                f"Missing {len(cross_ref_coverage['missing_refs'])} cross-references"
            )

        if timeline_coverage['coverage_percentage'] < 80:
            gaps.append(
                f"Missing {timeline_coverage['missing']} deadlines"
            )

        if form_coverage['coverage_percentage'] < 80:
            gaps.append(
                f"Missing {form_coverage['missing']} forms/documents"
            )

        # Generate recommendations
        recommendations = []

        if overall_score < 70:
            recommendations.append("Overall coverage is LOW. Consider comprehensive rewrite.")
        elif overall_score < 85:
            recommendations.append("Coverage is MODERATE. Focus on identified gaps.")
        else:
            recommendations.append("Coverage is GOOD. Minor improvements needed.")

        for entity_type, metrics in entity_coverage.items():
            if metrics.coverage_percentage < 70 and metrics.total_relevant > 0:
                recommendations.append(
                    f"Add more {entity_type} (currently {metrics.coverage_percentage:.1f}%)"
                )

        return CoverageReport(
            topic=topic,
            overall_score=overall_score,
            entity_coverage=entity_coverage,
            cross_reference_coverage=cross_ref_coverage,
            timeline_coverage=timeline_coverage,
            form_coverage=form_coverage,
            gaps=gaps,
            recommendations=recommendations
        )

    def print_report(self, report: CoverageReport):
        """Print coverage report in human-readable format."""
        print(f"\n{'='*60}")
        print(f"COVERAGE ANALYSIS: {report.topic}")
        print(f"{'='*60}")
        print(f"Overall Score: {report.overall_score:.1f}%")
        print(f"{'='*60}\n")

        # Entity coverage
        print("ENTITY COVERAGE:")
        print("-" * 60)
        for entity_type, metrics in report.entity_coverage.items():
            status = "✅" if metrics.coverage_percentage >= 80 else "⚠️" if metrics.coverage_percentage >= 60 else "❌"
            print(f"{status} {entity_type.capitalize():20s}: {metrics.coverage_percentage:5.1f}% "
                  f"({metrics.mentioned}/{metrics.total_relevant})")

            if metrics.sample_missing:
                print(f"    Missing examples:")
                for example in metrics.sample_missing[:3]:
                    print(f"      - {example}")

        # Cross-references
        print(f"\n{'='*60}")
        print("CROSS-REFERENCES:")
        print("-" * 60)
        cr = report.cross_reference_coverage
        status = "✅" if cr['coverage_percentage'] >= 80 else "⚠️" if cr['coverage_percentage'] >= 60 else "❌"
        print(f"{status} Coverage: {cr['coverage_percentage']:.1f}% "
              f"({cr['mentioned_in_guide']}/{cr['total_db_refs']})")
        if cr['missing_refs']:
            print(f"    Missing: {', '.join(cr['missing_refs'][:5])}")

        # Timelines
        print(f"\n{'='*60}")
        print("TIMELINES/DEADLINES:")
        print("-" * 60)
        tl = report.timeline_coverage
        status = "✅" if tl['coverage_percentage'] >= 80 else "⚠️" if tl['coverage_percentage'] >= 60 else "❌"
        print(f"{status} Coverage: {tl['coverage_percentage']:.1f}% "
              f"({tl['mentioned']}/{tl['total_deadlines']})")
        if tl['sample_missing']:
            print(f"    Missing examples:")
            for example in tl['sample_missing'][:3]:
                print(f"      - {example}")

        # Forms
        print(f"\n{'='*60}")
        print("FORMS/DOCUMENTS:")
        print("-" * 60)
        fm = report.form_coverage
        status = "✅" if fm['coverage_percentage'] >= 80 else "⚠️" if fm['coverage_percentage'] >= 60 else "❌"
        print(f"{status} Coverage: {fm['coverage_percentage']:.1f}% "
              f"({fm['mentioned']}/{fm['total_forms']})")
        if fm['sample_missing']:
            print(f"    Missing examples:")
            for example in fm['sample_missing'][:3]:
                print(f"      - {example}")

        # Gaps
        if report.gaps:
            print(f"\n{'='*60}")
            print("IDENTIFIED GAPS:")
            print("-" * 60)
            for gap in report.gaps:
                print(f"  - {gap}")

        # Recommendations
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS:")
        print("-" * 60)
        for rec in report.recommendations:
            print(f"  - {rec}")

        print(f"\n{'='*60}\n")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 4:
        print("Usage: python coverage_analyzer.py <database_path> <topic> <study_guide_file>")
        print("\nExample:")
        print("  python coverage_analyzer.py projects/insolvency-law/database/knowledge.db 'consumer proposals' guide.md")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    db_path = Path(sys.argv[1])
    topic = sys.argv[2]
    guide_file = Path(sys.argv[3])

    if not db_path.exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)

    if not guide_file.exists():
        print(f"Error: Study guide not found: {guide_file}")
        sys.exit(1)

    # Read study guide
    study_guide_text = guide_file.read_text(encoding='utf-8')

    # Analyze coverage
    analyzer = CoverageAnalyzer(db_path)
    report = analyzer.analyze(topic, study_guide_text)

    # Print report
    analyzer.print_report(report)

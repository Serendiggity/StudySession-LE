"""
Schema definitions for all 15 extraction categories.
Includes standard categories plus visualization-specific categories.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import langextract as lx


@dataclass
class ExtractionCategory:
    """
    Definition of an extraction category.

    Attributes:
        name: Category identifier (e.g., "concepts", "deadlines")
        description: What this category captures
        attributes: List of attribute names to extract
        prompt_template: Prompt describing what to extract
        examples: List of ExampleData objects (3-5 recommended)
        priority: Extraction priority (1=highest, 3=lowest)
        passes: Number of extraction passes (default: 3)
    """
    name: str
    description: str
    attributes: List[str]
    prompt_template: str
    examples: List[lx.data.ExampleData] = field(default_factory=list)
    priority: int = 2
    passes: int = 3


# Schema definitions will be populated with examples in data/examples/
# For now, defining the structure

def create_concepts_category(examples: List[lx.data.ExampleData]) -> ExtractionCategory:
    """Create concepts extraction category."""
    return ExtractionCategory(
        name="concepts",
        description="Key terms and definitions in insolvency law",
        attributes=[
            "term",
            "definition",
            "source_act",
            "section_reference",
            "context",
            "importance_level",
            "related_terms"
        ],
        prompt_template="""
        Extract key insolvency concepts and their definitions from the text.
        Focus on terms central to insolvency law and practice.
        Include the act and section where defined if mentioned.
        Mark importance as high, medium, or low based on exam relevance.
        """,
        examples=examples,
        priority=1,
        passes=3
    )


def create_statutory_references_category(examples: List[lx.data.ExampleData]) -> ExtractionCategory:
    """Create statutory references extraction category."""
    return ExtractionCategory(
        name="statutory_references",
        description="Specific citations to legislation (BIA, CCAA, etc.)",
        attributes=[
            "act_name",
            "section_number",
            "subsection",
            "provision_text",
            "practical_effect",
            "related_sections",
            "frequency_of_reference"
        ],
        prompt_template="""
        Extract all statutory references including act name, section number, and
        what the provision means in practice. Focus on BIA (Bankruptcy and Insolvency Act)
        and CCAA (Companies' Creditors Arrangement Act) references.
        Include cross-references to related sections if mentioned.
        """,
        examples=examples,
        priority=1,
        passes=3
    )


def create_deadlines_category(examples: List[lx.data.ExampleData]) -> ExtractionCategory:
    """Create deadlines extraction category - CRITICAL for exam!"""
    return ExtractionCategory(
        name="deadlines",
        description="Time-sensitive requirements with calculation methods",
        attributes=[
            "deadline_type",
            "timeframe",
            "calculation_method",
            "day_type_specified",
            "exclude_holidays",
            "exclude_weekends",
            "triggering_event",
            "required_action",
            "responsible_party",
            "recipient",
            "statutory_reference",
            "consequences_if_missed",
            "extension_available",
            "common_pitfalls"
        ],
        prompt_template="""
        Extract all deadlines and time-sensitive requirements.
        CRITICAL: Identify if timeframe is business days, calendar days, or clear days.
        Extract triggering event, responsible party, what must be done, and consequences if missed.
        Note common calculation pitfalls.
        """,
        examples=examples,
        priority=1,
        passes=3
    )


def create_timeline_sequences_category(examples: List[lx.data.ExampleData]) -> ExtractionCategory:
    """Create timeline sequences category - NEW for swimlane diagrams!"""
    return ExtractionCategory(
        name="timeline_sequences",
        description="Complete event sequences for insolvency scenarios",
        attributes=[
            "scenario_name",
            "scenario_type",
            "sequence_steps",
            "total_duration",
            "statutory_basis",
            "actors_involved"
        ],
        prompt_template="""
        Extract complete sequences of events for insolvency scenarios.
        For each step, identify: timing, responsible actor, required documents, deadlines.
        Capture the full timeline from initiation to completion.
        Note dependencies between steps (what must happen before what).
        """,
        examples=examples,
        priority=2,
        passes=2
    )


def create_decision_points_category(examples: List[lx.data.ExampleData]) -> ExtractionCategory:
    """Create decision points category - NEW for flowcharts!"""
    return ExtractionCategory(
        name="decision_points",
        description="Decision trees and conditional branches",
        attributes=[
            "decision_name",
            "question",
            "condition",
            "options",
            "context",
            "factors_to_consider"
        ],
        prompt_template="""
        Extract decision points and the options available at each point.
        Identify conditions that determine which path to take.
        Include outcomes for each option and factors to consider.
        """,
        examples=examples,
        priority=2,
        passes=2
    )


# Placeholder for other categories
# Will implement as examples are created

# Consolidated from 15 to 11 categories
# Merged: Event Triggers→Deadlines, Communications→Deadlines, Requirements→Principles, Exceptions→Principles
# Deferred: Cases (add later if needed)
ALL_CATEGORIES = [
    "concepts",
    "statutory_references",
    "deadlines",  # Enhanced: includes triggering events, required documents, communication methods
    "document_requirements",  # Separate: forms, reports (important for exam!)
    "role_obligations",
    "principles",  # Enhanced: includes requirements and exceptions as attributes
    "procedures",
    "timeline_sequences",  # For swimlane diagrams
    "decision_points",  # For flowcharts
    "relationships",
    "pitfalls"  # Common mistakes
]

TOTAL_CATEGORIES = len(ALL_CATEGORIES)  # 11 streamlined categories

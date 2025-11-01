"""
Consolidated examples for all 10 core categories.

Categories consolidated from original 15:
- Event Triggers → merged into Deadlines (as triggering_event attribute)
- Communication Requirements → merged into Deadlines (as recipient/method attributes)
- Requirements → merged into Principles (as requirements attribute)
- Exceptions → merged into Principles (as exceptions attribute)
- Cases → deferred (add later if needed)

Final 10 Categories:
1. Concepts
2. Statutory References
3. Deadlines (enhanced)
4. Document Requirements
5. Role Obligations
6. Principles (enhanced)
7. Procedures
8. Timeline Sequences (for swimlanes)
9. Decision Points (for flowcharts)
10. Pitfalls
11. Relationships
"""

from .concepts_examples import concept_examples
from .statutory_examples import statutory_examples
from .deadlines_examples import deadlines_examples
from .role_obligations_examples import role_obligations_examples
from .principles_examples import principles_examples
from .procedures_examples import procedures_examples
from .timeline_examples import timeline_examples
from .decision_points_examples import decision_points_examples
from .pitfalls_examples import pitfalls_examples

# Import document requirements and relationships from remaining_categories
from .remaining_categories_examples import (
    document_requirements_examples,
    relationships_examples
)

# Export all examples grouped by category
ALL_EXAMPLES = {
    "concepts": concept_examples,
    "statutory_references": statutory_examples,
    "deadlines": deadlines_examples,
    "document_requirements": document_requirements_examples,
    "role_obligations": role_obligations_examples,
    "principles": principles_examples,
    "procedures": procedures_examples,
    "timeline_sequences": timeline_examples,
    "decision_points": decision_points_examples,
    "relationships": relationships_examples,
    "pitfalls": pitfalls_examples
}

# Count total
TOTAL_EXAMPLES = sum(len(examples) for examples in ALL_EXAMPLES.values())

print(f"Loaded {TOTAL_EXAMPLES} examples across {len(ALL_EXAMPLES)} categories")

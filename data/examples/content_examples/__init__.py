"""
Atomic minimal examples for insolvency extraction (v2.0).

Schema v2.0: 7 Core Atomic Categories + 1 Relationship Category
- Each category: 3 examples, 2-3 attributes maximum
- Proven approach: concepts_minimal.py yielded 411 extractions with 0 errors

Design Philosophy:
- Minimal examples prevent JSON errors (research-validated)
- Lang Extract generates rich content automatically from simple patterns
- Atomic entities enable database reconstruction of complex scenarios

Categories:
1. Concepts ✅ (Working - 411 extracted)
2. Statutory References (Ready)
3. Deadlines (Ready)
4. Documents (Ready)
5. Actors (Ready)
6. Procedures (Ready)
7. Consequences (Ready)
8. Dependencies (Pass 2 - relationship extraction)
"""

# Import all minimal examples
from .concepts_minimal import concept_minimal_examples as concept_examples  # ✅ WORKING - 411 extractions!
from .statutory_references_minimal import statutory_references_minimal_examples as statutory_examples
from .deadlines_minimal import deadlines_minimal_examples as deadlines_examples
from .documents_minimal import documents_minimal_examples as document_examples
from .actors_minimal import actors_minimal_examples as actor_examples
from .procedures_minimal import procedures_minimal_examples as procedure_examples
from .consequences_minimal import consequences_minimal_examples as consequence_examples

# Export all examples grouped by category
ALL_EXAMPLES = {
    "concepts": concept_examples,
    "statutory_references": statutory_examples,
    "deadlines": deadlines_examples,
    "documents": document_examples,
    "actors": actor_examples,
    "procedures": procedure_examples,
    "consequences": consequence_examples
}

# Count total
TOTAL_EXAMPLES = sum(len(examples) for examples in ALL_EXAMPLES.values())

print(f"Loaded {TOTAL_EXAMPLES} examples across {len(ALL_EXAMPLES)} categories")

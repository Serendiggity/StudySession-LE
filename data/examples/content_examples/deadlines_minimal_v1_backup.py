"""
ULTRA-minimal deadline examples - Version 2.
Reduced to 2 attributes only after JSON errors with 3 attributes.

KEEP IT SIMPLE:
- 3 examples
- 2 attributes ONLY
- No apostrophes or special chars
- Ultra-short values
"""

import langextract as lx


# Example 1: Just timeframe + who
deadline_minimal_1 = lx.data.ExampleData(
    text="Within five days the Trustee notifies creditors.",
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="Within five days",
            attributes={
                "timeframe": "5 days",
                "who": "Trustee"
            }
        )
    ]
)

# Example 2: Just timeframe + action
deadline_minimal_2 = lx.data.ExampleData(
    text="File cash flow within ten days.",
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="within ten days",
            attributes={
                "timeframe": "10 days",
                "action": "File cash flow"
            }
        )
    ]
)

# Example 3: Just timeframe + action
deadline_minimal_3 = lx.data.ExampleData(
    text="Within 30 days file the proposal.",
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="Within 30 days",
            attributes={
                "timeframe": "30 days",
                "action": "File proposal"
            }
        )
    ]
)


# Export
deadlines_minimal_examples = [
    deadline_minimal_1,
    deadline_minimal_2,
    deadline_minimal_3
]

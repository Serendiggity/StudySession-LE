"""
ULTRA-minimal deadline examples - 1 ATTRIBUTE ONLY.
Just extract temporal expressions. Lang Extract will capture full context automatically.
"""

import langextract as lx


# Example 1: "within X days" pattern
deadline_ultra_1 = lx.data.ExampleData(
    text="File within ten days.",
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="within ten days",
            attributes={
                "timeframe": "within 10 days"
            }
        )
    ]
)

# Example 2: "X days before" pattern
deadline_ultra_2 = lx.data.ExampleData(
    text="Must mail notice at least 10 days before the meeting.",
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="at least 10 days before the meeting",
            attributes={
                "timeframe": "10 days before meeting"
            }
        )
    ]
)

# Example 3: "X days after" pattern
deadline_ultra_3 = lx.data.ExampleData(
    text="Apply within 15 days after receiving notice.",
    extractions=[
        lx.data.Extraction(
            extraction_class="deadline",
            extraction_text="within 15 days after receiving notice",
            attributes={
                "timeframe": "15 days after notice"
            }
        )
    ]
)


deadlines_minimal_examples = [
    deadline_ultra_1,
    deadline_ultra_2,
    deadline_ultra_3
]

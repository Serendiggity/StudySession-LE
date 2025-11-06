"""
Schema Suggester - Converts material analysis into extraction schemas.

Takes MaterialAnalyzer output and refines it into a project-ready schema configuration.
Part of Phase 2: AI Material Analyzer implementation.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path


class SchemaSuggester:
    """
    Convert material analysis into extraction schemas.
    Refines AI-suggested categories into project-compatible configurations.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SchemaSuggester.

        Args:
            api_key: Gemini API key (if None, reads from GEMINI_API_KEY env var)
        """
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )

        # Get API key
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Configure Gemini
        self.genai.configure(api_key=self.api_key)
        self.model = self.genai.GenerativeModel('gemini-2.0-flash-exp')

    def suggest_schema(
        self,
        analysis: Dict,
        domain: str,
        project_name: Optional[str] = None
    ) -> Dict:
        """
        Suggest entity schema based on material analysis.

        Args:
            analysis: Output from MaterialAnalyzer.analyze()
            domain: Domain/subject area (e.g., "law", "medicine")
            project_name: Optional project name for context

        Returns:
            {
                "entity_schema": {
                    "categories": [
                        {
                            "name": "condition",
                            "description": "Medical conditions diagnosed",
                            "attributes": ["condition_name", "presentation"],
                            "examples": ["pneumonia", "fracture", "cardiac arrest"],
                            "confidence": 0.87
                        }
                    ],
                    "relationship_types": [
                        {
                            "name": "diagnostic_chain",
                            "description": "Diagnosis workflow",
                            "structure": "condition → imaging → finding → diagnosis",
                            "critical_field": "relationship_text",
                            "examples": ["..."]
                        }
                    ]
                },
                "extraction_recommendations": {
                    "granularity": "sentence",
                    "min_examples_per_category": 2,
                    "use_relationship_text": true
                }
            }
        """
        # Extract relevant parts from analysis
        recommended_categories = analysis.get("recommended_categories", [])
        detected_patterns = analysis.get("detected_patterns", [])
        sample_entities = analysis.get("sample_entities", {})
        domain_indicators = analysis.get("domain_indicators", {})

        # Build schema suggestion prompt
        prompt = self._build_schema_prompt(
            recommended_categories,
            detected_patterns,
            sample_entities,
            domain,
            project_name or "Unknown Project"
        )

        try:
            # Generate schema
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,  # Very low for consistent schema generation
                    "response_mime_type": "application/json"
                }
            )

            # Parse JSON response
            schema = json.loads(response.text)

            # Validate and enhance schema
            schema = self._validate_schema(schema, recommended_categories)

            return schema

        except Exception as e:
            raise RuntimeError(f"Schema suggestion failed: {e}")

    def _build_schema_prompt(
        self,
        categories: List[Dict],
        patterns: List[str],
        samples: Dict[str, List[str]],
        domain: str,
        project_name: str
    ) -> str:
        """Build the schema suggestion prompt for Gemini."""

        categories_json = json.dumps(categories, indent=2)
        patterns_json = json.dumps(patterns, indent=2)
        samples_json = json.dumps(samples, indent=2)

        return f"""You are designing an extraction schema for a knowledge base project.

PROJECT INFO:
- Name: {project_name}
- Domain: {domain}

ANALYSIS INPUT:
Recommended Categories:
{categories_json}

Detected Patterns:
{patterns_json}

Sample Entities:
{samples_json}

TASK:
Create a refined extraction schema that will be used with Lang Extract API and stored in a SQLite database.

CRITICAL CONSTRAINTS:
1. **Minimal Attributes**: Each category should have ONLY 1-2 attributes
   - More attributes = exponentially higher error rates
   - Research shows: text_size × attributes = complexity = errors
   - For large documents, 1-2 attributes per category is OPTIMAL

2. **Relationship Text Field**: ALL relationship types MUST include:
   - "critical_field": "relationship_text"
   - This field preserves the original quote from the source material
   - This enables zero-hallucination answers

3. **Sentence-Level Granularity**: Default to sentence-level extraction
   - Proven optimal (95% completeness, excellent quote quality)

OUTPUT JSON STRUCTURE:
{{
  "entity_schema": {{
    "categories": [
      {{
        "name": "category_name",
        "description": "What this category represents",
        "attributes": ["attribute1", "attribute2"],  // MAX 2 attributes!
        "examples": ["example1", "example2", "example3"],
        "confidence": 0.87,
        "rationale": "Why this category is needed"
      }}
    ],
    "relationship_types": [
      {{
        "name": "relationship_name",
        "description": "What this relationship captures",
        "structure": "entity1 → entity2 → entity3",
        "critical_field": "relationship_text",  // MANDATORY
        "examples": ["Exact quote from source showing this pattern"]
      }}
    ]
  }},
  "extraction_recommendations": {{
    "granularity": "sentence",
    "min_examples_per_category": 2,
    "use_relationship_text": true,
    "rationale": "Why these recommendations"
  }}
}}

ATTRIBUTE NAMING GUIDELINES:
- Use clear, descriptive names
- For canonical/normalized values: add "_canonical" suffix
- For original extraction text: use "extraction_text"
- For references: use "reference_text" or "section_ref"
- Keep names consistent with domain conventions

RELATIONSHIP TYPE GUIDELINES:
- Name should describe the relationship (e.g., "duty_relationships", "diagnostic_chain")
- Structure should show entity flow with → arrows
- ALWAYS include "critical_field": "relationship_text"
- Provide 1-2 actual examples from the sample entities

Return ONLY valid JSON matching this structure."""

    def _validate_schema(self, schema: Dict, original_categories: List[Dict]) -> Dict:
        """Validate and enhance the schema."""

        # Ensure top-level keys
        if "entity_schema" not in schema:
            schema["entity_schema"] = {
                "categories": [],
                "relationship_types": []
            }

        if "extraction_recommendations" not in schema:
            schema["extraction_recommendations"] = {
                "granularity": "sentence",
                "min_examples_per_category": 2,
                "use_relationship_text": True
            }

        # Validate categories
        categories = schema["entity_schema"].get("categories", [])

        for cat in categories:
            # Ensure attributes list exists
            if "attributes" not in cat:
                cat["attributes"] = ["extraction_text"]

            # Warn if too many attributes
            if len(cat["attributes"]) > 2:
                print(f"Warning: Category '{cat['name']}' has {len(cat['attributes'])} attributes. "
                      f"Recommended: 1-2 attributes for optimal accuracy.")

            # Ensure examples exist
            if "examples" not in cat or not cat["examples"]:
                cat["examples"] = []

        # Validate relationship types
        relationship_types = schema["entity_schema"].get("relationship_types", [])

        for rel in relationship_types:
            # Ensure critical_field is set
            if "critical_field" not in rel:
                rel["critical_field"] = "relationship_text"
                print(f"Added critical_field to relationship '{rel.get('name', 'unknown')}'")

            # Ensure examples exist
            if "examples" not in rel:
                rel["examples"] = []

        # Check category count (should be 4-7)
        if len(categories) < 4:
            print(f"Warning: Only {len(categories)} categories (recommended: 4-7)")
        elif len(categories) > 7:
            print(f"Warning: {len(categories)} categories (recommended: 4-7)")

        return schema

    def refine_with_user_examples(
        self,
        schema: Dict,
        user_examples: Dict[str, List[str]]
    ) -> Dict:
        """
        Refine schema using user-selected examples from actual material.

        This is more accurate than AI-generated examples.

        Args:
            schema: Schema from suggest_schema()
            user_examples: Dict of category -> list of user-highlighted examples

        Returns:
            Refined schema with user examples
        """
        categories = schema["entity_schema"]["categories"]

        for cat in categories:
            cat_name = cat["name"]
            if cat_name in user_examples:
                # Replace AI examples with user examples
                cat["examples"] = user_examples[cat_name]
                cat["user_validated"] = True

        return schema

    def generate_project_config(
        self,
        schema: Dict,
        project_name: str,
        domain: str,
        description: str = ""
    ) -> Dict:
        """
        Generate a complete project config.json from schema.

        Args:
            schema: Schema from suggest_schema()
            project_name: Project name
            domain: Domain/subject area
            description: Project description

        Returns:
            Complete config.json structure
        """
        from datetime import datetime

        project_id = project_name.lower().replace(" ", "-")

        config = {
            "project_name": project_name,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "description": description,
            "domain": domain,
            "entity_schema": schema.get("entity_schema", {}),
            "sources": [],
            "database_path": "database/knowledge.db",
            "agent_config": {
                "search_phases": ["database", "full_text"],
                "auto_follow_references": True,
                "logging_enabled": True
            },
            "statistics": {
                "total_entities": 0,
                "total_relationships": 0,
                "total_questions_answered": 0,
                "average_query_time_ms": 0
            },
            "extraction_config": schema.get("extraction_recommendations", {})
        }

        return config

    def save_schema(self, schema: Dict, output_path: Path):
        """
        Save schema to JSON file.

        Args:
            schema: Schema dictionary
            output_path: Path to save JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2)

        print(f"Schema saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    # This would normally be called after MaterialAnalyzer
    suggester = SchemaSuggester()

    # Example analysis input (from MaterialAnalyzer)
    example_analysis = {
        "recommended_categories": [
            {
                "name": "actors",
                "description": "People or roles performing actions",
                "confidence": 0.85,
                "rationale": "Document frequently mentions specific roles"
            },
            {
                "name": "procedures",
                "description": "Actions to be performed",
                "confidence": 0.92,
                "rationale": "Many procedural requirements"
            }
        ],
        "detected_patterns": [
            "actor-action-deadline-consequence"
        ],
        "sample_entities": {
            "actors": ["trustee", "debtor", "official receiver"],
            "procedures": ["file proposal", "call meeting", "prepare statement"]
        }
    }

    print("Generating schema from analysis...")
    schema = suggester.suggest_schema(
        example_analysis,
        domain="law",
        project_name="Example Law Project"
    )

    print("\nGenerated Schema:")
    print(json.dumps(schema, indent=2))

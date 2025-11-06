"""
Common Ground Finder - Cross-domain schema mapping.

Finds conceptual similarities between schemas from different domains.
Enables unified knowledge graphs and cross-domain querying.
Part of Phase 2: AI Material Analyzer implementation.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class CommonGroundFinder:
    """
    Find conceptual mappings between schemas from different domains.

    Example mappings:
    - Law "procedures" ≈ Medicine "treatments" (both are professional actions)
    - Law "deadlines" ≈ Medicine "dosing_schedules" (both are timing requirements)
    - Engineering "components" ≈ Law "documents" (both are concrete artifacts)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CommonGroundFinder.

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

    def find_mappings(
        self,
        new_schema: Dict,
        existing_schemas: List[Dict],
        new_project_name: str,
        new_domain: str
    ) -> Dict:
        """
        Find conceptual mappings between new schema and existing projects.

        Args:
            new_schema: Schema for new project (from SchemaSuggester)
            existing_schemas: List of schemas from existing projects
            new_project_name: Name of new project
            new_domain: Domain of new project

        Returns:
            {
                "mappings": [
                    {
                        "new_category": "imaging_methods",
                        "maps_to": {
                            "project": "insolvency-law",
                            "category": "procedures",
                            "confidence": 0.75,
                            "rationale": "Both represent professional actions"
                        }
                    }
                ],
                "unified_categories": [
                    {
                        "name": "actions",
                        "subsumes": ["procedures", "treatments", "imaging_methods"],
                        "description": "Actions performed by professionals"
                    }
                ],
                "recommendations": [
                    "Consider creating unified 'actions' table for cross-domain queries",
                    "Map relationship structures to common patterns"
                ]
            }
        """
        # Extract categories from new schema
        new_categories = new_schema.get("entity_schema", {}).get("categories", [])

        # Extract categories from existing schemas
        existing_categories_by_project = {}
        for schema in existing_schemas:
            project_id = schema.get("project_id", "unknown")
            project_domain = schema.get("domain", "unknown")
            categories = schema.get("entity_schema", {}).get("categories", [])

            existing_categories_by_project[project_id] = {
                "domain": project_domain,
                "categories": categories
            }

        # Build mapping prompt
        prompt = self._build_mapping_prompt(
            new_categories,
            existing_categories_by_project,
            new_project_name,
            new_domain
        )

        try:
            # Generate mappings
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )

            # Parse JSON response
            mappings = json.loads(response.text)

            # Validate mappings
            mappings = self._validate_mappings(mappings)

            return mappings

        except Exception as e:
            raise RuntimeError(f"Mapping generation failed: {e}")

    def _build_mapping_prompt(
        self,
        new_categories: List[Dict],
        existing_by_project: Dict[str, Dict],
        new_project_name: str,
        new_domain: str
    ) -> str:
        """Build the mapping prompt for Gemini."""

        new_cats_json = json.dumps(new_categories, indent=2)
        existing_json = json.dumps(existing_by_project, indent=2)

        return f"""You are mapping schemas from different knowledge domains to find common ground.

NEW PROJECT:
- Name: {new_project_name}
- Domain: {new_domain}
- Categories:
{new_cats_json}

EXISTING PROJECTS:
{existing_json}

TASK:
Find conceptual mappings between the new project's categories and existing projects' categories.

MAPPING CRITERIA:
1. **Functional Similarity**: Do they serve similar purposes?
   - "procedures" (law) ≈ "treatments" (medicine) - both are actions performed
   - "deadlines" (law) ≈ "dosing_schedules" (medicine) - both are timing requirements

2. **Structural Similarity**: Do they have similar attributes?
   - "actors" (law) ≈ "healthcare_providers" (medicine) - both are people/roles
   - "documents" (law) ≈ "test_results" (medicine) - both are artifacts/records

3. **Relationship Patterns**: Do they appear in similar relationship chains?
   - "actor → action → deadline" (law)
   - "provider → treatment → schedule" (medicine)

OUTPUT JSON STRUCTURE:
{{
  "mappings": [
    {{
      "new_category": "category_name",
      "maps_to": {{
        "project": "project-id",
        "category": "existing_category",
        "confidence": 0.75,
        "rationale": "Brief explanation of why they map",
        "functional_similarity": true,
        "structural_similarity": false,
        "relationship_similarity": true
      }}
    }}
  ],
  "unified_categories": [
    {{
      "name": "unified_name",
      "description": "What this unified category represents",
      "subsumes": ["cat1", "cat2", "cat3"],
      "projects": ["project-1", "project-2"],
      "rationale": "Why these categories can be unified"
    }}
  ],
  "recommendations": [
    "Recommendation 1: Specific actionable suggestion",
    "Recommendation 2: Another suggestion"
  ],
  "cross_domain_queries": [
    {{
      "description": "Query all professional actions across law and medicine",
      "unified_category": "actions",
      "example_query": "SELECT * FROM actions WHERE domain IN ('law', 'medicine')"
    }}
  ]
}}

IMPORTANT CONSTRAINTS:
- Only suggest mappings with confidence >= 0.6
- Unified categories should include 2+ categories from different domains
- Recommendations should be specific and actionable
- Cross-domain queries should be realistic and useful

Return ONLY valid JSON matching this structure."""

    def _validate_mappings(self, mappings: Dict) -> Dict:
        """Validate and enhance the mappings."""

        # Ensure required keys
        if "mappings" not in mappings:
            mappings["mappings"] = []

        if "unified_categories" not in mappings:
            mappings["unified_categories"] = []

        if "recommendations" not in mappings:
            mappings["recommendations"] = []

        if "cross_domain_queries" not in mappings:
            mappings["cross_domain_queries"] = []

        # Filter low-confidence mappings
        filtered_mappings = []
        for mapping in mappings["mappings"]:
            confidence = mapping.get("maps_to", {}).get("confidence", 0.0)
            if confidence >= 0.6:
                filtered_mappings.append(mapping)
            else:
                print(f"Warning: Filtered out low-confidence mapping "
                      f"({mapping.get('new_category')} → confidence {confidence})")

        mappings["mappings"] = filtered_mappings

        return mappings

    def suggest_unified_schema(
        self,
        mappings: Dict,
        project_schemas: List[Dict]
    ) -> Dict:
        """
        Suggest a unified schema that spans multiple domains.

        Args:
            mappings: Output from find_mappings()
            project_schemas: List of project schemas

        Returns:
            Unified schema structure
        """
        unified_categories = mappings.get("unified_categories", [])

        # Build unified schema
        unified_schema = {
            "schema_type": "unified_multi_domain",
            "categories": [],
            "cross_domain_relationships": []
        }

        for unified_cat in unified_categories:
            category = {
                "name": unified_cat["name"],
                "description": unified_cat["description"],
                "source_categories": unified_cat["subsumes"],
                "source_projects": unified_cat["projects"],
                "attributes": self._merge_attributes(
                    unified_cat["subsumes"],
                    project_schemas
                )
            }
            unified_schema["categories"].append(category)

        return unified_schema

    def _merge_attributes(
        self,
        category_names: List[str],
        project_schemas: List[Dict]
    ) -> List[str]:
        """Merge attributes from multiple categories."""
        all_attributes = set()

        for schema in project_schemas:
            categories = schema.get("entity_schema", {}).get("categories", [])
            for cat in categories:
                if cat["name"] in category_names:
                    attributes = cat.get("attributes", [])
                    all_attributes.update(attributes)

        # Add unified attributes
        all_attributes.add("domain")  # To track which domain
        all_attributes.add("original_category")  # To track original category

        return sorted(list(all_attributes))

    def visualize_mappings(self, mappings: Dict) -> str:
        """
        Generate a text visualization of mappings.

        Args:
            mappings: Output from find_mappings()

        Returns:
            Text visualization
        """
        lines = []
        lines.append("="*70)
        lines.append("CROSS-DOMAIN MAPPINGS")
        lines.append("="*70)

        # Show individual mappings
        lines.append("\nCategory Mappings:")
        for mapping in mappings.get("mappings", []):
            new_cat = mapping["new_category"]
            maps_to = mapping["maps_to"]
            project = maps_to["project"]
            old_cat = maps_to["category"]
            confidence = maps_to["confidence"]
            rationale = maps_to["rationale"]

            lines.append(f"\n  {new_cat} → {old_cat} (in {project})")
            lines.append(f"    Confidence: {confidence:.2f}")
            lines.append(f"    Rationale: {rationale}")

        # Show unified categories
        lines.append("\n\nUnified Categories:")
        for unified in mappings.get("unified_categories", []):
            name = unified["name"]
            subsumes = ", ".join(unified["subsumes"])
            desc = unified["description"]

            lines.append(f"\n  {name}")
            lines.append(f"    Subsumes: {subsumes}")
            lines.append(f"    Description: {desc}")

        # Show recommendations
        lines.append("\n\nRecommendations:")
        for idx, rec in enumerate(mappings.get("recommendations", []), 1):
            lines.append(f"  {idx}. {rec}")

        lines.append("\n" + "="*70)

        return "\n".join(lines)

    def save_mappings(self, mappings: Dict, output_path: Path):
        """
        Save mappings to JSON file.

        Args:
            mappings: Mappings dictionary
            output_path: Path to save JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(mappings, f, indent=2)

        print(f"Mappings saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    finder = CommonGroundFinder()

    # Example new schema (radiology)
    new_schema = {
        "entity_schema": {
            "categories": [
                {
                    "name": "imaging_methods",
                    "description": "Diagnostic imaging procedures",
                    "attributes": ["method_name", "body_part"]
                },
                {
                    "name": "findings",
                    "description": "Observed abnormalities or conditions",
                    "attributes": ["finding_text", "severity"]
                }
            ]
        }
    }

    # Example existing schema (insolvency law)
    existing_schemas = [
        {
            "project_id": "insolvency-law",
            "domain": "law",
            "entity_schema": {
                "categories": [
                    {
                        "name": "procedures",
                        "description": "Actions to be performed",
                        "attributes": ["step_name", "action"]
                    },
                    {
                        "name": "consequences",
                        "description": "Outcomes of actions",
                        "attributes": ["outcome", "severity"]
                    }
                ]
            }
        }
    ]

    print("Finding common ground between domains...")
    mappings = finder.find_mappings(
        new_schema,
        existing_schemas,
        "Radiology Knowledge Base",
        "medicine"
    )

    print("\nMappings:")
    print(finder.visualize_mappings(mappings))

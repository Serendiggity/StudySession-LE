"""
Lang Extract Client - Interface to Lang Extract API.

Handles communication with Lang Extract API for entity and relationship extraction.
Part of Phase 3: Extraction Pipeline implementation.
"""

import os
import json
import requests
from typing import Dict, List, Optional
from pathlib import Path


class LangExtractClient:
    """
    Client for Lang Extract API.

    Handles:
    - Entity extraction with minimal examples
    - Relationship extraction
    - API authentication
    - Error handling and retries
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LangExtractClient.

        Args:
            api_key: Lang Extract API key (if None, reads from LANG_EXTRACT_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("LANG_EXTRACT_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Lang Extract API key required. Set LANG_EXTRACT_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.base_url = "https://api.langextract.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def extract_entities(
        self,
        text: str,
        category: str,
        attributes: List[str],
        examples: List[Dict[str, str]],
        granularity: str = "sentence"
    ) -> List[Dict]:
        """
        Extract entities of a specific category from text.

        Args:
            text: Source text to extract from
            category: Entity category (e.g., "actors", "procedures")
            attributes: List of attributes to extract (keep to 1-2 for accuracy)
            examples: List of example entities with attribute values
            granularity: "sentence" (recommended) or "paragraph"

        Returns:
            List of extracted entities with attributes

        Example:
            entities = client.extract_entities(
                text="The trustee shall file within 10 days.",
                category="actors",
                attributes=["role_canonical"],
                examples=[
                    {"role_canonical": "trustee"},
                    {"role_canonical": "debtor"}
                ],
                granularity="sentence"
            )
            # Returns: [{"role_canonical": "trustee", "extraction_text": "..."}]
        """
        endpoint = f"{self.base_url}/extract/entities"

        payload = {
            "text": text,
            "category": category,
            "attributes": attributes,
            "examples": examples,
            "granularity": granularity,
            "include_context": True  # Include surrounding text
        }

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            return result.get("entities", [])

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Entity extraction failed: {e}")

    def extract_relationships(
        self,
        text: str,
        relationship_type: str,
        structure: str,
        examples: List[str],
        entity_categories: List[str]
    ) -> List[Dict]:
        """
        Extract relationships from text.

        Args:
            text: Source text to extract from
            relationship_type: Type of relationship (e.g., "duty_relationships")
            structure: Relationship structure (e.g., "actor → procedure → deadline")
            examples: List of example relationship patterns from text
            entity_categories: List of entity categories involved

        Returns:
            List of extracted relationships

        Example:
            relationships = client.extract_relationships(
                text="The trustee shall file within 10 days.",
                relationship_type="duty_relationships",
                structure="actor → procedure → deadline",
                examples=["The trustee shall file within 10 days"],
                entity_categories=["actors", "procedures", "deadlines"]
            )
        """
        endpoint = f"{self.base_url}/extract/relationships"

        payload = {
            "text": text,
            "relationship_type": relationship_type,
            "structure": structure,
            "examples": examples,
            "entity_categories": entity_categories,
            "preserve_quotes": True  # Critical for relationship_text field
        }

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            return result.get("relationships", [])

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Relationship extraction failed: {e}")

    def extract_batch(
        self,
        text: str,
        schema: Dict,
        examples_per_category: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """
        Extract all categories and relationships in batch.

        More efficient than individual calls.

        Args:
            text: Source text to extract from
            schema: Entity schema from SchemaSuggester
            examples_per_category: Dict mapping category -> examples

        Returns:
            {
                "entities": {
                    "actors": [...],
                    "procedures": [...]
                },
                "relationships": [...]
            }
        """
        endpoint = f"{self.base_url}/extract/batch"

        # Build entity extraction specs
        entity_specs = []
        categories = schema.get("entity_schema", {}).get("categories", [])

        for cat in categories:
            cat_name = cat["name"]
            attributes = cat["attributes"]
            examples = examples_per_category.get(cat_name, [])

            entity_specs.append({
                "category": cat_name,
                "attributes": attributes,
                "examples": examples
            })

        # Build relationship extraction specs
        relationship_specs = []
        rel_types = schema.get("entity_schema", {}).get("relationship_types", [])

        for rel in rel_types:
            relationship_specs.append({
                "relationship_type": rel["name"],
                "structure": rel["structure"],
                "examples": rel.get("examples", []),
                "entity_categories": [cat["name"] for cat in categories]
            })

        payload = {
            "text": text,
            "entity_specs": entity_specs,
            "relationship_specs": relationship_specs,
            "granularity": "sentence"
        }

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=120  # Longer timeout for batch
            )

            response.raise_for_status()
            result = response.json()

            return result

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Batch extraction failed: {e}")

    def check_quota(self) -> Dict:
        """
        Check API usage quota.

        Returns:
            {
                "remaining_calls": 1000,
                "quota_limit": 10000,
                "reset_date": "2025-02-01"
            }
        """
        endpoint = f"{self.base_url}/quota"

        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=10
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Quota check failed: {e}")


# Mock implementation for testing (when API not available)
class MockLangExtractClient(LangExtractClient):
    """
    Mock client for testing without actual API calls.

    Returns simulated extraction results.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize mock client (no API key required)."""
        self.api_key = api_key or "mock_key"
        self.base_url = "http://mock.langextract.com/v1"

    def extract_entities(
        self,
        text: str,
        category: str,
        attributes: List[str],
        examples: List[Dict[str, str]],
        granularity: str = "sentence"
    ) -> List[Dict]:
        """Return mock entities."""
        print(f"[MOCK] Extracting {category} from {len(text)} chars...")

        # Simple mock: return examples as extracted entities
        mock_results = []
        for example in examples[:3]:  # Return first 3 examples
            entity = example.copy()
            entity["extraction_text"] = f"Mock extraction for {category}"
            entity["confidence"] = 0.85
            mock_results.append(entity)

        return mock_results

    def extract_relationships(
        self,
        text: str,
        relationship_type: str,
        structure: str,
        examples: List[str],
        entity_categories: List[str]
    ) -> List[Dict]:
        """Return mock relationships."""
        print(f"[MOCK] Extracting {relationship_type} from {len(text)} chars...")

        # Return mock relationship
        return [
            {
                "relationship_type": relationship_type,
                "entities": {cat: f"mock_{cat}" for cat in entity_categories},
                "relationship_text": examples[0] if examples else "Mock relationship text",
                "confidence": 0.80
            }
        ]

    def extract_batch(
        self,
        text: str,
        schema: Dict,
        examples_per_category: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """Return mock batch extraction."""
        print(f"[MOCK] Batch extracting from {len(text)} chars...")

        categories = schema.get("entity_schema", {}).get("categories", [])

        # Mock entities
        entities = {}
        for cat in categories:
            cat_name = cat["name"]
            examples = examples_per_category.get(cat_name, [])
            entities[cat_name] = self.extract_entities(
                text, cat_name, cat["attributes"], examples
            )

        # Mock relationships
        relationships = self.extract_relationships(
            text,
            "mock_relationship",
            "entity1 → entity2",
            ["Mock example"],
            [cat["name"] for cat in categories]
        )

        return {
            "entities": entities,
            "relationships": relationships
        }

    def check_quota(self) -> Dict:
        """Return mock quota."""
        return {
            "remaining_calls": 9999,
            "quota_limit": 10000,
            "reset_date": "2025-02-01"
        }


# Example usage
if __name__ == "__main__":
    # Use mock client for testing
    client = MockLangExtractClient()

    # Test entity extraction
    text = "The trustee shall file a proposal within 10 days."

    entities = client.extract_entities(
        text=text,
        category="actors",
        attributes=["role_canonical"],
        examples=[
            {"role_canonical": "trustee"},
            {"role_canonical": "debtor"}
        ]
    )

    print(f"\nExtracted entities:")
    print(json.dumps(entities, indent=2))

    # Check quota
    quota = client.check_quota()
    print(f"\nQuota: {quota}")

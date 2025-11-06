"""
Material Analyzer - AI-powered document structure analysis.

Uses Gemini 2.0 Flash to analyze unknown materials and detect patterns.
Part of Phase 2: AI Material Analyzer implementation.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path


class MaterialAnalyzer:
    """
    Analyze unknown materials to detect structure and patterns.
    Uses Gemini 2.0 Flash to understand document characteristics.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize MaterialAnalyzer.

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

    def analyze(
        self,
        content: str,
        content_type: str = "text",
        sample_size: int = 2000
    ) -> Dict:
        """
        Analyze material and detect patterns.

        Args:
            content: Text content (from PDF, URL, etc.)
            content_type: "pdf", "url", "text", "markdown", etc.
            sample_size: Number of words to sample for analysis

        Returns:
            {
                "document_structure": {
                    "has_sections": bool,
                    "has_numbered_items": bool,
                    "has_definitions": bool,
                    "hierarchical": bool,
                    "section_pattern": str
                },
                "detected_patterns": [
                    "actor-action-deadline",
                    "condition-diagnosis",
                    "component-interface"
                ],
                "recommended_categories": [
                    {
                        "name": "actors",
                        "description": "People or roles performing actions",
                        "confidence": 0.85,
                        "rationale": "Document frequently mentions roles..."
                    }
                ],
                "sample_entities": {
                    "actors": ["trustee", "debtor", "official receiver"],
                    "procedures": ["file proposal", "call meeting"]
                },
                "domain_indicators": {
                    "primary_domain": "law",
                    "confidence": 0.92,
                    "secondary_domains": ["business", "finance"]
                }
            }
        """
        # Sample content for analysis (first N words)
        words = content.split()
        sample_words = words[:sample_size]
        sample = " ".join(sample_words)

        # Build analysis prompt
        prompt = self._build_analysis_prompt(sample, content_type, len(words))

        try:
            # Generate analysis
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,  # Lower temperature for more consistent analysis
                    "response_mime_type": "application/json"
                }
            )

            # Parse JSON response
            analysis = json.loads(response.text)

            # Validate and enhance analysis
            analysis = self._validate_analysis(analysis)

            return analysis

        except Exception as e:
            raise RuntimeError(f"Analysis failed: {e}")

    def _build_analysis_prompt(
        self,
        sample: str,
        content_type: str,
        total_words: int
    ) -> str:
        """Build the analysis prompt for Gemini."""

        return f"""You are analyzing a document to understand its structure and suggest an optimal extraction schema.

DOCUMENT INFO:
- Content Type: {content_type}
- Total Words: {total_words:,}
- Sample Size: {len(sample.split())} words (shown below)

DOCUMENT SAMPLE:
{sample}

ANALYSIS TASK:
Analyze this document and provide a structured JSON response with the following:

1. **document_structure**: Structural characteristics
   - has_sections: Does it have clear section headings?
   - has_numbered_items: Are there numbered lists or items?
   - has_definitions: Are there explicit definitions?
   - hierarchical: Is there a clear hierarchy (chapters, sections, subsections)?
   - section_pattern: Describe the pattern (e.g., "numeric sections", "alphabetic divisions")

2. **detected_patterns**: Relationship patterns found in the content
   - Examples: "actor-action-consequence", "condition-diagnosis-treatment", "component-interface-operation"
   - List 2-5 patterns that appear repeatedly

3. **recommended_categories**: Suggested entity types for extraction (4-7 categories)
   For each category provide:
   - name: Short identifier (lowercase, underscores)
   - description: What this category represents
   - confidence: Score 0.0-1.0 indicating how confident you are
   - rationale: Brief explanation of why this category was identified
   - suggested_attributes: 1-2 key attributes to extract (keep minimal)

4. **sample_entities**: Example instances for each recommended category
   - Provide 3-5 actual examples extracted from the sample
   - Use exact text from the document when possible

5. **domain_indicators**: Domain classification
   - primary_domain: Main subject area (law, medicine, engineering, business, etc.)
   - confidence: Score 0.0-1.0
   - secondary_domains: Related domains (if applicable)

IMPORTANT CONSTRAINTS:
- Recommend 4-7 entity categories (not more, not less)
- Keep attributes minimal (1-2 per category) - complexity = errors
- Use exact text from document for examples
- Focus on recurring patterns, not one-off mentions
- Be specific about relationship patterns

Return ONLY valid JSON matching this structure."""

    def _validate_analysis(self, analysis: Dict) -> Dict:
        """Validate and enhance the analysis results."""

        # Ensure required top-level keys exist
        required_keys = [
            "document_structure",
            "detected_patterns",
            "recommended_categories",
            "sample_entities",
            "domain_indicators"
        ]

        for key in required_keys:
            if key not in analysis:
                analysis[key] = self._get_default_for_key(key)

        # Validate recommended_categories count (should be 4-7)
        categories = analysis.get("recommended_categories", [])
        if len(categories) < 4:
            print(f"Warning: Only {len(categories)} categories suggested (expected 4-7)")
        elif len(categories) > 7:
            # Keep top 7 by confidence
            categories = sorted(
                categories,
                key=lambda c: c.get("confidence", 0),
                reverse=True
            )[:7]
            analysis["recommended_categories"] = categories
            print(f"Limited to top 7 categories by confidence")

        return analysis

    def _get_default_for_key(self, key: str) -> any:
        """Get default value for missing key."""
        defaults = {
            "document_structure": {
                "has_sections": False,
                "has_numbered_items": False,
                "has_definitions": False,
                "hierarchical": False,
                "section_pattern": "unknown"
            },
            "detected_patterns": [],
            "recommended_categories": [],
            "sample_entities": {},
            "domain_indicators": {
                "primary_domain": "unknown",
                "confidence": 0.0,
                "secondary_domains": []
            }
        }
        return defaults.get(key, {})

    def analyze_structure(self, content: str) -> Dict:
        """
        Lightweight analysis focusing only on document structure.

        Args:
            content: Text content

        Returns:
            Structure analysis only
        """
        full_analysis = self.analyze(content)
        return full_analysis.get("document_structure", {})

    def detect_patterns(self, content: str) -> List[str]:
        """
        Lightweight analysis focusing only on relationship patterns.

        Args:
            content: Text content

        Returns:
            List of detected patterns
        """
        full_analysis = self.analyze(content)
        return full_analysis.get("detected_patterns", [])

    def sample_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Lightweight analysis focusing only on entity sampling.

        Args:
            content: Text content

        Returns:
            Dictionary of category -> example entities
        """
        full_analysis = self.analyze(content)
        return full_analysis.get("sample_entities", {})

    def save_analysis(self, analysis: Dict, output_path: Path):
        """
        Save analysis results to JSON file.

        Args:
            analysis: Analysis results dictionary
            output_path: Path to save JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"Analysis saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    # This would normally be called by the CLI or project manager
    analyzer = MaterialAnalyzer()

    # Example: Analyze a sample text
    sample_text = """
    Section 50.4 - Duties of Insolvent Person

    (1) The insolvent person shall, within ten days after filing a notice of intention,
        (a) prepare a statement of affairs;
        (b) provide the trustee with information regarding creditors;
        (c) attend the first meeting of creditors.

    (2) If the insolvent person fails to comply with subsection (1), the trustee
    shall notify the official receiver.
    """

    print("Analyzing sample text...")
    result = analyzer.analyze(sample_text)

    print("\nAnalysis Results:")
    print(json.dumps(result, indent=2))

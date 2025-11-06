"""
Example Selector - User-guided example selection from actual material.

Allows users to review AI suggestions and select better examples from the document.
More accurate than AI-generated examples.
Part of Phase 2: AI Material Analyzer implementation.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


class ExampleSelector:
    """
    Interactive interface for user to select examples from material.
    User-selected examples are more accurate than AI-generated ones.
    """

    def __init__(self):
        """Initialize ExampleSelector."""
        pass

    def review_and_refine(
        self,
        categories: List[Dict],
        document_text: str,
        interactive: bool = True
    ) -> Dict[str, List[str]]:
        """
        Review AI-suggested categories and select better examples.

        Args:
            categories: List of category dicts from MaterialAnalyzer/SchemaSuggester
            document_text: Full text of the document
            interactive: If True, prompt user interactively; if False, just return AI examples

        Returns:
            Dict mapping category name -> list of user-selected examples
            {
                "actors": ["trustee", "debtor", "official receiver"],
                "procedures": ["file proposal", "prepare statement"]
            }
        """
        if not interactive:
            # Non-interactive mode: just extract AI examples
            return self._extract_ai_examples(categories)

        # Interactive mode: prompt user for better examples
        print("\n" + "="*70)
        print("EXAMPLE SELECTION - Review and refine AI suggestions")
        print("="*70)
        print("\nThe AI has suggested categories and examples.")
        print("You can review and select better examples from your actual material.\n")

        user_examples = {}

        for idx, category in enumerate(categories, 1):
            cat_name = category.get("name", "unknown")
            cat_desc = category.get("description", "")
            ai_examples = category.get("examples", [])
            confidence = category.get("confidence", 0.0)

            print(f"\n{'─'*70}")
            print(f"Category {idx}/{len(categories)}: {cat_name}")
            print(f"Description: {cat_desc}")
            print(f"Confidence: {confidence:.2f}")
            print(f"\nAI-suggested examples:")
            for ex in ai_examples:
                print(f"  • {ex}")

            # Ask user if they want to refine
            print(f"\nOptions:")
            print(f"  [k] Keep AI examples")
            print(f"  [s] Search document and select your own examples")
            print(f"  [e] Enter examples manually")

            choice = input(f"\nYour choice for '{cat_name}' [k/s/e]: ").lower().strip()

            if choice == 'k':
                # Keep AI examples
                user_examples[cat_name] = ai_examples
                print(f"✓ Kept AI examples for '{cat_name}'")

            elif choice == 's':
                # Search document and select
                selected = self._search_and_select(
                    cat_name,
                    cat_desc,
                    document_text,
                    ai_examples
                )
                user_examples[cat_name] = selected
                print(f"✓ Selected {len(selected)} examples for '{cat_name}'")

            elif choice == 'e':
                # Enter manually
                entered = self._enter_manually(cat_name, ai_examples)
                user_examples[cat_name] = entered
                print(f"✓ Entered {len(entered)} examples for '{cat_name}'")

            else:
                # Default: keep AI examples
                user_examples[cat_name] = ai_examples
                print(f"✓ Kept AI examples for '{cat_name}' (default)")

        print(f"\n{'='*70}")
        print(f"Example selection complete!")
        print(f"{'='*70}\n")

        return user_examples

    def _extract_ai_examples(self, categories: List[Dict]) -> Dict[str, List[str]]:
        """Extract AI examples from categories (non-interactive)."""
        examples = {}
        for category in categories:
            cat_name = category.get("name", "unknown")
            cat_examples = category.get("examples", [])
            examples[cat_name] = cat_examples
        return examples

    def _search_and_select(
        self,
        category_name: str,
        category_desc: str,
        document_text: str,
        ai_examples: List[str]
    ) -> List[str]:
        """
        Search document and select examples interactively.

        Args:
            category_name: Name of category
            category_desc: Description of category
            document_text: Full document text
            ai_examples: AI-suggested examples

        Returns:
            List of user-selected examples
        """
        print(f"\n{'─'*70}")
        print(f"SEARCH MODE: Finding examples for '{category_name}'")
        print(f"{'─'*70}")

        selected_examples = []

        while True:
            print(f"\nCurrent examples: {len(selected_examples)}")
            if selected_examples:
                for idx, ex in enumerate(selected_examples, 1):
                    print(f"  {idx}. {ex}")

            print(f"\nOptions:")
            print(f"  [s <keyword>] - Search document for keyword")
            print(f"  [a <text>]    - Add example directly")
            print(f"  [r <number>]  - Remove example by number")
            print(f"  [d]           - Done selecting")

            cmd = input(f"\nCommand: ").strip()

            if cmd.lower() == 'd':
                # Done
                if len(selected_examples) == 0:
                    print(f"Warning: No examples selected. Keeping AI examples.")
                    return ai_examples
                break

            elif cmd.lower().startswith('s '):
                # Search for keyword
                keyword = cmd[2:].strip()
                matches = self._find_matches(document_text, keyword)

                if not matches:
                    print(f"No matches found for '{keyword}'")
                    continue

                print(f"\nFound {len(matches)} matches:")
                for idx, match in enumerate(matches[:10], 1):  # Show first 10
                    print(f"  {idx}. {match}")

                if len(matches) > 10:
                    print(f"  ... and {len(matches) - 10} more")

                which = input(f"\nSelect match numbers (comma-separated) or 'n' to skip: ").strip()

                if which.lower() != 'n':
                    try:
                        indices = [int(x.strip()) - 1 for x in which.split(',')]
                        for idx in indices:
                            if 0 <= idx < len(matches):
                                example = matches[idx]
                                if example not in selected_examples:
                                    selected_examples.append(example)
                                    print(f"✓ Added: {example}")
                    except ValueError:
                        print("Invalid input. Use comma-separated numbers.")

            elif cmd.lower().startswith('a '):
                # Add directly
                text = cmd[2:].strip()
                if text and text not in selected_examples:
                    selected_examples.append(text)
                    print(f"✓ Added: {text}")

            elif cmd.lower().startswith('r '):
                # Remove by number
                try:
                    num = int(cmd[2:].strip())
                    if 1 <= num <= len(selected_examples):
                        removed = selected_examples.pop(num - 1)
                        print(f"✓ Removed: {removed}")
                    else:
                        print(f"Invalid number. Must be 1-{len(selected_examples)}")
                except ValueError:
                    print("Invalid number.")

            else:
                print("Invalid command. Use: s <keyword>, a <text>, r <number>, or d")

        return selected_examples

    def _find_matches(self, document_text: str, keyword: str) -> List[str]:
        """
        Find text snippets matching keyword.

        Args:
            document_text: Full document text
            keyword: Keyword to search for

        Returns:
            List of text snippets containing the keyword
        """
        keyword_lower = keyword.lower()
        matches = []

        # Split into sentences (simple approach)
        sentences = document_text.replace('\n', ' ').split('.')

        for sentence in sentences:
            sentence = sentence.strip()
            if keyword_lower in sentence.lower():
                # Extract the relevant phrase (±50 chars around keyword)
                idx = sentence.lower().find(keyword_lower)
                start = max(0, idx - 50)
                end = min(len(sentence), idx + len(keyword) + 50)
                snippet = sentence[start:end].strip()

                # Try to extract just the key entity
                words = sentence.split()
                for word in words:
                    if keyword_lower in word.lower():
                        # Found the word containing keyword
                        matches.append(word.strip('.,;:()[]{}'))
                        break

        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for match in matches:
            if match.lower() not in seen:
                seen.add(match.lower())
                unique_matches.append(match)

        return unique_matches

    def _enter_manually(self, category_name: str, ai_examples: List[str]) -> List[str]:
        """
        Enter examples manually.

        Args:
            category_name: Name of category
            ai_examples: AI-suggested examples (for reference)

        Returns:
            List of manually entered examples
        """
        print(f"\n{'─'*70}")
        print(f"MANUAL ENTRY: Enter examples for '{category_name}'")
        print(f"{'─'*70}")
        print(f"Enter examples one per line. Enter blank line when done.\n")

        examples = []
        while True:
            example = input(f"Example {len(examples) + 1}: ").strip()
            if not example:
                break
            examples.append(example)

        if not examples:
            print(f"No examples entered. Keeping AI examples.")
            return ai_examples

        return examples

    def display_summary(self, user_examples: Dict[str, List[str]]):
        """
        Display summary of selected examples.

        Args:
            user_examples: Dict of category -> examples
        """
        print(f"\n{'='*70}")
        print("EXAMPLE SELECTION SUMMARY")
        print(f"{'='*70}\n")

        for cat_name, examples in user_examples.items():
            print(f"{cat_name}:")
            for ex in examples:
                print(f"  • {ex}")
            print()

    def save_examples(self, user_examples: Dict[str, List[str]], output_path: Path):
        """
        Save user-selected examples to JSON file.

        Args:
            user_examples: Dict of category -> examples
            output_path: Path to save JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(user_examples, f, indent=2)

        print(f"Examples saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    selector = ExampleSelector()

    # Example categories (from SchemaSuggester)
    example_categories = [
        {
            "name": "actors",
            "description": "People or roles performing actions",
            "examples": ["trustee", "debtor", "receiver"],
            "confidence": 0.85
        },
        {
            "name": "procedures",
            "description": "Actions to be performed",
            "examples": ["file proposal", "prepare statement"],
            "confidence": 0.92
        }
    ]

    # Example document
    example_doc = """
    Section 50.4 - Duties of Insolvent Person

    (1) The insolvent person shall, within ten days after filing a notice of intention,
        (a) prepare a statement of affairs;
        (b) provide the trustee with information regarding creditors;
        (c) attend the first meeting of creditors.

    (2) The trustee shall notify the official receiver if the insolvent person fails
    to comply with subsection (1).
    """

    print("Starting example selection...")
    user_examples = selector.review_and_refine(
        example_categories,
        example_doc,
        interactive=True
    )

    selector.display_summary(user_examples)

#!/usr/bin/env python3
"""
Test all 4 critical categories together.
Phase 3: Validate concept, statutory, deadline, and timeline examples.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

import langextract as lx
from data.examples.content_examples.concepts_examples import concept_examples
from data.examples.content_examples.statutory_examples import statutory_examples
from data.examples.content_examples.deadlines_examples import deadlines_examples
from data.examples.content_examples.timeline_examples import timeline_examples

console = Console()


def test_category(category_name, examples, prompt, test_text):
    """Test a single category."""

    console.print(f"\n[bold cyan]Testing {category_name}...[/bold cyan]")
    console.print(f"Examples: {len(examples)}")

    try:
        with console.status(f"[bold green]Extracting {category_name}..."):
            result = lx.extract(
                text_or_documents=test_text,
                prompt_description=prompt,
                examples=examples,
                model_id="gemini-2.5-flash",
                extraction_passes=1,  # Single pass for testing
                max_workers=3  # Conservative to avoid rate limits
            )

        console.print(f"[green]✓[/green] Extracted {len(result.extractions)} items")

        # Show first 3
        for i, e in enumerate(result.extractions[:3], 1):
            text = e.extraction_text[:50]
            console.print(f"  {i}. {text}...")

        return result

    except Exception as e:
        console.print(f"[red]✗[/red] Failed: {str(e)[:100]}")
        return None


def main():
    """Test all 4 categories."""

    console.print("\n[bold]Testing All Critical Categories[/bold]")
    console.print("=" * 70)

    # Load test text (first 30,000 chars - about 12 pages)
    text_file = Path("data/input/study_materials/insolvency_admin_extracted.txt")
    full_text = text_file.read_text()
    test_text = full_text[:30000]  # Smaller sample for faster testing

    console.print(f"\nTest text: {len(test_text):,} characters (~12 pages)\n")

    results = {}

    # Test 1: Concepts
    results['concepts'] = test_category(
        "Concepts",
        concept_examples,
        "Extract key insolvency concepts and their definitions.",
        test_text
    )

    # Test 2: Statutory References
    results['statutory'] = test_category(
        "Statutory References",
        statutory_examples,
        "Extract statutory references including act name, section number, and practical effect.",
        test_text
    )

    # Test 3: Deadlines
    results['deadlines'] = test_category(
        "Deadlines",
        deadlines_examples,
        "Extract deadlines with triggering events, timeframes, and responsible parties.",
        test_text
    )

    # Test 4: Timeline Sequences
    results['timelines'] = test_category(
        "Timeline Sequences",
        timeline_examples,
        "Extract complete event sequences showing timeline of steps and actors involved.",
        test_text
    )

    # Summary
    console.print("\n" + "=" * 70)
    console.print("[bold]Summary[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Category", style="cyan")
    table.add_column("Examples", justify="right")
    table.add_column("Extracted", justify="right")
    table.add_column("Status", justify="center")

    for name, result in results.items():
        if result:
            table.add_row(
                name.capitalize(),
                str(len(eval(f"{name}_examples"))),
                str(len(result.extractions)),
                "[green]✓[/green]"
            )
        else:
            table.add_row(
                name.capitalize(),
                "?",
                "0",
                "[red]✗[/red]"
            )

    console.print(table)

    # Save results
    output_dir = Path("data/output/knowledge_base")
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, result in results.items():
        if result:
            lx.io.save_annotated_documents(
                [result],
                output_name=f"test_{name}",
                output_dir=str(output_dir)
            )

    console.print(f"\n[green]✓[/green] Results saved to: {output_dir}/")

    console.print("\n[bold]Next Steps:[/bold]")
    console.print("1. Review results in data/output/knowledge_base/")
    console.print("2. If quality good (80%+): Create remaining category examples")
    console.print("3. If quality needs work: Refine examples and re-test")
    console.print()


if __name__ == "__main__":
    main()

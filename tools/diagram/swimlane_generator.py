#!/usr/bin/env python3
"""
Production-Ready Swimlane Diagram Generator

Generates professional swimlane diagrams for BIA process flows.
Uses PlantUML via Kroki.io API with Direct SVG fallback.

Usage:
    python tools/diagram/swimlane_generator.py --topic "Consumer Proposal" --section "50%"
    python tools/diagram/swimlane_generator.py --topic "Bankruptcy Process" --section "62%"
"""

import argparse
import sqlite3
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProcessStep:
    """Represents a single process step in swimlane."""
    actor: str
    action: str
    section: Optional[str] = None
    timeframe: Optional[str] = None
    day: Optional[int] = None
    modal_verb: Optional[str] = None
    consequence: Optional[str] = None


class SwimlaneGenerator:
    """
    Generate swimlane diagrams from database.

    Primary: PlantUML via Kroki.io API
    Fallback: Direct SVG generation
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.kroki_url = "https://kroki.io/plantuml/svg"

    # ========================================
    # Data Extraction
    # ========================================

    def get_process_data(self, section_pattern: str = "50%") -> List[ProcessStep]:
        """
        Extract process steps from database.

        Args:
            section_pattern: BIA section SQL pattern (e.g., "50%", "62%")

        Returns:
            List of ProcessStep objects ordered by section
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT DISTINCT
                a.role_canonical,
                COALESCE(p.step_name, p.action, p.extraction_text),
                dr.bia_section,
                d.timeframe,
                dr.modal_verb,
                c.extraction_text AS consequence
            FROM duty_relationships dr
            LEFT JOIN actors a ON dr.actor_id = a.id
            LEFT JOIN procedures p ON dr.procedure_id = p.id
            LEFT JOIN deadlines d ON dr.deadline_id = d.id
            LEFT JOIN consequences c ON dr.consequence_id = c.id
            WHERE dr.bia_section LIKE ?
              AND a.role_canonical IS NOT NULL
              AND (p.step_name IS NOT NULL OR p.action IS NOT NULL OR p.extraction_text IS NOT NULL)
            ORDER BY dr.bia_section, a.role_canonical
            LIMIT 50
        '''

        cursor.execute(query, (section_pattern,))

        steps = []
        for row in cursor.fetchall():
            actor = row[0]
            action = (row[1] or "Process step")[:60]  # Truncate long actions
            section = row[2]
            timeframe = row[3]
            modal_verb = row[4]
            consequence = row[5]

            # Estimate day from timeframe
            day = self._estimate_day_from_timeframe(timeframe)

            steps.append(ProcessStep(
                actor=actor,
                action=action,
                section=section,
                timeframe=timeframe,
                day=day,
                modal_verb=modal_verb,
                consequence=consequence[:40] if consequence else None
            ))

        conn.close()

        logger.info(f"Extracted {len(steps)} process steps for pattern '{section_pattern}'")
        return steps

    def _estimate_day_from_timeframe(self, timeframe: Optional[str]) -> Optional[int]:
        """Estimate day number from timeframe text."""
        if not timeframe:
            return None

        import re

        # Look for patterns like "10 days", "within 30 days", "5 business days"
        match = re.search(r'(\d+)\s*(?:business\s+)?days?', timeframe, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Look for "X weeks"
        match = re.search(r'(\d+)\s*weeks?', timeframe, re.IGNORECASE)
        if match:
            return int(match.group(1)) * 7

        # Look for "X months"
        match = re.search(r'(\d+)\s*months?', timeframe, re.IGNORECASE)
        if match:
            return int(match.group(1)) * 30

        # Look for "X years"
        match = re.search(r'(\d+)\s*years?', timeframe, re.IGNORECASE)
        if match:
            return int(match.group(1)) * 365

        return None

    # ========================================
    # PlantUML Generation
    # ========================================

    def generate_plantuml_swimlane(
        self,
        steps: List[ProcessStep],
        title: str = "BIA Process Flow"
    ) -> str:
        """
        Generate PlantUML activity diagram with swimlanes.

        Args:
            steps: List of process steps
            title: Diagram title

        Returns:
            PlantUML source code
        """
        # Get unique actors in order of appearance
        actors = list(dict.fromkeys(step.actor for step in steps))

        plantuml = "@startuml\n"
        plantuml += f"title {title}\n\n"

        # Styling
        plantuml += "skinparam backgroundColor white\n"
        plantuml += "skinparam ActivityBackgroundColor white\n"
        plantuml += "skinparam ActivityBorderColor #333333\n"
        plantuml += "skinparam ActivityFontSize 11\n"
        plantuml += "skinparam ArrowColor #666666\n\n"

        # Start in first actor's lane
        if actors:
            plantuml += f"|{actors[0]}|\n"
        plantuml += "start\n\n"

        current_lane = actors[0] if actors else None

        for i, step in enumerate(steps):
            # Switch lane if needed
            if step.actor != current_lane:
                plantuml += f"|{step.actor}|\n"
                current_lane = step.actor

            # Build activity text
            activity_text = step.action.replace('"', "'")

            # Add timeframe
            if step.timeframe:
                activity_text += f"\\n({step.timeframe})"

            # Add day marker
            if step.day is not None:
                activity_text += f"\\n[Day {step.day}]"

            # Add activity
            plantuml += f":{activity_text};\n"

            # Add note for section reference
            if step.section:
                plantuml += f"note right: BIA §{step.section}\n"

            # Add consequence note
            if step.consequence:
                plantuml += f"note right\n  ⚠️ If not met:\n  {step.consequence}\nend note\n"

            plantuml += "\n"

        plantuml += "stop\n"
        plantuml += "@enduml\n"

        return plantuml

    def plantuml_to_svg_via_kroki(
        self,
        plantuml_code: str,
        timeout: int = 30
    ) -> Optional[bytes]:
        """
        Convert PlantUML to SVG using Kroki.io API.

        Args:
            plantuml_code: PlantUML source
            timeout: Request timeout in seconds

        Returns:
            SVG data as bytes, or None if failed
        """
        try:
            data = plantuml_code.encode('utf-8')
            headers = {'Content-Type': 'text/plain'}

            request = urllib.request.Request(
                self.kroki_url,
                data=data,
                headers=headers
            )

            with urllib.request.urlopen(request, timeout=timeout) as response:
                svg_data = response.read()
                logger.info(f"Kroki API success: {len(svg_data)} bytes received")
                return svg_data

        except urllib.error.HTTPError as e:
            logger.error(f"Kroki API HTTP error: {e.code} {e.reason}")
            return None
        except urllib.error.URLError as e:
            logger.error(f"Kroki API URL error: {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Kroki API error: {e}")
            return None

    # ========================================
    # Direct SVG Generation (Fallback)
    # ========================================

    def generate_svg_swimlane(
        self,
        steps: List[ProcessStep],
        title: str = "BIA Process Flow"
    ) -> str:
        """
        Generate swimlane diagram as pure SVG.

        Fallback method when Kroki API unavailable.

        Args:
            steps: List of process steps
            title: Diagram title

        Returns:
            SVG XML string
        """
        # Layout parameters
        lane_width = 220
        step_height = 70
        step_margin = 15
        header_height = 50
        step_width = 200

        # Group by actor
        actors = list(dict.fromkeys(step.actor for step in steps))
        actor_steps = {actor: [] for actor in actors}

        for step in steps:
            actor_steps[step.actor].append(step)

        # Calculate dimensions
        max_steps_per_actor = max(len(actor_steps[actor]) for actor in actors)
        total_width = len(actors) * lane_width + 100
        total_height = header_height + 60 + max_steps_per_actor * (step_height + step_margin) + 50

        # Build SVG
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{total_width}"
     height="{total_height}"
     viewBox="0 0 {total_width} {total_height}">

    <!-- Title -->
    <text x="{total_width/2}" y="30"
          text-anchor="middle"
          font-size="20"
          font-weight="bold"
          font-family="Arial, sans-serif"
          fill="#333">
        {title}
    </text>

    <!-- Swimlanes -->
'''

        # Draw lanes and steps
        for i, actor in enumerate(actors):
            x = 50 + i * lane_width
            lane_color = self._get_lane_color(i)

            # Lane background
            svg += f'''
    <rect x="{x}" y="{header_height}"
          width="{lane_width}"
          height="{total_height - header_height - 40}"
          fill="{lane_color}"
          stroke="#333"
          stroke-width="2"
          fill-opacity="0.1"/>

    <!-- Lane header -->
    <rect x="{x}" y="{header_height}"
          width="{lane_width}"
          height="50"
          fill="{lane_color}"
          stroke="#333"
          stroke-width="2"
          fill-opacity="0.4"/>

    <text x="{x + lane_width/2}" y="{header_height + 30}"
          text-anchor="middle"
          font-size="14"
          font-weight="bold"
          font-family="Arial, sans-serif"
          fill="#333">
        {actor}
    </text>
'''

            # Draw steps for this actor
            for j, step in enumerate(actor_steps[actor]):
                y = header_height + 70 + j * (step_height + step_margin)

                # Step box
                svg += f'''
    <rect x="{x + 10}" y="{y}"
          width="{step_width}"
          height="{step_height}"
          fill="white"
          stroke="#333"
          stroke-width="2"
          rx="5"/>

    <text x="{x + lane_width/2}" y="{y + 20}"
          text-anchor="middle"
          font-size="11"
          font-family="Arial, sans-serif"
          fill="#333">
        {self._wrap_svg_text(step.action, 25)}
    </text>
'''

                # Day marker
                if step.day is not None:
                    svg += f'''
    <text x="{x + lane_width/2}" y="{y + step_height - 10}"
          text-anchor="middle"
          font-size="9"
          fill="#666"
          font-family="Arial, sans-serif">
        Day {step.day}
    </text>
'''

                # Section reference
                if step.section:
                    svg += f'''
    <text x="{x + lane_width/2}" y="{y + step_height - 22}"
          text-anchor="middle"
          font-size="8"
          fill="#999"
          font-style="italic"
          font-family="Arial, sans-serif">
        BIA §{step.section}
    </text>
'''

        svg += '''
</svg>'''

        logger.info(f"Generated direct SVG: {total_width}x{total_height}px")
        return svg

    def _get_lane_color(self, index: int) -> str:
        """Get color for lane based on index."""
        colors = [
            "#e3f2fd",  # Blue
            "#f3e5f5",  # Purple
            "#e8f5e9",  # Green
            "#fff3e0",  # Orange
            "#fce4ec",  # Pink
            "#e0f2f1",  # Teal
        ]
        return colors[index % len(colors)]

    def _wrap_svg_text(self, text: str, max_chars: int) -> str:
        """Simple text wrapping for SVG."""
        if len(text) <= max_chars:
            return text
        return text[:max_chars-3] + "..."

    # ========================================
    # Main Generation Method
    # ========================================

    def generate_swimlane_diagram(
        self,
        topic: str,
        section_pattern: str = "50%",
        output_format: str = "svg",
        use_fallback: bool = False
    ) -> Tuple[Path, str]:
        """
        Generate swimlane diagram (primary entry point).

        Args:
            topic: Diagram title
            section_pattern: BIA section pattern
            output_format: "svg" or "png"
            use_fallback: Force direct SVG (skip Kroki)

        Returns:
            (output_path, generation_method)
        """
        logger.info(f"Generating swimlane: {topic} (section: {section_pattern})")

        # Get data
        steps = self.get_process_data(section_pattern)

        if not steps:
            logger.warning(f"No process steps found for section pattern: {section_pattern}")
            # Return empty diagram
            steps = [ProcessStep(
                actor="Notice",
                action=f"No process data found for section {section_pattern}",
                section=None
            )]

        # Generate PlantUML
        plantuml_code = self.generate_plantuml_swimlane(steps, title=topic)

        # Save PlantUML source
        output_dir = Path("data/output/diagrams")
        output_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = topic.lower().replace(' ', '_').replace('/', '_')
        plantuml_file = output_dir / f"{safe_filename}_swimlane.plantuml"
        plantuml_file.write_text(plantuml_code)
        logger.info(f"PlantUML source saved: {plantuml_file}")

        # Try Kroki API (unless fallback forced)
        generation_method = "unknown"

        if not use_fallback:
            svg_data = self.plantuml_to_svg_via_kroki(plantuml_code)

            if svg_data:
                # Kroki success
                svg_file = output_dir / f"{safe_filename}_swimlane.svg"
                svg_file.write_bytes(svg_data)
                logger.info(f"✅ PlantUML via Kroki: {svg_file}")
                return (svg_file, "plantuml_kroki")

            else:
                logger.warning("Kroki API failed, falling back to direct SVG")

        # Fallback: Direct SVG
        svg_code = self.generate_svg_swimlane(steps, title=topic)
        svg_file = output_dir / f"{safe_filename}_swimlane_direct.svg"
        svg_file.write_text(svg_code)
        logger.info(f"✅ Direct SVG: {svg_file}")
        return (svg_file, "direct_svg")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate swimlane diagrams for BIA process flows'
    )

    parser.add_argument(
        '--topic',
        required=True,
        help='Diagram title (e.g., "Consumer Proposal Process")'
    )

    parser.add_argument(
        '--section',
        default='50%',
        help='BIA section pattern (e.g., "50%%", "62%%")'
    )

    parser.add_argument(
        '--db',
        default='projects/insolvency-law/database/knowledge.db',
        help='Path to database file'
    )

    parser.add_argument(
        '--format',
        default='svg',
        choices=['svg', 'png'],
        help='Output format'
    )

    parser.add_argument(
        '--fallback',
        action='store_true',
        help='Force direct SVG generation (skip Kroki API)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Generate diagram
    db_path = Path(args.db)

    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return 1

    generator = SwimlaneGenerator(db_path)

    output_path, method = generator.generate_swimlane_diagram(
        topic=args.topic,
        section_pattern=args.section,
        output_format=args.format,
        use_fallback=args.fallback
    )

    print("\n" + "=" * 80)
    print("SWIMLANE DIAGRAM GENERATED")
    print("=" * 80)
    print(f"Title:  {args.topic}")
    print(f"Section: {args.section}")
    print(f"Method: {method}")
    print(f"Output: {output_path.absolute()}")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    exit(main())

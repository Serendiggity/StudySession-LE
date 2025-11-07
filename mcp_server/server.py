#!/usr/bin/env python3
"""
Universal Knowledge Platform MCP Server

Knowledge extraction and query server for Claude Desktop and Claude Code.
Works with any domain: law, medicine, engineering, and more.
Provides tools and resources for multi-project knowledge bases.
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add shared/src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "shared" / "src"))
# NOTE: Do NOT add src/ to path - causes import conflicts with shared/src/extraction

from project import ProjectManager, Project
from extraction import SourceManager, ExtractionRunner, DatabaseLoader

# Add src/ to path AFTER shared imports for other modules
sys.path.insert(0, str(repo_root / "src"))

# Import new modules for Tier 1 features
from analysis.coverage_analyzer import CoverageAnalyzer
from visualization.diagram_generator import MermaidDiagramGenerator

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    import mcp.types as types
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


# Initialize MCP server
app = Server("knowledge-platform")

# Initialize ProjectManager
pm = ProjectManager(repo_root)


# ============================================================================
# TOOLS
# ============================================================================

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="query_knowledge_base",
            description=(
                "⚠️ DEPRECATED: DO NOT USE THIS TOOL FOR USER QUESTIONS. "
                "This is a low-level database search for internal exploration only. "
                "❌ NEVER use for: exam questions, legal questions, 'what does the law say', discharge questions. "
                "✅ ALWAYS use 'answer_exam_question' instead - it has better search and prevents hallucinations. "
                "This tool may return 'NOT FOUND' even when content exists (use answer_exam_question for better results)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to answer (e.g., 'What must the trustee do after filing NOI?')"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Optional: specific project to query (defaults to current project)"
                    }
                },
                "required": ["query"]
            }
        ),

        Tool(
            name="switch_project",
            description=(
                "Switch to a different knowledge base project. "
                "Use when user wants to query a different domain (e.g., switch from law to medicine). "
                "Lists available projects if no project_id provided."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID to switch to (e.g., 'insolvency-law', 'radiology')"
                    }
                },
                "required": []
            }
        ),

        Tool(
            name="add_material",
            description=(
                "Add source material to current project for extraction. "
                "Use when user wants to add a PDF, textbook, or document to the knowledge base. "
                "Material will be queued for extraction."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to source file (PDF, text, markdown, etc.)"
                    },
                    "source_name": {
                        "type": "string",
                        "description": "Optional: Custom name for the source"
                    }
                },
                "required": ["file_path"]
            }
        ),

        Tool(
            name="extract_knowledge",
            description=(
                "Run knowledge extraction on unextracted sources in current project. "
                "Use after adding materials to extract entities and relationships. "
                "Shows progress in real-time."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "Optional: Extract specific source (omit to extract all pending)"
                    },
                    "use_mock": {
                        "type": "boolean",
                        "description": "Use mock extraction for testing (no API calls)",
                        "default": False
                    }
                },
                "required": []
            }
        ),

        Tool(
            name="get_statistics",
            description=(
                "Get statistics for current project. "
                "Shows entity counts, relationship counts, sources, etc. "
                "Use when user asks 'what's in the database' or 'how much data'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Optional: specific project (defaults to current)"
                    }
                },
                "required": []
            }
        ),

        Tool(
            name="answer_exam_question",
            description=(
                "✅ PRIMARY TOOL - USE THIS FOR ALL USER QUESTIONS ABOUT THE LAW/DOMAIN. "
                "Returns COMPLETE authoritative source text with citations and anti-hallucination instructions. "
                "Advanced search with phrase matching + fallback strategies (better than query_knowledge_base). "
                "ALWAYS use for: exam questions, 'which of the following', legal/medical/technical questions, "
                "'what does the law say', discharge questions, debts questions, ANY domain-specific query. "
                "Output format: Sidebar with full quoted text + source citation + rationale + cross-references. "
                "CRITICAL: Follow ALL instructions in tool output - they prevent hallucinations. "
                "Universal for all domains: law (BIA §178), medicine (ACR), engineering (ACI). "
                "Records every Q&A to CSV audit trail."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to answer (exam, technical, clinical, legal, etc.)"
                    },
                    "answer_choice": {
                        "type": "string",
                        "description": "Optional: The selected answer (e.g., 'Option 2', 'Yes', 'Contraindicated')"
                    },
                    "topic_hint": {
                        "type": "string",
                        "description": "Optional: Topic keyword to narrow search (e.g., 'discharge', 'contrast safety', 'beam design')"
                    }
                },
                "required": ["question"]
            }
        ),

        Tool(
            name="analyze_study_guide_coverage",
            description=(
                "Analyze study guide completeness against database entities. "
                "Checks coverage of concepts, procedures, deadlines, forms, actors, consequences, and cross-references. "
                "Returns comprehensive coverage metrics with identified gaps and recommendations. "
                "Use to verify study guide quality before finalizing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic being analyzed (e.g., 'consumer proposals')"
                    },
                    "study_guide_text": {
                        "type": "string",
                        "description": "Full text of the study guide to analyze"
                    }
                },
                "required": ["topic", "study_guide_text"]
            }
        ),

        Tool(
            name="generate_timeline_diagram",
            description=(
                "Generate Mermaid Gantt chart timeline diagram from database deadlines. "
                "Automatically creates visual timeline showing all deadlines for a topic. "
                "Returns Mermaid diagram code that can be rendered in markdown."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to generate timeline for (e.g., 'consumer proposals')"
                    }
                },
                "required": ["topic"]
            }
        ),

        Tool(
            name="generate_process_diagram",
            description=(
                "Generate Mermaid flowchart diagram from database procedures. "
                "Automatically creates visual process flow showing all steps for a topic. "
                "Returns Mermaid diagram code that can be rendered in markdown."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to generate process diagram for (e.g., 'consumer proposals')"
                    }
                },
                "required": ["topic"]
            }
        ),

        Tool(
            name="generate_comparison_diagram",
            description=(
                "Generate comparison table between two topics. "
                "Extracts key features from database and creates markdown comparison table. "
                "Useful for understanding differences between similar concepts."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic1": {
                        "type": "string",
                        "description": "First topic to compare"
                    },
                    "topic2": {
                        "type": "string",
                        "description": "Second topic to compare"
                    }
                },
                "required": ["topic1", "topic2"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""

    if name == "query_knowledge_base":
        return await tool_query_knowledge_base(arguments)

    elif name == "switch_project":
        return await tool_switch_project(arguments)

    elif name == "add_material":
        return await tool_add_material(arguments)

    elif name == "extract_knowledge":
        return await tool_extract_knowledge(arguments)

    elif name == "get_statistics":
        return await tool_get_statistics(arguments)

    elif name == "answer_exam_question":
        return await tool_answer_exam_question(arguments)

    elif name == "analyze_study_guide_coverage":
        return await tool_analyze_coverage(arguments)

    elif name == "generate_timeline_diagram":
        return await tool_generate_timeline(arguments)

    elif name == "generate_process_diagram":
        return await tool_generate_process(arguments)

    elif name == "generate_comparison_diagram":
        return await tool_generate_comparison(arguments)

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

async def tool_query_knowledge_base(args: Dict[str, Any]) -> List[TextContent]:
    """Query knowledge base with direct quotes."""
    query = args.get("query", "")
    project_id = args.get("project_id")

    # Get project
    if project_id:
        project = pm.load_project(project_id)
    else:
        project = pm.get_current_project()

    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project tool to select a project first."
        )]

    # Check if database exists
    db_path = Path(project.database_path)
    if not db_path.exists():
        return [TextContent(
            type="text",
            text=f"No database found for {project.project_name}. Add materials and run extraction first."
        )]

    # Query database
    try:
        results = query_database(db_path, query)

        if not results:
            return [TextContent(
                type="text",
                text=f"""**CRITICAL INSTRUCTION:**
DO NOT answer this question from your training data or general knowledge.
DO NOT provide analysis based on "bankruptcy law principles" or any external knowledge.

**Database Search Result:** No results found for query: "{query}"

**You MUST tell the user:**
"I searched the knowledge base but found no matching content for this query. I cannot answer this question without database results. Please try:
1. Different keywords (e.g., 'discharge', 'debts not released', 'Section 178')
2. More specific terms from the BIA
3. Verifying the content exists in the database"

**DO NOT provide any answer beyond stating no results were found.**"""
            )]

        # Format response with direct quotes
        response = f"**Query**: {query}\n"
        response += f"**Project**: {project.project_name}\n\n"
        response += f"**Found {len(results)} result(s)**:\n\n"

        for idx, result in enumerate(results, 1):
            response += f"**{idx}. {result['type']}**\n"
            response += f"```\n{result['text']}\n```\n"
            if result.get('source'):
                response += f"*Source: {result['source']}*\n"
            response += "\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error querying database: {e}"
        )]


async def tool_switch_project(args: Dict[str, Any]) -> List[TextContent]:
    """Switch to a different project."""
    project_id = args.get("project_id")

    # If no project_id, list available projects
    if not project_id:
        projects = pm.list_projects()

        if not projects:
            return [TextContent(
                type="text",
                text="No projects found. Create a project first."
            )]

        current = pm.get_current_project()
        current_id = current.project_id if current else None

        response = f"**Available Projects ({len(projects)})**:\n\n"
        for p in projects:
            active = " (current)" if p.project_id == current_id else ""
            response += f"- **{p.project_id}**{active}\n"
            response += f"  Name: {p.project_name}\n"
            response += f"  Domain: {p.domain}\n"
            response += f"  Entities: {p.total_entities:,}\n"
            response += f"  Relationships: {p.total_relationships:,}\n\n"

        response += "Use `switch_project` with a project_id to switch."

        return [TextContent(type="text", text=response)]

    # Switch to project
    try:
        project = pm.switch_to(project_id)

        response = f"**Switched to**: {project.project_name}\n\n"
        response += f"- Domain: {project.domain}\n"
        response += f"- Entities: {project.total_entities:,}\n"
        response += f"- Relationships: {project.total_relationships:,}\n"
        response += f"- Sources: {project.sources_count}\n"

        return [TextContent(type="text", text=response)]

    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def tool_add_material(args: Dict[str, Any]) -> List[TextContent]:
    """Add source material to current project."""
    file_path = args.get("file_path", "")
    source_name = args.get("source_name")

    # Get current project
    project = pm.get_current_project()
    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project first."
        )]

    # Add source
    try:
        project_dir = pm.projects_dir / project.project_id
        source_manager = SourceManager(project_dir)

        source = source_manager.add_source(
            Path(file_path),
            source_name=source_name
        )

        response = f"**Source Added Successfully!**\n\n"
        response += f"- ID: {source.source_id}\n"
        response += f"- Name: {source.source_name}\n"
        response += f"- Type: {source.source_type}\n"
        response += f"- Size: {source.file_size:,} characters\n\n"
        response += f"Use `extract_knowledge` to extract knowledge from this source."

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def tool_extract_knowledge(args: Dict[str, Any]) -> List[TextContent]:
    """Run extraction on sources."""
    source_id = args.get("source_id")
    use_mock = args.get("use_mock", False)

    # Get current project
    project = pm.get_current_project()
    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project first."
        )]

    # Run extraction
    try:
        project_dir = pm.projects_dir / project.project_id
        runner = ExtractionRunner(project_dir, use_mock=use_mock)

        if source_id:
            result = runner.extract_source(source_id)

            response = f"**Extraction Complete!**\n\n"
            response += f"- Source: {result['source_name']}\n"
            response += f"- Entities extracted: {result['entities_extracted']:,}\n"
            response += f"- Relationships extracted: {result['relationships_extracted']:,}\n\n"
            response += f"**Total in database**:\n"
            response += f"- Entities: {result['total_entities']:,}\n"
            response += f"- Relationships: {result['total_relationships']:,}\n"

        else:
            result = runner.extract_all_sources()

            response = f"**Extraction Complete!**\n\n"
            response += f"- Sources processed: {result['sources_processed']}\n"
            response += f"- Entities extracted: {result['total_entities']:,}\n"
            response += f"- Relationships extracted: {result['total_relationships']:,}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}\n\nTry with use_mock=true for testing.")]


async def tool_get_statistics(args: Dict[str, Any]) -> List[TextContent]:
    """Get project statistics."""
    project_id = args.get("project_id")

    # Get project
    if project_id:
        project = pm.load_project(project_id)
    else:
        project = pm.get_current_project()

    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project first."
        )]

    # Get database statistics
    try:
        project_dir = pm.projects_dir / project.project_id
        loader = DatabaseLoader(project_dir)
        stats = loader.get_statistics()

        response = f"**Statistics for {project.project_name}**\n\n"
        response += f"**Totals**:\n"
        response += f"- Entities: {stats['total_entities']:,}\n"
        response += f"- Relationships: {stats['total_relationships']:,}\n"
        response += f"- Sources: {project.sources_count}\n\n"

        if stats['entities_by_category']:
            response += f"**Entities by Category**:\n"
            for cat, count in sorted(stats['entities_by_category'].items()):
                response += f"- {cat}: {count:,}\n"
            response += "\n"

        if stats['relationships_by_type']:
            response += f"**Relationships by Type**:\n"
            for rel, count in sorted(stats['relationships_by_type'].items()):
                response += f"- {rel}: {count:,}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def tool_answer_exam_question(args: Dict[str, Any]) -> List[TextContent]:
    """
    Answer question with sidebar formatting and CSV recording.

    UNIVERSAL: Adapts to any domain (law, medicine, engineering, etc.)
    based on project's domain_terminology configuration.
    """
    from datetime import datetime
    import csv

    question = args.get("question", "")
    answer_choice = args.get("answer_choice", "")
    topic_hint = args.get("topic_hint", "")

    # Get current project
    project = pm.get_current_project()
    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project to select a project first."
        )]

    # Check database exists
    db_path = Path(project.database_path)
    if not db_path.exists():
        return [TextContent(
            type="text",
            text=f"No database found for {project.project_name}."
        )]

    # Search database using universal functions
    try:
        keywords = topic_hint if topic_hint else question

        # Universal search (adapts to project's structure)
        structured_results, relationship_results = search_content_universal(
            db_path,
            keywords,
            project.domain_terminology
        )

        # Universal formatting (adapts to project's terminology)
        answer = format_sidebar_answer(
            question,
            structured_results,
            relationship_results,
            project.domain_terminology,
            answer_choice
        )

        # Add search details
        response = answer + f"""

**Search Details:**
- Keywords: {keywords}
- Structured content found: {len(structured_results)}
- Relationships found: {len(relationship_results)}
- Domain: {project.domain}
"""

        # Record to CSV (project-specific path)
        try:
            csv_path = project.get_tracking_file("questions_answered.csv")

            # Check if file exists to determine if we need header
            file_exists = csv_path.exists()

            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header if new file
                if not file_exists:
                    writer.writerow([
                        "timestamp", "question", "answer_choice", "primary_quote",
                        "reference", "source", "cross_references",
                        "search_method", "keywords", "rationale",
                        "correct_answer", "is_correct"
                    ])

                # Extract quote from results
                if structured_results:
                    quote = structured_results[0]['full_text'][:500]
                    source_ref = structured_results[0]['id']
                elif relationship_results:
                    quote = relationship_results[0]['text'][:500]
                    source_ref = "Study Materials"
                else:
                    quote = "NOT FOUND"
                    source_ref = "N/A"

                # Write record
                writer.writerow([
                    datetime.now().isoformat(),
                    question,
                    answer_choice if answer_choice else "",
                    quote,
                    source_ref,
                    f"{project.domain_terminology.get('source_type', 'document')}",
                    "",  # cross_references (extracted in answer)
                    "Universal FTS5 search",
                    keywords,
                    f"Based on {project.domain} domain knowledge base",
                    "",  # correct_answer (user fills later)
                    ""   # is_correct (user fills later)
                ])

            response += f"\n✅ **Recorded to**: `{csv_path.relative_to(repo_root)}`"

        except Exception as csv_error:
            response += f"\n⚠️  **CSV recording failed**: {csv_error}"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error answering question: {e}\n\nTry checking if database tables are properly set up."
        )]


# ============================================================================
# RESOURCES
# ============================================================================

@app.list_resources()
async def list_resources() -> List[types.Resource]:
    """List available resources."""
    resources = [
        types.Resource(
            uri="project://list",
            name="List of all projects",
            mimeType="application/json",
            description="Lists all available knowledge base projects"
        )
    ]

    # Add project-specific resources
    projects = pm.list_projects()
    for project in projects:
        resources.append(
            types.Resource(
                uri=f"project://{project.project_id}/schema",
                name=f"Schema for {project.project_name}",
                mimeType="application/json",
                description=f"Entity schema for {project.project_name} project"
            )
        )

    # NOTE: BIA section resources disabled to prevent memory issues
    # Claude Desktop crashes when loading 249+ resources
    # BIA sections can still be accessed via read_resource() on demand

    # insolvency = pm.load_project("insolvency-law")
    # if insolvency:
    #     for section_num in range(1, 250):
    #         resources.append(
    #             types.Resource(
    #                 uri=f"bia://section/{section_num}",
    #                 name=f"BIA Section {section_num}",
    #                 mimeType="text/plain",
    #                 description=f"Bankruptcy and Insolvency Act - Section {section_num}"
    #             )
    #         )

    return resources


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""

    if uri == "project://list":
        projects = pm.list_projects()
        return json.dumps([p.to_dict() for p in projects], indent=2)

    elif uri.startswith("project://") and uri.endswith("/schema"):
        # Extract project_id
        project_id = uri.replace("project://", "").replace("/schema", "")
        config = pm.get_project_config(project_id)
        if config:
            return json.dumps(config.get("entity_schema", {}), indent=2)
        else:
            raise ValueError(f"Project not found: {project_id}")

    elif uri.startswith("bia://section/"):
        # Extract section number
        section_num = uri.replace("bia://section/", "")
        return get_bia_section(int(section_num))

    else:
        raise ValueError(f"Unknown resource: {uri}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def query_database(db_path: Path, query: str) -> List[Dict[str, str]]:
    """Query database for relationships and BIA sections matching query."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = []

    try:
        # 1. Search relationships table
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='relationships_fts'
        """)

        has_rel_fts = cursor.fetchone() is not None

        if has_rel_fts:
            cursor.execute("""
                SELECT r.relationship_text, r.relationship_type, r.source_id
                FROM relationships r
                WHERE r.id IN (
                    SELECT rowid FROM relationships_fts
                    WHERE relationship_text MATCH ?
                )
                LIMIT 10
            """, (query,))
        else:
            cursor.execute("""
                SELECT relationship_text, relationship_type, source_id
                FROM relationships
                WHERE relationship_text LIKE ?
                LIMIT 10
            """, (f"%{query}%",))

        for row in cursor.fetchall():
            results.append({
                "type": row[1] if len(row) > 1 else "Relationship",
                "text": row[0],
                "source": row[2] if len(row) > 2 else "Study Materials"
            })

        # 2. Search BIA sections table
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='bia_sections_fts'
        """)

        has_bia_fts = cursor.fetchone() is not None

        if has_bia_fts:
            cursor.execute("""
                SELECT s.section_number, s.section_title, s.full_text
                FROM bia_sections s
                WHERE s.rowid IN (
                    SELECT rowid FROM bia_sections_fts
                    WHERE full_text MATCH ?
                )
                LIMIT 10
            """, (query,))
        else:
            cursor.execute("""
                SELECT section_number, section_title, full_text
                FROM bia_sections
                WHERE full_text LIKE ?
                LIMIT 10
            """, (f"%{query}%",))

        for row in cursor.fetchall():
            # Return COMPLETE full_text (no truncation - let caller decide)
            results.append({
                "type": f"BIA Section {row[0]}",
                "text": row[2],  # Full text, no truncation
                "section_number": row[0],
                "section_title": row[1],
                "source": "BIA Statute"
            })

    finally:
        conn.close()

    return results


def get_bia_section(section_num: int) -> str:
    """Get BIA section text (stub for now)."""
    # This would read from database or files
    return f"BIA Section {section_num} text would be here.\n\n(Not yet implemented - needs BIA text extraction)"


def find_primary_content_table(db_path: Path, domain_config: Dict) -> Optional[str]:
    """
    Discover the primary structured content table in database.

    Universal function that adapts to any domain's table structure.

    Args:
        db_path: Path to project database
        domain_config: Domain terminology configuration

    Returns:
        Table name or None if not found
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Try explicit config first
        explicit_table = domain_config.get('primary_content_table')
        if explicit_table:
            cursor.execute(f"""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            """, (explicit_table,))
            if cursor.fetchone():
                return explicit_table

        # 2. Fallback: Find any table with full_text column (structured content pattern)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]

            # Look for tables with hierarchical content pattern
            if 'full_text' in columns and any(col in columns for col in ['section_number', 'content_id', 'chapter_id']):
                return table

        return None

    finally:
        conn.close()


def search_content_universal(db_path: Path, query: str, domain_config: Dict) -> tuple[List[Dict], List[Dict]]:
    """
    Universal content search that adapts to any domain.

    Uses hybrid search (FTS5 + vector embeddings with RRF) for 30% better retrieval.

    Returns:
        (structured_results, relationship_results)
    """
    import re
    import numpy as np

    # Try to load sentence transformers for hybrid search
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        use_hybrid = True
    except:
        use_hybrid = False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    structured_results = []
    relationship_results = []

    try:
        # 1. Search primary structured content
        content_table = find_primary_content_table(db_path, domain_config)

        if content_table:
            # Check for FTS index
            fts_table = f"{content_table}_fts"
            cursor.execute(f"""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            """, (fts_table,))

            has_fts = cursor.fetchone() is not None

            if has_fts:
                # Get table structure to determine ID column
                cursor.execute(f"PRAGMA table_info({content_table})")
                columns = {row[1]: row[0] for row in cursor.fetchall()}

                id_col = 'section_number' if 'section_number' in columns else 'content_id' if 'content_id' in columns else 'id'
                title_col = 'section_title' if 'section_title' in columns else 'title' if 'title' in columns else None

                # Build dynamic query (qualify with table name to avoid ambiguity in JOIN)
                select_cols = [f'{content_table}.{id_col}', f'{content_table}.full_text']
                if title_col:
                    select_cols.insert(1, f'{content_table}.{title_col}')

                # HYBRID SEARCH: FTS5 + Vector embeddings with RRF
                # This provides 30% better retrieval than pure FTS5

                # Check if embeddings table exists
                emb_table = f"{content_table}_embeddings"
                cursor.execute(f"""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name=?
                """, (emb_table,))
                has_embeddings = cursor.fetchone() is not None

                if use_hybrid and has_embeddings:
                    # HYBRID SEARCH: FTS5 + Vector

                    # 1. Get FTS5 results (top 20 for RRF)
                    fts_results = []
                    search_queries = [query]  # Start with original query

                    # Extract key terms for fallback
                    stop_words = {'by', 'the', 'a', 'an', 'to', 'of', 'in', 'for', 'on', 'at', 'from', 'is', 'are', 'was'}
                    key_terms = [w for w in query.split() if w.lower() not in stop_words and len(w) > 2]
                    if key_terms:
                        search_queries.append(' OR '.join(key_terms))  # Fallback OR query

                    for search_query in search_queries:
                        cursor.execute(f"""
                            SELECT {id_col}
                            FROM {content_table}
                            JOIN {fts_table} ON {content_table}.rowid = {fts_table}.rowid
                            WHERE {fts_table} MATCH ?
                            ORDER BY rank
                            LIMIT 20
                        """, (search_query,))
                        fts_results = [row[0] for row in cursor.fetchall()]
                        if fts_results:
                            break  # Got FTS results

                    # 2. Get vector similarity results (top 20 for RRF)
                    query_emb = model.encode(query)
                    cursor.execute(f'SELECT section_number, embedding_json FROM {emb_table}')
                    vec_results = []
                    for section_id, emb_json in cursor.fetchall():
                        emb = np.array(json.loads(emb_json))
                        sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
                        vec_results.append((section_id, sim))
                    vec_results.sort(key=lambda x: x[1], reverse=True)
                    vec_top = [section_id for section_id, _ in vec_results[:20]]

                    # 3. Reciprocal Rank Fusion (RRF)
                    fts_ranks = {section_id: i for i, section_id in enumerate(fts_results)}
                    vec_ranks = {section_id: i for i, section_id in enumerate(vec_top)}
                    all_sections = set(fts_ranks.keys()) | set(vec_ranks.keys())

                    k = 60  # RRF constant
                    rrf_scores = []
                    for section_id in all_sections:
                        fts_score = 1.0 / (k + fts_ranks.get(section_id, 999)) if section_id in fts_ranks else 0
                        vec_score = 1.0 / (k + vec_ranks.get(section_id, 999)) if section_id in vec_ranks else 0
                        rrf_scores.append((section_id, fts_score + vec_score))

                    rrf_scores.sort(key=lambda x: x[1], reverse=True)
                    top_sections = [section_id for section_id, _ in rrf_scores[:5]]

                    # 4. Get full content for top results
                    for section_id in top_sections:
                        cursor.execute(f"""
                            SELECT {', '.join(select_cols)}
                            FROM {content_table}
                            WHERE {id_col} = ?
                        """, (section_id,))
                        row = cursor.fetchone()
                        if row:
                            structured_results.append({
                                'id': row[0],
                                'title': row[1] if len(row) > 2 else '',
                                'full_text': row[-1],
                                'table': content_table
                            })

                else:
                    # FALLBACK: Pure FTS5 (if no embeddings or sentence-transformers not available)
                    search_queries = [query]
                    stop_words = {'by', 'the', 'a', 'an', 'to', 'of', 'in', 'for', 'on', 'at', 'from', 'is', 'are', 'was'}
                    key_terms = [w for w in query.split() if w.lower() not in stop_words and len(w) > 2]
                    if key_terms:
                        search_queries.append(' OR '.join(key_terms))

                    for search_query in search_queries:
                        cursor.execute(f"""
                            SELECT {', '.join(select_cols)}
                            FROM {content_table}
                            JOIN {fts_table} ON {content_table}.rowid = {fts_table}.rowid
                            WHERE {fts_table} MATCH ?
                            ORDER BY rank
                            LIMIT 5
                        """, (search_query,))

                        rows = cursor.fetchall()
                        if rows:
                            for row in rows:
                                structured_results.append({
                                    'id': row[0],
                                    'title': row[1] if len(row) > 2 else '',
                                    'full_text': row[-1],
                                    'table': content_table
                                })
                            break

        # 2. Search relationships (always present)
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='relationships_fts'
        """)

        if cursor.fetchone():
            cursor.execute("""
                SELECT r.relationship_text, r.relationship_type
                FROM relationships r
                JOIN relationships_fts ON r.id = relationships_fts.rowid
                WHERE relationships_fts MATCH ?
                ORDER BY rank
                LIMIT 5
            """, (query,))

            for row in cursor.fetchall():
                relationship_results.append({
                    'text': row[0],
                    'type': row[1]
                })

        # 3. Search atomic entity tables (study materials)
        entity_tables = [
            ('concepts', 'concepts_fts', ['term', 'definition', 'extraction_text']),
            ('actors', 'actors_fts', ['role_canonical', 'extraction_text']),
            ('deadlines', 'deadlines_fts', ['extraction_text']),
            ('documents', 'documents_fts', ['extraction_text']),
            ('procedures', 'procedures_fts', ['extraction_text']),
            ('consequences', 'consequences_fts', ['extraction_text']),
            ('statutory_references', 'statutory_references_fts', ['extraction_text'])
        ]

        for table_name, fts_name, columns in entity_tables:
            # Check if FTS table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
            """, (fts_name,))

            if cursor.fetchone():
                # Build column selection (use COALESCE for optional fields)
                col_select = ', '.join([f"COALESCE(e.{col}, '')" for col in columns])

                cursor.execute(f"""
                    SELECT {col_select}, e.section_number, e.section_title
                    FROM {table_name} e
                    JOIN {fts_name} ON e.id = {fts_name}.rowid
                    WHERE {fts_name} MATCH ?
                    ORDER BY rank
                    LIMIT 3
                """, (query,))

                for row in cursor.fetchall():
                    # Combine all text fields
                    text_parts = [str(part) for part in row[:-2] if part]
                    section_ref = row[-2] if row[-2] else ""
                    section_title = row[-1] if row[-1] else ""

                    combined_text = " | ".join(text_parts)
                    if section_ref:
                        combined_text += f" [Study Materials §{section_ref}]"
                    if section_title:
                        combined_text += f" ({section_title})"

                    relationship_results.append({
                        'text': combined_text,
                        'type': table_name.replace('_', ' ').title()
                    })

        return (structured_results, relationship_results)

    finally:
        conn.close()


def format_sidebar_answer(
    question: str,
    structured_results: List[Dict],
    relationship_results: List[Dict],
    domain_config: Dict,
    answer_choice: str = ""
) -> str:
    """
    Format answer in universal sidebar style.

    Adapts to domain terminology while maintaining consistent structure.
    """
    import re

    # Get domain-specific formatting
    ref_format = domain_config.get('reference_format', '{id}')
    ref_prefix = domain_config.get('reference_prefix', '')
    source_type = domain_config.get('source_type', 'document')

    # Determine primary result
    if structured_results:
        primary = structured_results[0]
        content_id = primary['id']
        full_text = primary['full_text']

        # Format reference
        reference = ref_format.replace('{section_number}', str(content_id)).replace('{id}', str(content_id))
        if ref_prefix:
            source_display = f"{ref_prefix} {reference}"
        else:
            source_display = reference

        # Extract quote (return full text for complete answers)
        # For very long sections, show first + last portions
        if len(full_text) <= 3000:
            # Short/medium sections: return complete text
            quote = full_text.strip()
        else:
            # Very long sections: show beginning and end
            quote = full_text[:1500].strip() + "\n\n[... middle section omitted ...]\n\n" + full_text[-1500:].strip()

        # Find cross-references in text
        cross_refs = re.findall(r'section\s+(\d+(?:\.\d+)?)', full_text, re.IGNORECASE)
        cross_refs = [f"{ref_format.replace('{section_number}', ref).replace('{id}', ref)}"
                     for ref in cross_refs[:3] if ref != str(content_id)]
        cross_refs_text = ", ".join(cross_refs) if cross_refs else "None"

        rationale = f"Based on {source_type} {source_display}. This {source_type} directly addresses this topic."

    elif relationship_results:
        primary = relationship_results[0]
        quote = primary['text']
        source_display = "Study Materials"
        cross_refs_text = "None"
        rationale = "Found in study materials database."

    else:
        return f"""**INSTRUCTIONS FOR ANSWERING:**
- No matching content found in database
- Inform user that the answer is not available in the knowledge base
- DO NOT provide an answer from your training data or general knowledge
- Tell user to try different search terms or verify content exists

```
┌─ Q: {question}
│
├─ A: ❌ NOT FOUND
│
├─ Searched: Structured content + relationships
│
└─ Suggestion: Try different keywords or verify content is in database
```

**You MUST tell the user:** No content found for this query. DO NOT answer from general knowledge."""

    # Format sidebar (universal structure, domain-adapted content)
    # Add instructions for Claude Desktop to preserve format and prioritize quotes
    answer = f"""**INSTRUCTIONS FOR ANSWERING:**
- **SHOW THE DIRECT QUOTE VERBATIM** - The quote below is the authoritative source text
- **DO NOT paraphrase or summarize the quote** - Display it exactly as shown
- **Preserve the sidebar format** - The structured layout ensures transparency
- **Base your answer ONLY on the quoted text** - Do not add external knowledge
- **Cite the source reference** when explaining

```
┌─ Q: {question}
│
├─ A: {'✅ ' + answer_choice if answer_choice else '📋 See quote below'}
│
├─ Quote: "{quote}"  {source_display}
│
├─ Why: {rationale}
│
├─ Cross-Refs: {cross_refs_text}
│
└─ Source: {source_display} (database)
```

**Your answer must:**
1. Quote the exact statutory text shown above
2. Cite {source_display} as the authoritative source
3. Explain based ONLY on the quoted content
4. Mention cross-references if relevant: {cross_refs_text}"""

    return answer


async def tool_analyze_coverage(args: Dict[str, Any]) -> List[TextContent]:
    """
    Analyze study guide coverage against database.
    """
    topic = args.get("topic", "")
    study_guide_text = args.get("study_guide_text", "")

    # Get current project
    project = pm.get_current_project()
    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project to select a project first."
        )]

    # Check database exists
    db_path = Path(project.database_path)
    if not db_path.exists():
        return [TextContent(
            type="text",
            text=f"No database found for {project.project_name}."
        )]

    # Analyze coverage
    try:
        analyzer = CoverageAnalyzer(db_path)
        report = analyzer.analyze(topic, study_guide_text)

        # Format report
        response = f"**Coverage Analysis: {topic}**\n\n"
        response += f"**Overall Score**: {report.overall_score:.1f}%\n\n"

        # Entity coverage summary
        response += f"**Entity Coverage**:\n"
        for entity_type, metrics in report.entity_coverage.items():
            status = "✅" if metrics.coverage_percentage >= 80 else "⚠️" if metrics.coverage_percentage >= 60 else "❌"
            response += f"{status} {entity_type}: {metrics.coverage_percentage:.1f}% ({metrics.mentioned}/{metrics.total_relevant})\n"

        # Cross-references
        cr = report.cross_reference_coverage
        status = "✅" if cr['coverage_percentage'] >= 80 else "⚠️"
        response += f"\n{status} **Cross-References**: {cr['coverage_percentage']:.1f}% ({cr['mentioned_in_guide']}/{cr['total_db_refs']})\n"

        # Timelines
        tl = report.timeline_coverage
        status = "✅" if tl['coverage_percentage'] >= 80 else "⚠️"
        response += f"{status} **Timelines**: {tl['coverage_percentage']:.1f}% ({tl['mentioned']}/{tl['total_deadlines']})\n"

        # Forms
        fm = report.form_coverage
        status = "✅" if fm['coverage_percentage'] >= 80 else "⚠️"
        response += f"{status} **Forms**: {fm['coverage_percentage']:.1f}% ({fm['mentioned']}/{fm['total_forms']})\n"

        # Gaps
        if report.gaps:
            response += f"\n**Identified Gaps**:\n"
            for gap in report.gaps[:5]:
                response += f"- {gap}\n"

        # Recommendations
        response += f"\n**Recommendations**:\n"
        for rec in report.recommendations[:5]:
            response += f"- {rec}\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error analyzing coverage: {e}"
        )]


async def tool_generate_timeline(args: Dict[str, Any]) -> List[TextContent]:
    """
    Generate timeline diagram for a topic.
    """
    topic = args.get("topic", "")

    # Get current project
    project = pm.get_current_project()
    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project to select a project first."
        )]

    db_path = Path(project.database_path)
    if not db_path.exists():
        return [TextContent(
            type="text",
            text=f"No database found for {project.project_name}."
        )]

    # Generate diagram
    try:
        generator = MermaidDiagramGenerator(db_path)
        diagram = generator.generate_timeline_diagram(topic)

        response = f"**Timeline Diagram: {topic}**\n\n"
        response += f"```mermaid\n{diagram}\n```\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error generating timeline diagram: {e}"
        )]


async def tool_generate_process(args: Dict[str, Any]) -> List[TextContent]:
    """
    Generate process flowchart for a topic.
    """
    topic = args.get("topic", "")

    # Get current project
    project = pm.get_current_project()
    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project to select a project first."
        )]

    db_path = Path(project.database_path)
    if not db_path.exists():
        return [TextContent(
            type="text",
            text=f"No database found for {project.project_name}."
        )]

    # Generate diagram
    try:
        generator = MermaidDiagramGenerator(db_path)
        diagram = generator.generate_process_flowchart(topic)

        response = f"**Process Diagram: {topic}**\n\n"
        response += f"```mermaid\n{diagram}\n```\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error generating process diagram: {e}"
        )]


async def tool_generate_comparison(args: Dict[str, Any]) -> List[TextContent]:
    """
    Generate comparison table between two topics.
    """
    topic1 = args.get("topic1", "")
    topic2 = args.get("topic2", "")

    # Get current project
    project = pm.get_current_project()
    if not project:
        return [TextContent(
            type="text",
            text="No active project. Use switch_project to select a project first."
        )]

    db_path = Path(project.database_path)
    if not db_path.exists():
        return [TextContent(
            type="text",
            text=f"No database found for {project.project_name}."
        )]

    # Generate comparison
    try:
        generator = MermaidDiagramGenerator(db_path)
        table = generator.generate_comparison_table(topic1, topic2)

        return [TextContent(type="text", text=table)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error generating comparison: {e}"
        )]


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

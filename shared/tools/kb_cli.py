#!/usr/bin/env python3
"""
Knowledge Base CLI - Command-line interface for project management.

Usage:
    kb projects list                  - List all projects
    kb projects create <name>         - Create new project
    kb projects switch <id>           - Switch to project
    kb projects delete <id>           - Delete project
    kb projects current               - Show current project
"""

import sys
import argparse
from pathlib import Path

# Add shared/src to Python path
shared_dir = Path(__file__).parent.parent
sys.path.insert(0, str(shared_dir / "src"))

from project import ProjectManager
from extraction import SourceManager, ExtractionRunner


def cmd_projects_list(pm: ProjectManager, args):
    """List all projects."""
    projects = pm.list_projects()

    if not projects:
        print("No projects found.")
        print("\nCreate a new project with:")
        print("  kb projects create \"Project Name\" --domain <domain>")
        return

    current = pm.get_current_project()
    current_id = current.project_id if current else None

    print(f"Available projects ({len(projects)}):\n")
    for p in projects:
        active_mark = " (active)" if p.project_id == current_id else ""
        print(f"  {p.project_id}{active_mark}")
        print(f"    Name: {p.project_name}")
        print(f"    Domain: {p.domain}")
        print(f"    Entities: {p.total_entities:,}")
        print(f"    Relationships: {p.total_relationships:,}")
        print(f"    Sources: {p.sources_count}")
        print()


def cmd_projects_current(pm: ProjectManager, args):
    """Show current project."""
    current = pm.get_current_project()

    if not current:
        print("No active project.")
        print("\nSwitch to a project with:")
        print("  kb projects switch <project-id>")
        return

    print(f"Current project: {current.project_name}")
    print(f"  ID: {current.project_id}")
    print(f"  Domain: {current.domain}")
    print(f"  Description: {current.description}")
    print(f"  Database: {current.database_path}")
    print(f"\nStatistics:")
    print(f"  Entities: {current.total_entities:,}")
    print(f"  Relationships: {current.total_relationships:,}")
    print(f"  Sources: {current.sources_count}")
    print(f"  Created: {current.created_at}")


def cmd_projects_create(pm: ProjectManager, args):
    """Create new project."""
    if not args.name:
        print("Error: Project name required")
        print("Usage: kb projects create <name> --domain <domain>")
        return 1

    if not args.domain:
        print("Error: --domain required")
        print("Usage: kb projects create <name> --domain <domain>")
        return 1

    try:
        project = pm.create_project(
            name=args.name,
            domain=args.domain,
            description=args.description or "",
            template=args.template
        )

        print(f"\n✓ Project created successfully!")
        print(f"  ID: {project.project_id}")
        print(f"  Name: {project.project_name}")
        print(f"  Domain: {project.domain}")
        print(f"\nNext steps:")
        print(f"  1. Switch to project: kb projects switch {project.project_id}")
        print(f"  2. Add sources: kb sources add --file <path>")

    except ValueError as e:
        print(f"Error: {e}")
        return 1


def cmd_projects_switch(pm: ProjectManager, args):
    """Switch to a project."""
    if not args.project_id:
        print("Error: Project ID required")
        print("Usage: kb projects switch <project-id>")
        return 1

    try:
        project = pm.switch_to(args.project_id)
        print(f"\n✓ Switched to: {project.project_name}")
        print(f"  Database: {project.database_path}")
        print(f"  Sources: {project.sources_count}")

    except ValueError as e:
        print(f"Error: {e}")
        print("\nAvailable projects:")
        for p in pm.list_projects():
            print(f"  - {p.project_id}")
        return 1


def cmd_projects_delete(pm: ProjectManager, args):
    """Delete a project."""
    if not args.project_id:
        print("Error: Project ID required")
        print("Usage: kb projects delete <project-id> --confirm")
        return 1

    if not args.confirm:
        print(f"⚠️  Warning: This will permanently delete project '{args.project_id}'")
        print("           All data, sources, and configuration will be lost.")
        print("\nTo confirm deletion, run:")
        print(f"  kb projects delete {args.project_id} --confirm")
        return 1

    try:
        pm.delete_project(args.project_id, confirm=True)
        print(f"✓ Project '{args.project_id}' deleted successfully")

    except ValueError as e:
        print(f"Error: {e}")
        return 1


def cmd_extract_add_source(pm: ProjectManager, args):
    """Add source material to current project."""
    current = pm.get_current_project()
    if not current:
        print("Error: No active project. Use 'kb projects switch <id>' first.")
        return 1

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    try:
        source_manager = SourceManager(pm.projects_dir / current.project_id)
        source = source_manager.add_source(
            file_path,
            source_name=args.name,
            source_type=args.type
        )

        print(f"\n✓ Source added successfully!")
        print(f"  ID: {source.source_id}")
        print(f"  Name: {source.source_name}")
        print(f"  Type: {source.source_type}")

    except ValueError as e:
        print(f"Error: {e}")
        return 1


def cmd_extract_list_sources(pm: ProjectManager, args):
    """List all sources in current project."""
    current = pm.get_current_project()
    if not current:
        print("Error: No active project. Use 'kb projects switch <id>' first.")
        return 1

    source_manager = SourceManager(pm.projects_dir / current.project_id)
    sources = source_manager.list_sources()

    if not sources:
        print("No sources found.")
        print("\nAdd a source with:")
        print("  kb extract add-source --file <path>")
        return

    print(f"Sources in {current.project_name} ({len(sources)}):\n")
    for s in sources:
        status = "✓ Extracted" if s.extracted else "⏳ Pending"
        print(f"  {s.source_id} {status}")
        print(f"    Name: {s.source_name}")
        print(f"    Type: {s.source_type}")
        print(f"    Size: {s.file_size:,} characters")
        if s.extracted:
            print(f"    Entities: {s.entity_count:,}")
            print(f"    Relationships: {s.relationship_count:,}")
        print()


def cmd_extract_run(pm: ProjectManager, args):
    """Run extraction on a source."""
    current = pm.get_current_project()
    if not current:
        print("Error: No active project. Use 'kb projects switch <id>' first.")
        return 1

    try:
        runner = ExtractionRunner(
            pm.projects_dir / current.project_id,
            use_mock=args.mock
        )

        if args.source_id:
            # Extract specific source
            result = runner.extract_source(args.source_id)
        else:
            # Extract all unextracted sources
            result = runner.extract_all_sources()

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


def cmd_extract_status(pm: ProjectManager, args):
    """Show extraction status."""
    current = pm.get_current_project()
    if not current:
        print("Error: No active project. Use 'kb projects switch <id>' first.")
        return 1

    source_manager = SourceManager(pm.projects_dir / current.project_id)
    sources = source_manager.list_sources()

    extracted = [s for s in sources if s.extracted]
    pending = [s for s in sources if not s.extracted]

    print(f"\n{'='*70}")
    print(f"EXTRACTION STATUS: {current.project_name}")
    print(f"{'='*70}")
    print(f"\nTotal sources: {len(sources)}")
    print(f"  Extracted: {len(extracted)}")
    print(f"  Pending: {len(pending)}")

    if pending:
        print(f"\nPending sources:")
        for s in pending:
            print(f"  • {s.source_name} ({s.source_id})")

    # Get database statistics
    from extraction import DatabaseLoader
    loader = DatabaseLoader(pm.projects_dir / current.project_id)
    stats = loader.get_statistics()

    print(f"\nDatabase statistics:")
    print(f"  Total entities: {stats['total_entities']:,}")
    print(f"  Total relationships: {stats['total_relationships']:,}")

    if stats['entities_by_category']:
        print(f"\n  Entities by category:")
        for cat, count in stats['entities_by_category'].items():
            print(f"    {cat}: {count:,}")

    print(f"\n{'='*70}\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Knowledge Base CLI - Multi-project management and extraction"
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Projects command
    projects_parser = subparsers.add_parser('projects', help='Project management')
    projects_sub = projects_parser.add_subparsers(dest='subcommand')

    # projects list
    projects_sub.add_parser('list', help='List all projects')

    # projects current
    projects_sub.add_parser('current', help='Show current project')

    # projects create
    create_parser = projects_sub.add_parser('create', help='Create new project')
    create_parser.add_argument('name', nargs='?', help='Project name')
    create_parser.add_argument('--domain', required=False, help='Domain/subject area')
    create_parser.add_argument('--description', help='Project description')
    create_parser.add_argument('--template', help='Schema template to use')

    # projects switch
    switch_parser = projects_sub.add_parser('switch', help='Switch to project')
    switch_parser.add_argument('project_id', nargs='?', help='Project ID')

    # projects delete
    delete_parser = projects_sub.add_parser('delete', help='Delete project')
    delete_parser.add_argument('project_id', nargs='?', help='Project ID')
    delete_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Knowledge extraction')
    extract_sub = extract_parser.add_subparsers(dest='subcommand')

    # extract add-source
    add_source_parser = extract_sub.add_parser('add-source', help='Add source material')
    add_source_parser.add_argument('--file', required=True, help='Path to source file')
    add_source_parser.add_argument('--name', help='Custom source name')
    add_source_parser.add_argument('--type', help='Source type (text, pdf, markdown)')

    # extract list-sources
    extract_sub.add_parser('list-sources', help='List all sources')

    # extract run
    run_parser = extract_sub.add_parser('run', help='Run extraction')
    run_parser.add_argument('--source-id', help='Extract specific source (optional)')
    run_parser.add_argument('--mock', action='store_true', help='Use mock client (testing)')
    run_parser.add_argument('--verbose', action='store_true', help='Verbose output')

    # extract status
    extract_sub.add_parser('status', help='Show extraction status')

    args = parser.parse_args()

    # Initialize ProjectManager
    pm = ProjectManager()

    # Route commands
    if args.command == 'projects':
        if args.subcommand == 'list':
            return cmd_projects_list(pm, args)
        elif args.subcommand == 'current':
            return cmd_projects_current(pm, args)
        elif args.subcommand == 'create':
            return cmd_projects_create(pm, args)
        elif args.subcommand == 'switch':
            return cmd_projects_switch(pm, args)
        elif args.subcommand == 'delete':
            return cmd_projects_delete(pm, args)
        else:
            projects_parser.print_help()
    elif args.command == 'extract':
        if args.subcommand == 'add-source':
            return cmd_extract_add_source(pm, args)
        elif args.subcommand == 'list-sources':
            return cmd_extract_list_sources(pm, args)
        elif args.subcommand == 'run':
            return cmd_extract_run(pm, args)
        elif args.subcommand == 'status':
            return cmd_extract_status(pm, args)
        else:
            extract_parser.print_help()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)

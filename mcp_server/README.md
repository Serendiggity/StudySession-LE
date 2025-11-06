# Universal Knowledge Platform - MCP Server

Knowledge extraction and query server for Claude Desktop and Claude Code.

**Works with any domain**: law, medicine, engineering, and more.
**Example implementation**: Canadian Insolvency Law (first use case)

## Features

### 🔧 Tools (5)

1. **query_knowledge_base** - Query with direct quotes from source material
2. **switch_project** - Switch between knowledge base projects
3. **add_material** - Add PDF/text/markdown sources
4. **extract_knowledge** - Run extraction on sources
5. **get_statistics** - View database statistics

### 📚 Resources

- `project://list` - List all projects
- `project://{id}/schema` - Get project schema
- `bia://section/{N}` - Access BIA sections (when available)

## Installation

### Prerequisites

- Python 3.10+
- Claude Desktop OR Claude Code
- MCP Python SDK

### Install MCP SDK

```bash
pip install mcp
```

### Install Knowledge Platform MCP Server

```bash
# From the repository root
cd insolvency-knowledge
pip install -e ./mcp_server
```

## Configuration

### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "knowledge-platform": {
      "command": "python3",
      "args": [
        "/Users/jeffr/Local Project Repo/insolvency-knowledge/mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/jeffr/Local Project Repo/insolvency-knowledge"
      }
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

### For Claude Code

Add to MCP settings (coming soon - Claude Code MCP support in development)

## Usage

### In Claude Desktop

Once configured, the tools are automatically available. Try:

```
User: "What must the trustee do after filing a notice of intention?"

Claude: [Uses query_knowledge_base tool automatically]
        [Returns answer with direct BIA quote]
```

```
User: "Switch to radiology project"

Claude: [Uses switch_project tool]
        [Confirms switch to radiology knowledge base]
```

```
User: "Add this PDF to the knowledge base"
User: *uploads medical_imaging.pdf*

Claude: [Uses add_material tool]
        [Queues PDF for extraction]
```

### Example Queries

**Query Knowledge**:
- "What are the trustee's duties in a Division I proposal?"
- "What deadlines apply after filing NOI?"
- "Show me all consequences for failing to file"

**Manage Projects**:
- "Switch to insolvency law project"
- "List all available projects"
- "What's in the current database?"

**Add Content**:
- "Add sources/bia_statute.txt to the project"
- "Extract knowledge from pending sources"

## Development

### Run Server Directly

```bash
cd insolvency-knowledge
python3 mcp_server/server.py
```

### Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python3 mcp_server/server.py
```

## Architecture

```
Claude Desktop/Code
       ↓
MCP Server (this package)
       ↓
Project Manager → Projects
       ↓
SQLite Databases (one per project)
```

### Projects

Each project is isolated with its own:
- Database (`projects/{id}/database/knowledge.db`)
- Sources (`projects/{id}/sources/`)
- Schema configuration (`projects/{id}/config.json`)

### Multi-Project Support

```
projects/
├── insolvency-law/     # Legal knowledge
├── radiology/          # Medical imaging
└── software-eng/       # Tech documentation
```

Switch between them with `switch_project` tool.

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. Check config file path is correct
2. Verify Python path in `command`
3. Check logs: `tail -f ~/Library/Logs/Claude/mcp*.log` (macOS)
4. Restart Claude Desktop

### Tool Calls Failing

1. Verify project exists: Use `switch_project` with no args to list
2. Check database exists: Use `get_statistics` to verify
3. Check file paths are absolute
4. View server logs for errors

### No Results from Queries

1. Verify data extracted: `get_statistics` shows counts
2. Check query terms match content
3. Try broader search terms
4. Verify database has relationship_text (critical field)

## Contributing

This MCP server is part of the Universal Knowledge Extraction Platform project.

See `docs/Enhancement-Roadmap.md` for full project vision.

## License

MIT

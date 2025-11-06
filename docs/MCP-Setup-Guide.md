# MCP Server Setup Guide

Complete setup guide for the Universal Knowledge Platform MCP Server in Claude Desktop and Claude Code.

**Works with any domain**: law, medicine, engineering, and more.
**Example repository**: insolvency-knowledge (first implementation)

**Date**: January 5, 2025
**Status**: Phase 5A Complete

---

## 📋 Prerequisites

- Python 3.10 or higher
- Claude Desktop OR Claude Code
- Knowledge Platform repository cloned (insolvency-knowledge)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install MCP SDK

```bash
pip install mcp
```

### Step 2: Verify Installation

```bash
cd /Users/jeffr/Local\ Project\ Repo/insolvency-knowledge
python3 -c "import mcp; print('MCP SDK installed successfully')"
```

### Step 3: Configure Claude Desktop

1. **Find config file location**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Edit config file** (create if doesn't exist):

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

**IMPORTANT**: Replace `/Users/jeffr/Local Project Repo/insolvency-knowledge` with your actual path!

3. **Restart Claude Desktop**

4. **Verify** - Open Claude Desktop, look for tools icon showing MCP servers connected

---

## ✅ Testing the Installation

### Test 1: List Projects

In Claude Desktop, try:

```
User: "List all knowledge base projects"
```

Expected: Claude uses `switch_project` tool and shows available projects.

### Test 2: Get Statistics

```
User: "What's in the insolvency database?"
```

Expected: Claude uses `get_statistics` tool and shows entity/relationship counts.

### Test 3: Query Knowledge

```
User: "What must the trustee do after filing a notice of intention?"
```

Expected: Claude uses `query_knowledge_base` tool and returns answer with direct BIA quote.

---

## 🛠️ Advanced Setup

### Running MCP Server Standalone

For testing/debugging:

```bash
cd /Users/jeffr/Local\ Project\ Repo/insolvency-knowledge
python3 mcp_server/server.py
```

### Remote GitHub Installation

**Can I use the MCP from remote GitHub?** Yes, but with limitations.

**Setup for read-only queries**:

```json
{
  "mcpServers": {
    "knowledge-platform-remote": {
      "command": "python3",
      "args": [
        "-c",
        "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/YOUR_USERNAME/insolvency-knowledge/main/mcp_server/server.py').read().decode())"
      ],
      "env": {
        "PYTHONPATH": "/tmp/knowledge-platform-remote"
      }
    }
  }
}
```

**Prerequisites**:
- `pip install mcp` (must be installed locally)
- Dependencies installed locally
- Internet connection required

**Limitations**:
- ❌ Cannot access local project files (projects/, shared/)
- ❌ Cannot add new sources
- ❌ Cannot run extraction
- ✅ Can query existing databases (if pre-built)
- ✅ Can switch between projects (if databases exist)

**Recommendation**: **Clone locally** for full functionality (extraction, adding sources, progress tracking).

Remote GitHub is suitable for:
- Quick demos
- Read-only queries
- Sharing with others (they get latest code)

Not suitable for:
- Adding new materials
- Running extractions
- Project creation

### Using MCP Inspector

The MCP Inspector provides a web UI for testing:

```bash
npx @modelcontextprotocol/inspector python3 mcp_server/server.py
```

Opens at: `http://localhost:5173`

You can:
- View all tools
- Test tool calls
- Inspect resources
- Debug responses

### Environment Variables

Optional environment variables:

```json
{
  "mcpServers": {
    "knowledge-platform": {
      "command": "python3",
      "args": ["..."],
      "env": {
        "PYTHONPATH": "/path/to/repo",
        "LANG_EXTRACT_API_KEY": "your-api-key",  # For actual extraction
        "GEMINI_API_KEY": "your-api-key"          # For AI analysis
      }
    }
  }
}
```

**Note**: API keys only needed for extraction. Querying works without them.

---

## 🔍 Available Tools

### 1. query_knowledge_base

**Description**: Query the knowledge base with direct quotes

**Parameters**:
- `query` (required): The question to answer
- `project_id` (optional): Specific project to query

**Example Use**:
```
"What are the deadlines for filing a notice of intention?"
"Show me trustee duties related to proposals"
"What happens if the debtor fails to file?"
```

**Auto-Invoked When**: User asks domain-specific questions

---

### 2. switch_project

**Description**: Switch between projects or list available projects

**Parameters**:
- `project_id` (optional): Project to switch to (omit to list all)

**Example Use**:
```
"Switch to radiology project"
"List all projects"
"What projects are available?"
```

**Auto-Invoked When**: User mentions switching or asks about projects

---

### 3. add_material

**Description**: Add source material to current project

**Parameters**:
- `file_path` (required): Path to source file
- `source_name` (optional): Custom name

**Example Use**:
```
"Add sources/bia_statute.txt to the project"
"Add the radiology textbook at ~/Documents/radiology.pdf"
```

**Auto-Invoked When**: User wants to add documents

---

### 4. extract_knowledge

**Description**: Run extraction on unextracted sources

**Parameters**:
- `source_id` (optional): Specific source to extract
- `use_mock` (optional): Use mock extraction for testing

**Example Use**:
```
"Extract knowledge from pending sources"
"Run extraction with mock mode"
```

**Auto-Invoked When**: User requests extraction

---

### 5. get_statistics

**Description**: Get database statistics

**Parameters**:
- `project_id` (optional): Specific project (defaults to current)

**Example Use**:
```
"What's in the database?"
"Show me statistics for the insolvency project"
"How much data do we have?"
```

**Auto-Invoked When**: User asks about database contents

---

## 📚 Available Resources

### project://list

Lists all projects in JSON format.

**Access**: Read via MCP resource protocol

### project://{id}/schema

Get entity schema for a specific project.

**Example**: `project://insolvency-law/schema`

### bia://section/{N}

Access specific BIA section (when available).

**Example**: `bia://section/50.4`

**Note**: Currently returns stub data. Full BIA integration coming in Phase 5B.

---

## 🐛 Troubleshooting

### Server Not Showing in Claude Desktop

**Symptoms**: No tools icon, can't access tools

**Solutions**:

1. **Check Config Path**:
   ```bash
   # macOS
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Check Python Path**:
   ```bash
   which python3
   # Use this path in config "command"
   ```

3. **Check Logs**:
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log

   # Windows
   # Check Event Viewer or Claude logs directory
   ```

4. **Verify Server Runs**:
   ```bash
   python3 mcp_server/server.py
   # Should not error
   ```

5. **Restart Claude Desktop** (important!)

---

### Tool Calls Failing

**Symptoms**: Error messages when using tools

**Solutions**:

1. **Check Project Exists**:
   ```
   User: "List all projects"
   # Verify project shown
   ```

2. **Check Database Exists**:
   ```bash
   ls projects/insolvency-law/database/knowledge.db
   # Should exist if extraction run
   ```

3. **Verify PYTHONPATH**:
   ```bash
   # In server.py logs, check imports work
   ```

4. **Check Absolute Paths**:
   - All paths in config must be absolute
   - No `~` or `../` allowed

---

### No Query Results

**Symptoms**: `query_knowledge_base` returns "No results"

**Solutions**:

1. **Check Data Exists**:
   ```
   User: "What's in the database?"
   # Verify entities/relationships > 0
   ```

2. **Run Extraction First**:
   ```bash
   python3 shared/tools/kb_cli.py extract run --mock
   ```

3. **Verify relationship_text Field**:
   - This field MUST exist for queries to work
   - Automatically created by DatabaseLoader

4. **Try Broader Query**:
   ```
   # Instead of: "What is section 50.4(1)(a)"
   # Try: "trustee duties"
   ```

---

### Permission Errors

**Symptoms**: "Permission denied" errors

**Solutions**:

1. **Check File Ownership**:
   ```bash
   ls -la mcp_server/server.py
   # Verify you own the file
   ```

2. **Make Executable** (optional):
   ```bash
   chmod +x mcp_server/server.py
   ```

3. **Check Directory Permissions**:
   ```bash
   ls -la projects/
   # Verify write permissions
   ```

---

## 🎯 Usage Examples

### Scenario 1: Query Existing Knowledge

```
User: "I'm studying for my insolvency exam.
       What are the trustee's duties after an NOI?"

Claude: [Uses query_knowledge_base]
        [Returns]:

        **Query**: trustee duties after NOI
        **Project**: Insolvency Law

        **Found 3 result(s)**:

        1. **Duty Relationships**
        ```
        The trustee shall, within 10 days after the filing
        of a notice of intention under subsection 50.4(1),
        prepare a statement of affairs...
        ```
        *Source: bia-statute*
```

---

### Scenario 2: Switch Projects

```
User: "I want to look at radiology information now"

Claude: [Uses switch_project with project_id="radiology"]
        [Returns]:

        **Switched to**: Radiology
        - Domain: medicine
        - Entities: 523
        - Relationships: 145
        - Sources: 2
```

---

### Scenario 3: Add New Material

```
User: "I have a new OSB directive PDF at ~/Downloads/directive_24.pdf
       Can you add it to the knowledge base?"

Claude: [Uses add_material with file_path="~/Downloads/directive_24.pdf"]
        [Returns]:

        **Source Added Successfully!**
        - ID: directive-24
        - Name: Directive 24
        - Type: pdf
        - Size: 45,231 characters

        Use `extract_knowledge` to extract knowledge from this source.

User: "Go ahead and extract it"

Claude: [Uses extract_knowledge with use_mock=false]
        [Shows progress, then returns]:

        **Extraction Complete!**
        - Entities extracted: 89
        - Relationships extracted: 23
```

---

## 📊 Performance

**Tool Response Times** (typical):

- `switch_project`: <100ms
- `get_statistics`: <200ms
- `query_knowledge_base`: 200-500ms (depends on DB size)
- `add_material`: <1s (file copy)
- `extract_knowledge`: 30s-5min (depends on content size and API)

**Memory Usage**:

- MCP Server: ~50MB idle
- During extraction: ~200MB
- With large DBs (10K+ entities): ~100MB

---

## 🔐 Security Notes

### Data Privacy

- All data stored locally in SQLite databases
- No data sent to external servers (except Lang Extract API during extraction)
- MCP server runs locally (not networked)

### API Keys

- Store in environment variables (not in config files)
- Only needed for extraction (not for querying)
- Not logged or transmitted

### File Access

- Server has access to repository directory only
- Cannot access files outside repository (unless explicitly path provided)

---

## 🚀 Next Steps

### After Setup

1. **Test with existing project**:
   ```
   "What's in the insolvency database?"
   ```

2. **Create new project** (Phase 2 workflow):
   ```bash
   python3 shared/tools/analyze_and_create_project.py \
     --file data/test_materials/radiology_sample.txt \
     --name "Test Radiology" \
     --domain medicine
   ```

3. **Query new project** via MCP:
   ```
   "Switch to test-radiology project"
   "What imaging methods are mentioned?"
   ```

### Coming in Phase 5B: Claude Skills

After MCP server is stable, we'll add:
- `knowledge-extraction` skill (automatic schema suggestion)
- `multi-project-query` skill (intelligent project switching)
- `exam-quiz-generator` skill (practice question generation)

These will provide **automatic workflows** on top of MCP tools.

---

## 📞 Support

### Debugging

**Enable verbose logging**:
```json
{
  "mcpServers": {
    "knowledge-platform": {
      "command": "python3",
      "args": ["-u", "/path/to/server.py"],  # -u for unbuffered
      "env": {
        "PYTHONPATH": "/path/to/repo",
        "PYTHON_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**View logs**:
- macOS: `~/Library/Logs/Claude/mcp-server-knowledge-platform.log`
- Windows: Event Viewer or Claude logs directory
- Linux: Check `.xsession-errors` or systemd journal

### Getting Help

1. Check this guide first
2. Review MCP server README: `mcp_server/README.md`
3. Check Phase 5A completion doc: `docs/Phase5A-Complete.md`
4. Open GitHub issue with:
   - OS and Claude version
   - Error messages from logs
   - Steps to reproduce

---

## ✅ Checklist

Before reporting issues, verify:

- [ ] MCP SDK installed (`pip install mcp`)
- [ ] Config file path correct for your OS
- [ ] Absolute paths used (no `~` or `../`)
- [ ] Python 3.10+ (`python3 --version`)
- [ ] Claude Desktop restarted after config change
- [ ] Server runs standalone (`python3 mcp_server/server.py`)
- [ ] Project exists (use `switch_project` to list)
- [ ] Database exists (check `projects/{id}/database/knowledge.db`)

---

**Setup Complete!** 🎉

You now have a working MCP server for the Universal Knowledge Extraction Platform.

Next: Try queries in Claude Desktop and explore the tools!

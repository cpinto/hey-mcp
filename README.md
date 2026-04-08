# hey-mcp

MCP server that gives Claude full access to [HEY](https://hey.com) email, calendars, todos, habits, time tracking, and journal. Built on [FastMCP](https://github.com/jlowin/fastmcp), it wraps the [hey-cli](https://github.com/cpinto/hey-cli) command-line tool.

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** package manager
- **[hey-cli](https://github.com/cpinto/hey-cli)** installed and authenticated

### Install uv

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install and authenticate hey-cli

Follow the [hey-cli installation instructions](https://github.com/cpinto/hey-cli#installation), then authenticate:

```sh
hey auth login
```

## Installation

```sh
git clone https://github.com/cpinto/hey-mcp.git
cd hey-mcp
uv sync
```

## Configuration

### Claude Desktop

Add the following to your `claude_desktop_config.json` (on macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "hey": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/hey-mcp", "run", "main.py"]
    }
  }
}
```

Replace `/absolute/path/to/hey-mcp` with the actual path where you cloned the repo.

### Claude Code

Add the same config to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "hey": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/hey-mcp", "run", "main.py"]
    }
  }
}
```

## Installing the Skill

The repo includes a `SKILL.md` file that teaches Claude Code when and how to use the HEY MCP tools. To install it:

```sh
mkdir -p ~/.claude/skills/hey
cp SKILL.md ~/.claude/skills/hey/SKILL.md
```

Or symlink it so updates pull automatically:

```sh
mkdir -p ~/.claude/skills/hey
ln -sf "$(pwd)/SKILL.md" ~/.claude/skills/hey/SKILL.md
```

Once installed, Claude Code will automatically invoke the HEY tools when you mention emails, todos, calendar, journal, etc.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_boxes` | List all HEY mailboxes |
| `list_postings` | List emails in a mailbox |
| `read_thread` | Read a full email thread |
| `compose_email` | Compose and send a new email |
| `reply_to_thread` | Reply to an email thread |
| `list_drafts` | List email drafts |
| `mark_seen` | Mark postings as seen |
| `mark_unseen` | Mark postings as unseen |
| `list_calendars` | List all HEY calendars |
| `list_recordings` | List calendar events, todos, habits |
| `create_event` | Create a calendar event |
| `update_event` | Update a calendar event |
| `delete_event` | Delete a calendar event |
| `list_todos` | List all todos |
| `add_todo` | Create a new todo |
| `complete_todo` | Mark a todo as complete |
| `uncomplete_todo` | Mark a todo as incomplete |
| `delete_todo` | Delete a todo |
| `complete_habit` | Mark a habit as complete |
| `uncomplete_habit` | Remove a habit completion |
| `timetrack_start` | Start time tracking |
| `timetrack_stop` | Stop time tracking |
| `timetrack_current` | Show current timer status |
| `timetrack_list` | List time tracking entries |
| `journal_list` | List journal entries |
| `journal_read` | Read a journal entry |
| `journal_write` | Write or edit a journal entry |

## License

MIT

---
name: hey
description: |
  Interact with HEY email via the HEY MCP server. Read and send emails, manage boxes,
  calendars, todos, habits, time tracking, and journal entries. Use for ANY
  HEY-related question or action.
triggers:
  # Direct invocations
  - hey
  - /hey
  # Email actions
  - hey boxes
  - hey box
  - hey threads
  - hey reply
  - hey compose
  - hey drafts
  # Calendar actions
  - hey calendars
  - hey recordings
  # Todos
  - hey todo
  # Seen/unseen
  - hey seen
  - hey unseen
  - mark as read
  - mark as seen
  - mark as unseen
  - mark as unread
  # Habits
  - hey habit
  # Time tracking
  - hey timetrack
  # Journal
  - hey journal
  # Common actions
  - check my email
  - read email
  - send email
  - reply to email
  - compose email
  - list mailboxes
  - check calendar
  - add todo
  - complete todo
  - track time
  - write journal
  # Questions
  - can I hey
  - how do I hey
  - what's in hey
  - what hey
  - does hey
  # My work
  - my emails
  - my inbox
  - my imbox
  - my todos
  - my calendar
  - my journal
  # URLs
  - hey.com
invocable: true
argument-hint: "[command] [args...]"
---

# /hey - HEY Email via MCP

Interact with HEY email using MCP tools from the `hey` MCP server. All tools return structured JSON.

## Agent Invariants

**MUST follow these rules:**

1. **Always use MCP tools** — never shell out to the `hey` CLI directly
2. **Use `mcp__hey__*` tool names** — all tools are prefixed with `mcp__hey__`
3. **Authentication** is handled by the CLI on the host machine — if tools return auth errors, ask the user to run `hey auth login` in their terminal

## Quick Reference

| Task | MCP Tool | Key Parameters |
|------|----------|----------------|
| List mailboxes | `list_boxes` | — |
| List emails in a box | `list_postings` | `box`, `limit` |
| Read email thread | `read_thread` | `thread_id` |
| Reply to email | `reply_to_thread` | `thread_id`, `message` |
| Compose email | `compose_email` | `to`, `subject`, `message`, `cc`, `bcc`, `thread_id` |
| List drafts | `list_drafts` | `limit` |
| Mark as seen | `mark_seen` | `posting_ids` (list) |
| Mark as unseen | `mark_unseen` | `posting_ids` (list) |
| List calendars | `list_calendars` | — |
| List calendar events | `list_recordings` | `calendar_id`, `starts_on`, `ends_on`, `limit` |
| List todos | `list_todos` | `limit` |
| Add todo | `add_todo` | `title`, `date` |
| Complete todo | `complete_todo` | `todo_id` |
| Uncomplete todo | `uncomplete_todo` | `todo_id` |
| Delete todo | `delete_todo` | `todo_id` |
| Complete habit | `complete_habit` | `habit_id`, `date` |
| Uncomplete habit | `uncomplete_habit` | `habit_id`, `date` |
| Start time tracking | `timetrack_start` | — |
| Stop time tracking | `timetrack_stop` | — |
| Current timer | `timetrack_current` | — |
| List time entries | `timetrack_list` | `limit` |
| List journal entries | `journal_list` | — |
| Read journal entry | `journal_read` | `date` |
| Write journal entry | `journal_write` | `content`, `date` |

## Decision Trees

### Reading Email

```
Want to read email?
├── Which mailbox? → list_boxes
├── List emails in box? → list_postings(box="imbox")
├── Read full thread? → read_thread(thread_id="...")
├── Mark as seen? → mark_seen(posting_ids=["12345"])
└── Mark as unseen? → mark_unseen(posting_ids=["12345"])
```

### Sending Email

```
Want to send email?
├── Reply to thread? → reply_to_thread(thread_id="...", message="...")
├── Compose new? → compose_email(to="...", subject="...", message="...")
│   └── With CC/BCC? → compose_email(to="...", subject="...", message="...", cc="...", bcc="...")
└── Check drafts? → list_drafts()
```

### Managing Todos

```
Want to manage todos?
├── List todos? → list_todos()
├── Add todo? → add_todo(title="...", date="YYYY-MM-DD")
├── Complete? → complete_todo(todo_id="...")
├── Uncomplete? → uncomplete_todo(todo_id="...")
└── Delete? → delete_todo(todo_id="...")
```

## Response Format Notes

### Email Postings
`list_postings` returns `{"box": {...}, "postings": [...]}`. Each posting has: `id` (posting ID), `topic_id` (topic ID), `name` (subject), `seen` (read status), `created_at`, `contacts`, `summary`, `app_url`. Use `topic_id` for `read_thread` and `reply_to_thread`.

### Thread IDs vs Posting IDs
- `read_thread` and `reply_to_thread` expect **topic_id** (from the `topic_id` field)
- `mark_seen` and `mark_unseen` expect **posting IDs** (from the `id` field)

### Box Names
Valid box names: `imbox`, `feedbox`, `trailbox`, `asidebox`, `laterbox`, `bubblebox`

### Calendar Recordings
`list_recordings` returns recordings grouped by type (e.g. `{"Calendar::Event": [...], "Calendar::Habit": [...], "Calendar::Todo": [...]}`). Each recording has: `id`, `title`, `starts_at`, `ends_at`, `all_day`, `recurring`. Habit IDs for `complete_habit` come from here.

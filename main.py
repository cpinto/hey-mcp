import json
import subprocess
import signal
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

HEY = "/opt/homebrew/bin/hey"

mcp = FastMCP("hey")


def run_hey(*args: str) -> dict[str, Any] | list[Any] | str:
    """Run a hey-cli command with --json and return parsed output."""
    cmd = [HEY, *args, "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return {"error": True, "stderr": result.stderr.strip(), "stdout": result.stdout.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()


# ── Email ──────────────────────────────────────────────────────────────

@mcp.tool()
def list_boxes() -> Any:
    """List all HEY mailboxes (imbox, feedbox, etc.)."""
    return run_hey("boxes")


@mcp.tool()
def list_postings(box: str, limit: int | None = None) -> Any:
    """List postings (emails) in a mailbox.

    Args:
        box: Mailbox name (imbox, feedbox, etc.) or numeric ID
        limit: Maximum number of postings to return
    """
    args = ["box", box]
    if limit:
        args.extend(["--limit", str(limit)])
    return run_hey(*args)


@mcp.tool()
def read_thread(thread_id: str) -> Any:
    """Read a full email thread.

    Args:
        thread_id: The thread/posting ID to read
    """
    return run_hey("threads", thread_id)


@mcp.tool()
def compose_email(
    to: str,
    subject: str,
    message: str,
    cc: str | None = None,
    bcc: str | None = None,
    thread_id: str | None = None,
) -> Any:
    """Compose and send a new email.

    Args:
        to: Recipient email address(es), comma-separated for multiple
        subject: Message subject
        message: Message body
        cc: CC recipient email address(es), comma-separated for multiple
        bcc: BCC recipient email address(es), comma-separated for multiple
        thread_id: Optional thread ID to post message to (for existing threads)
    """
    args = ["compose", "--to", to, "--subject", subject, "-m", message]
    if cc:
        args.extend(["--cc", cc])
    if bcc:
        args.extend(["--bcc", bcc])
    if thread_id:
        args.extend(["--thread-id", thread_id])
    return run_hey(*args)


@mcp.tool()
def reply_to_thread(thread_id: str, message: str) -> Any:
    """Reply to an email thread.

    Args:
        thread_id: The thread ID to reply to
        message: Reply message body
    """
    return run_hey("reply", thread_id, "-m", message)


@mcp.tool()
def list_drafts(limit: int | None = None) -> Any:
    """List email drafts.

    Args:
        limit: Maximum number of drafts to return
    """
    args = ["drafts"]
    if limit:
        args.extend(["--limit", str(limit)])
    return run_hey(*args)


@mcp.tool()
def mark_seen(posting_ids: list[str]) -> Any:
    """Mark postings as seen.

    Args:
        posting_ids: List of posting IDs to mark as seen
    """
    return run_hey("seen", *posting_ids)


@mcp.tool()
def mark_unseen(posting_ids: list[str]) -> Any:
    """Mark postings as unseen.

    Args:
        posting_ids: List of posting IDs to mark as unseen
    """
    return run_hey("unseen", *posting_ids)


# ── Calendars ──────────────────────────────────────────────────────────

@mcp.tool()
def list_calendars() -> Any:
    """List all HEY calendars."""
    return run_hey("calendars")


@mcp.tool()
def list_recordings(
    calendar_id: str,
    starts_on: str | None = None,
    ends_on: str | None = None,
    limit: int | None = None,
) -> Any:
    """List recordings (events, todos, etc.) for a calendar.

    Args:
        calendar_id: Calendar ID
        starts_on: Start date (YYYY-MM-DD, defaults to today)
        ends_on: End date (YYYY-MM-DD, defaults to 30 days from starts_on)
        limit: Maximum number of recordings per type
    """
    args = ["recordings", calendar_id]
    if starts_on:
        args.extend(["--starts-on", starts_on])
    if ends_on:
        args.extend(["--ends-on", ends_on])
    if limit:
        args.extend(["--limit", str(limit)])
    return run_hey(*args)


# ── Calendar Events ───────────────────────────────────────────────────

@mcp.tool()
def create_event(
    calendar_id: str,
    title: str,
    starts_at: str,
    all_day: bool = False,
    ends_at: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    timezone: str | None = None,
    reminders: list[str] | None = None,
) -> Any:
    """Create a calendar event.

    Args:
        calendar_id: Calendar ID (from list_calendars)
        title: Event title
        starts_at: Start date (YYYY-MM-DD)
        all_day: Whether this is an all-day event
        ends_at: End date (YYYY-MM-DD, defaults to starts_at)
        start_time: Start time (HH:MM, required for timed events)
        end_time: End time (HH:MM, required for timed events)
        timezone: IANA timezone (e.g. America/New_York, required for timed events)
        reminders: List of reminder durations before event (e.g. ["15m", "1h"])
    """
    args = ["event", "create", "-t", title, "--calendar-id", calendar_id, "--starts-at", starts_at]
    if all_day:
        args.append("--all-day")
    if ends_at:
        args.extend(["--ends-at", ends_at])
    if start_time:
        args.extend(["--start-time", start_time])
    if end_time:
        args.extend(["--end-time", end_time])
    if timezone:
        args.extend(["--timezone", timezone])
    if reminders:
        for r in reminders:
            args.extend(["--reminder", r])
    return run_hey(*args)


@mcp.tool()
def update_event(
    event_id: str,
    title: str | None = None,
    starts_at: str | None = None,
    ends_at: str | None = None,
    all_day: bool | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    timezone: str | None = None,
    reminders: list[str] | None = None,
) -> Any:
    """Update a calendar event. Only provided fields are changed.

    Args:
        event_id: Event ID to update
        title: New event title
        starts_at: New start date (YYYY-MM-DD)
        ends_at: New end date (YYYY-MM-DD)
        all_day: Set to true for all-day, false for timed
        start_time: New start time (HH:MM)
        end_time: New end time (HH:MM)
        timezone: New IANA timezone (e.g. America/New_York)
        reminders: New list of reminder durations (e.g. ["15m", "1h"])
    """
    args = ["event", "update", event_id]
    if title is not None:
        args.extend(["--title", title])
    if starts_at is not None:
        args.extend(["--starts-at", starts_at])
    if ends_at is not None:
        args.extend(["--ends-at", ends_at])
    if all_day is not None:
        args.append(f"--all-day={str(all_day).lower()}")
    if start_time is not None:
        args.extend(["--start-time", start_time])
    if end_time is not None:
        args.extend(["--end-time", end_time])
    if timezone is not None:
        args.extend(["--timezone", timezone])
    if reminders is not None:
        for r in reminders:
            args.extend(["--reminder", r])
    return run_hey(*args)


@mcp.tool()
def delete_event(event_id: str) -> Any:
    """Delete a calendar event.

    Args:
        event_id: Event ID to delete
    """
    return run_hey("event", "delete", event_id)


# ── Todos ──────────────────────────────────────────────────────────────

@mcp.tool()
def list_todos(limit: int | None = None) -> Any:
    """List all todos.

    Args:
        limit: Maximum number of todos to return
    """
    args = ["todo", "list"]
    if limit:
        args.extend(["--limit", str(limit)])
    return run_hey(*args)


@mcp.tool()
def add_todo(title: str, date: str | None = None) -> Any:
    """Create a new todo.

    Args:
        title: Todo title
        date: Optional due date (YYYY-MM-DD)
    """
    args = ["todo", "add", "-t", title]
    if date:
        args.extend(["--date", date])
    return run_hey(*args)


@mcp.tool()
def complete_todo(todo_id: str) -> Any:
    """Mark a todo as complete.

    Args:
        todo_id: The todo ID to complete
    """
    return run_hey("todo", "complete", todo_id)


@mcp.tool()
def uncomplete_todo(todo_id: str) -> Any:
    """Mark a todo as incomplete.

    Args:
        todo_id: The todo ID to mark incomplete
    """
    return run_hey("todo", "uncomplete", todo_id)


@mcp.tool()
def delete_todo(todo_id: str) -> Any:
    """Delete a todo.

    Args:
        todo_id: The todo ID to delete
    """
    return run_hey("todo", "delete", todo_id)


# ── Habits ─────────────────────────────────────────────────────────────

@mcp.tool()
def complete_habit(habit_id: str, date: str | None = None) -> Any:
    """Mark a habit as complete for a date.

    Args:
        habit_id: The habit ID
        date: Date (YYYY-MM-DD, defaults to today)
    """
    args = ["habit", "complete", habit_id]
    if date:
        args.extend(["--date", date])
    return run_hey(*args)


@mcp.tool()
def uncomplete_habit(habit_id: str, date: str | None = None) -> Any:
    """Remove a habit completion for a date.

    Args:
        habit_id: The habit ID
        date: Date (YYYY-MM-DD, defaults to today)
    """
    args = ["habit", "uncomplete", habit_id]
    if date:
        args.extend(["--date", date])
    return run_hey(*args)


# ── Time Tracking ──────────────────────────────────────────────────────

@mcp.tool()
def timetrack_start() -> Any:
    """Start time tracking."""
    return run_hey("timetrack", "start")


@mcp.tool()
def timetrack_stop() -> Any:
    """Stop time tracking."""
    return run_hey("timetrack", "stop")


@mcp.tool()
def timetrack_current() -> Any:
    """Show current time tracking status."""
    return run_hey("timetrack", "current")


@mcp.tool()
def timetrack_list(limit: int | None = None) -> Any:
    """List time tracks.

    Args:
        limit: Maximum number of tracks to return
    """
    args = ["timetrack", "list"]
    if limit:
        args.extend(["--limit", str(limit)])
    return run_hey(*args)


# ── Journal ────────────────────────────────────────────────────────────

@mcp.tool()
def journal_list() -> Any:
    """List journal entries."""
    return run_hey("journal", "list")


@mcp.tool()
def journal_read(date: str | None = None) -> Any:
    """Read a journal entry.

    Args:
        date: Date to read (YYYY-MM-DD, defaults to today)
    """
    args = ["journal", "read"]
    if date:
        args.append(date)
    return run_hey(*args)


@mcp.tool()
def journal_write(content: str, date: str | None = None) -> Any:
    """Write or edit a journal entry.

    Args:
        content: Journal content
        date: Date to write (YYYY-MM-DD, defaults to today)
    """
    args = ["journal", "write"]
    if date:
        args.append(date)
    args.extend(["-c", content])
    return run_hey(*args)


def shutdown_handler(signum, frame):
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    mcp.run(transport="stdio")

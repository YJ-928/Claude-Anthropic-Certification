"""
tools.py — Real Python functions that the Reminder Agent can invoke.

Functions:
  get_current_datetime()           → current ISO timestamp
  add_duration_to_datetime(...)    → add minutes/hours/days to a datetime
  set_reminder(...)                → "schedule" a reminder (in-memory store)
"""
from datetime import datetime, timedelta

# ── In-memory reminder store ──────────────────────────────────────────────────
# Maps reminder_id → dict with title, remind_at, message
_reminders: dict[str, dict] = {}
_counter = 0


def get_current_datetime() -> str:
    """Return the current local date and time as an ISO-8601 string."""
    return datetime.now().isoformat(timespec="seconds")


def add_duration_to_datetime(
    base_datetime: str,
    minutes: int = 0,
    hours: int = 0,
    days: int = 0,
) -> str:
    """
    Add a duration to a given datetime string and return the result.

    Args:
        base_datetime: ISO-8601 datetime string (e.g. "2024-03-15T10:30:00")
        minutes: Minutes to add (may be negative)
        hours:   Hours to add (may be negative)
        days:    Days to add (may be negative)

    Returns:
        New datetime as ISO-8601 string.
    """
    try:
        dt = datetime.fromisoformat(base_datetime)
    except ValueError as e:
        return f"Error parsing datetime: {e}"

    delta = timedelta(minutes=minutes, hours=hours, days=days)
    return (dt + delta).isoformat(timespec="seconds")


def set_reminder(
    title: str,
    remind_at: str,
    message: str = "",
) -> str:
    """
    Schedule a reminder at a specific datetime.

    Args:
        title:     Short name for the reminder.
        remind_at: ISO-8601 datetime when to trigger the reminder.
        message:   Optional longer description / note.

    Returns:
        A confirmation string with the assigned reminder ID.
    """
    global _counter
    _counter += 1
    reminder_id = f"REM-{_counter:04d}"

    _reminders[reminder_id] = {
        "title":     title,
        "remind_at": remind_at,
        "message":   message,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    return (
        f"Reminder '{title}' scheduled for {remind_at}. "
        f"ID: {reminder_id}"
    )


def list_reminders() -> str:
    """Return a formatted list of all current reminders."""
    if not _reminders:
        return "No reminders set."
    lines = []
    for rid, r in sorted(_reminders.items()):
        lines.append(f"  {rid}: [{r['remind_at']}] {r['title']}")
        if r["message"]:
            lines.append(f"        Note: {r['message']}")
    return "\n".join(lines)

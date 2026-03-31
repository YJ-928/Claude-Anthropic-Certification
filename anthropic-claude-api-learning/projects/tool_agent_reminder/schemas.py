"""
schemas.py — JSON tool schemas for the Reminder Agent.

Each schema follows the Anthropic tool definition format:
{
    "name":          str,
    "description":   str,
    "input_schema":  dict   (JSON Schema)
}
"""

TOOL_SCHEMAS = [
    {
        "name": "get_current_datetime",
        "description": (
            "Return the current local date and time as an ISO-8601 string. "
            "Always call this first when the user provides relative time references "
            "like 'in 30 minutes' or 'tomorrow morning'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "add_duration_to_datetime",
        "description": (
            "Add a duration (minutes, hours, and/or days) to a given datetime "
            "and return the resulting datetime string. Use this to convert relative "
            "time expressions into absolute datetime values before calling set_reminder."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "base_datetime": {
                    "type": "string",
                    "description": "ISO-8601 datetime string to start from.",
                },
                "minutes": {
                    "type": "integer",
                    "description": "Minutes to add (can be negative). Default 0.",
                    "default": 0,
                },
                "hours": {
                    "type": "integer",
                    "description": "Hours to add (can be negative). Default 0.",
                    "default": 0,
                },
                "days": {
                    "type": "integer",
                    "description": "Days to add (can be negative). Default 0.",
                    "default": 0,
                },
            },
            "required": ["base_datetime"],
        },
    },
    {
        "name": "set_reminder",
        "description": (
            "Schedule a reminder at a specific datetime. Use absolute ISO-8601 "
            "datetime strings only — never relative expressions. Returns a "
            "confirmation with the reminder ID."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short title for the reminder (e.g. 'Team standup').",
                },
                "remind_at": {
                    "type": "string",
                    "description": "ISO-8601 datetime when the reminder should trigger.",
                },
                "message": {
                    "type": "string",
                    "description": "Optional longer note or description. Default empty.",
                    "default": "",
                },
            },
            "required": ["title", "remind_at"],
        },
    },
]

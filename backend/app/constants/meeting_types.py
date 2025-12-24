"""Meeting type multipliers based on tech_task.md lines 28-35."""

MEETING_MULTIPLIERS = {
    "brainstorm": {
        "moderator": 1.5,
        "ideologue": 1.5,
        "harmonizer": 1.3,
        "critic": 0.5,
        "time_manager": 0.7,
        "speaker": 1.0,
        "mediator": 1.0,
    },
    "review": {
        "moderator": 1.4,
        "critic": 1.5,
        "mediator": 1.3,
        "ideologue": 0.6,
        "speaker": 0.8,
        "time_manager": 1.0,
        "harmonizer": 1.0,
    },
    "planning": {
        "moderator": 1.3,
        "time_manager": 1.4,
        "critic": 1.2,
        "harmonizer": 0.8,
        "speaker": 1.0,
        "ideologue": 1.0,
        "mediator": 1.0,
    },
    "status_update": {
        "speaker": 1.4,
        "time_manager": 1.5,
        "moderator": 1.2,
        "ideologue": 0.5,
        "mediator": 0.6,
        "critic": 1.0,
        "harmonizer": 1.0,
    },
}

VALID_MEETING_TYPES = list(MEETING_MULTIPLIERS.keys())

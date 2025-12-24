"""Role requirements matrix based on tech_task.md lines 11-19."""

ROLE_REQUIREMENTS = {
    "moderator": {
        "ei_min": 75,
        "ei_max": 100,
        "si_min": 75,
        "si_max": 100,
        "energy_min": 70,
        "energy_max": 100,
    },
    "speaker": {
        "ei_min": 60,
        "ei_max": 85,
        "si_min": 75,
        "si_max": 100,
        "energy_min": 80,
        "energy_max": 100,
    },
    "time_manager": {
        "ei_min": 50,
        "ei_max": 75,
        "si_min": 30,
        "si_max": 60,
        "energy_min": 60,
        "energy_max": 90,
    },
    "critic": {
        "ei_min": 60,
        "ei_max": 85,
        "si_min": 50,
        "si_max": 75,
        "energy_min": 40,
        "energy_max": 70,
    },
    "ideologue": {
        "ei_min": 50,
        "ei_max": 75,
        "si_min": 60,
        "si_max": 85,
        "energy_min": 75,
        "energy_max": 100,
    },
    "mediator": {
        "ei_min": 80,
        "ei_max": 100,
        "si_min": 70,
        "si_max": 95,
        "energy_min": 65,
        "energy_max": 90,
    },
    "harmonizer": {
        "ei_min": 70,
        "ei_max": 95,
        "si_min": 75,
        "si_max": 100,
        "energy_min": 60,
        "energy_max": 85,
    },
}

ALL_ROLES = list(ROLE_REQUIREMENTS.keys())

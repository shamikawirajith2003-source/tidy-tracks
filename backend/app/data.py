"""Static data: map stops, collection zones and demo accounts (no database access)."""

STOPS = [
    (140, 300, "Temple Rd"), (230, 345, "Market Jn"), (330, 300, "School Ln"),
    (430, 345, "Bus Stand"), (520, 300, "Lake Rd"), (520, 215, "Hospital Rd"),
    (410, 215, "Park Ave"), (300, 215, "Clock Tower"), (140, 215, "Station Rd"),
    (140, 105, "Canal St"), (300, 105, "Library Rd"), (410, 105, "Beach Rd"),
]
ZONES = [
    (1, "Zone 1: Temple Rd to Bus Stand", "Mon"),
    (2, "Zone 2: Lake Rd to Clock Tower", "Tue"),
    (3, "Zone 3: Station Rd to Beach Rd", "Thu"),
]
DEMO_USERS = [
    {"name": "A. Perera", "email": "a.perera@example.lk", "role": "resident", "phone": "077 100 2001", "stop": 7},
    {"name": "N. Fernando", "email": "n.fernando@example.lk", "role": "resident", "phone": "071 100 2002", "stop": 3},
    {"name": "K. Silva", "email": "k.silva@example.lk", "role": "driver", "phone": "070 100 2003", "vehicle": "WP LK-4821"},
    {"name": "R. Jayasinghe", "email": "r.jayasinghe@example.lk", "role": "driver", "phone": "076 100 2004", "vehicle": "WP LK-3307"},
]
DEMO_PASSWORD = "demo123"

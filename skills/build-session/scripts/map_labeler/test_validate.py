from validate_catalog import validate_map_entry

VALID_ENTRY = {
    "id": "fraif/warehouse",
    "name": "Warehouse",
    "source": "fraif",
    "type": "dungeon",
    "image_dm": "maps/fraif/map-01.016-warehouse-dm.jpg",
    "image_player": "maps/fraif/map-01.016-warehouse-player.jpg",
    "image_size": [4096, 2650],
    "rooms": [
        {"id": "A1", "name": "Main Hall", "x": 3300, "y": 1350, "tags": ["large"]},
        {"id": "A2", "name": "Entrance", "x": 700, "y": 1850, "tags": ["entrance"]},
    ],
    "connections": [
        {"from": "A2", "to": "A1", "type": "door"},
    ],
}

def test_valid_entry_passes():
    errors = validate_map_entry(VALID_ENTRY)
    assert errors == []

def test_missing_entrance_tag():
    entry = {**VALID_ENTRY, "rooms": [
        {"id": "A1", "name": "Hall", "x": 100, "y": 100, "tags": ["large"]},
    ], "connections": []}
    errors = validate_map_entry(entry)
    assert any("entrance" in e for e in errors)

def test_room_out_of_bounds():
    entry = {**VALID_ENTRY, "rooms": [
        {"id": "A1", "name": "Hall", "x": 9999, "y": 100, "tags": ["entrance"]},
    ], "connections": []}
    errors = validate_map_entry(entry)
    assert any("bounds" in e for e in errors)

def test_connection_references_invalid_room():
    entry = {**VALID_ENTRY, "connections": [
        {"from": "A1", "to": "FAKE", "type": "door"},
    ]}
    errors = validate_map_entry(entry)
    assert any("FAKE" in e for e in errors)

def test_duplicate_room_ids():
    entry = {**VALID_ENTRY, "rooms": [
        {"id": "A1", "name": "Hall", "x": 100, "y": 100, "tags": ["entrance"]},
        {"id": "A1", "name": "Duplicate", "x": 200, "y": 200, "tags": []},
    ], "connections": []}
    errors = validate_map_entry(entry)
    assert any("duplicate" in e.lower() for e in errors)

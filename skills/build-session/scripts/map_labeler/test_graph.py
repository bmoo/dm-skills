from graph import longest_path, path_depth, reachable_from

ROOMS = ["A", "B", "C", "D", "E"]
CONNECTIONS = [
    {"from": "A", "to": "B", "type": "door"},
    {"from": "B", "to": "C", "type": "corridor"},
    {"from": "B", "to": "D", "type": "door"},
    {"from": "D", "to": "E", "type": "stairs"},
]

def test_longest_path_from_entrance():
    path = longest_path("A", CONNECTIONS)
    assert path == ["A", "B", "D", "E"]

def test_path_depth():
    assert path_depth("A", CONNECTIONS) == 4

def test_reachable_from():
    reached = reachable_from("A", CONNECTIONS)
    assert reached == {"A", "B", "C", "D", "E"}

def test_reachable_ignores_one_way_reverse():
    conns = [
        {"from": "A", "to": "B", "type": "door"},
        {"from": "B", "to": "C", "type": "one-way"},
    ]
    assert reachable_from("A", conns) == {"A", "B", "C"}
    assert reachable_from("C", conns) == {"C"}

def test_longest_path_single_room():
    path = longest_path("A", [])
    assert path == ["A"]

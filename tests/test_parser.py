import json
from zeon.stringify import dumps
from zeon.parse import loads

def test_roundtrip():
    scenarios = {
        'uniform-flat': [
            {'id': 1, 'name': 'John', 'role': 'admin'},
            {'id': 2, 'name': 'Mary', 'role': 'user'}
        ],
        'non-uniform-flat': {
            'id': '12345',
            'status': 'active',
            'count': 42
        },
        'uniform-nested-uniform': [
            {'id': 1, 'prefs': {'theme': 'dark', 'lang': 'en'}},
            {'id': 2, 'prefs': {'theme': 'light', 'lang': 'fr'}}
        ],
        'uniform-nested-nonuniform': [
            {'id': 1, 'meta': {'last_login': 'today'}},
            {'id': 2, 'meta': {'visits': 5, 'source': 'ad'}}
        ],
        'nonuniform-nested-nonuniform': {
            'user1': {'a': 1, 'b': {'c': 2}},
            'config': {'host': 'localhost', 'ports': [80, 443]}
        },
        'nonuniform-nested-uniform': {
            'status': 'success',
            'data': [
                {'id': 1, 'score': 90},
                {'id': 2, 'score': 85}
            ]
        }
    }

    all_passed = True
    for name, original in scenarios.items():
        try:
            l_str = dumps(original)
            parsed = loads(l_str)
            if parsed == original:
                print(f"PASS: {name}")
            else:
                print(f"FAIL: {name}")
                print(f"  Original: {original}")
                print(f"  Parsed:   {parsed}")
                all_passed = False
        except Exception as e:
            print(f"ERROR: {name}")
            print(f"  Exception: {e}")
            all_passed = False
            
    assert all_passed, "Some tests failed!"
    print("All round-trip tests passed!")

if __name__ == "__main__":
    test_roundtrip()

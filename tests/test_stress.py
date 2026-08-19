"""
ZEON Stress Test Suite
======================
50+ tests covering every documented syntax feature and pathological edge cases.
Run with: pytest tests/test_stress.py -v
"""
import json
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zeon.stringify import dumps
from zeon.parse import loads


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def roundtrip(original):
    zeon_text = dumps(original)
    return loads(zeon_text), zeon_text


def assert_roundtrip(original, label=""):
    result, zeon_text = roundtrip(original)
    assert result == original, (
        f"Roundtrip FAILED for: {label}\n"
        f"  Original : {original}\n"
        f"  ZEON     :\n{zeon_text}\n"
        f"  Parsed   : {result}"
    )


# ===========================================================================
# 1. PRIMITIVES
# ===========================================================================

class TestPrimitives:
    def test_integer(self):
        assert_roundtrip({"n": 42}, "integer")

    def test_negative_integer(self):
        assert_roundtrip({"n": -7}, "negative integer")

    def test_zero(self):
        assert_roundtrip({"n": 0}, "zero")

    def test_float(self):
        assert_roundtrip({"v": 3.14}, "float")

    def test_negative_float(self):
        assert_roundtrip({"v": -0.001}, "negative float")

    def test_large_float(self):
        assert_roundtrip({"v": 1234567.89}, "large float")

    def test_boolean_true(self):
        assert_roundtrip({"flag": True}, "boolean True")

    def test_boolean_false(self):
        assert_roundtrip({"flag": False}, "boolean False")

    def test_none_value(self):
        assert_roundtrip({"x": None}, "None value")

    def test_simple_string(self):
        assert_roundtrip({"name": "alice"}, "simple string")

    def test_string_with_spaces(self):
        assert_roundtrip({"name": "John Doe"}, "string with spaces")

    def test_string_with_path(self):
        assert_roundtrip({"path": "C:/Users/foo bar/file.txt"}, "string with path")

    def test_iso_date_string(self):
        assert_roundtrip({"created_at": "2026-08-16T14:30:00Z"}, "ISO date")

    def test_email_string(self):
        assert_roundtrip({"email": "user@example.com"}, "email string")

    def test_multiple_primitives(self):
        assert_roundtrip({
            "id": 1,
            "name": "Alice",
            "score": 9.5,
            "active": True,
            "deleted_at": None,
        }, "multiple primitives")


# ===========================================================================
# 2. FLAT OBJECTS
# ===========================================================================

class TestFlatObjects:
    def test_single_nested_flat_object(self):
        assert_roundtrip({
            "config": {"host": "localhost", "port": 5432}
        }, "single nested flat object")

    def test_multiple_flat_fields(self):
        assert_roundtrip({
            "user": {"id": 1, "name": "Bob", "role": "admin", "active": True}
        }, "multiple flat fields")

    def test_nested_flat_with_none(self):
        assert_roundtrip({
            "meta": {"version": "1.0", "deprecated": None}
        }, "nested flat with None")

    def test_flat_object_mixed_types(self):
        assert_roundtrip({
            "settings": {"retries": 3, "timeout": 30, "debug": False}
        }, "flat object mixed types")


# ===========================================================================
# 3. UNIFORM ARRAYS OF OBJECTS (tabular [])
# ===========================================================================

class TestUniformArrays:
    def test_two_row_uniform_array(self):
        assert_roundtrip([
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ], "two row uniform array")

    def test_ten_row_uniform_array(self):
        rows = [{"id": i, "value": i * 10, "active": i % 2 == 0} for i in range(10)]
        assert_roundtrip(rows, "10 row uniform array")

    def test_100_row_uniform_array(self):
        rows = [{"id": i, "name": f"user_{i}", "score": i * 0.5} for i in range(100)]
        assert_roundtrip(rows, "100 row uniform array")

    def test_uniform_array_with_none_fields(self):
        assert_roundtrip([
            {"id": 1, "name": "Alice", "email": None},
            {"id": 2, "name": "Bob", "email": None},
        ], "uniform array with None fields")

    def test_uniform_array_with_quoted_strings(self):
        assert_roundtrip([
            {"id": 1, "city": "New York", "country": "United States"},
            {"id": 2, "city": "Sao Paulo", "country": "Brazil"},
        ], "uniform array with multi-word strings")

    def test_uniform_array_wrapped_in_dict(self):
        assert_roundtrip({
            "status": "ok",
            "users": [
                {"id": 1, "role": "admin"},
                {"id": 2, "role": "viewer"},
            ]
        }, "uniform array inside dict")

    def test_uniform_array_all_booleans(self):
        assert_roundtrip([
            {"id": 1, "a": True, "b": False, "c": True},
            {"id": 2, "a": False, "b": True, "c": False},
        ], "uniform array with booleans")


# ===========================================================================
# 4. NESTED UNIFORM SUB-OBJECTS (tuple headers)
# ===========================================================================

class TestNestedUniformSubObjects:
    def test_nested_uniform_object_in_array(self):
        assert_roundtrip([
            {"id": 1, "prefs": {"theme": "dark", "lang": "en"}},
            {"id": 2, "prefs": {"theme": "light", "lang": "fr"}},
        ], "nested uniform sub-objects")

    def test_nested_sub_object_with_sibling_field(self):
        assert_roundtrip([
            {"id": 1, "stats": {"logins": 5, "errors": 0}, "role": "admin"},
            {"id": 2, "stats": {"logins": 12, "errors": 2}, "role": "user"},
        ], "nested sub-object with sibling field")


# ===========================================================================
# 5. SEMI-UNIFORM ARRAYS (hybrid tabular-inline)
# ===========================================================================

class TestSemiUniformArrays:
    def test_semi_uniform_extra_keys(self):
        data = [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user", "extra": "vip"},
        ]
        zeon_text = dumps(data)
        result = loads(zeon_text)
        assert result == data

    def test_event_logs_with_optional_fields(self):
        data = [
            {"level": "INFO", "message": "start"},
            {"level": "ERROR", "message": "db fail", "retry": 3},
            {"level": "WARN", "message": "slow", "latency_ms": 1200},
        ]
        zeon_text = dumps(data)
        result = loads(zeon_text)
        assert result == data


# ===========================================================================
# 6. KEYED TABULAR ({})
# ===========================================================================

class TestKeyedTabular:
    def test_simple_keyed_tabular(self):
        assert_roundtrip({
            "envs": {
                "production": {"region": "eu-central-1", "replicas": 6, "debug": False},
                "staging": {"region": "eu-central-1", "replicas": 2, "debug": True},
            }
        }, "keyed tabular {}")

    def test_keyed_tabular_feature_flags(self):
        assert_roundtrip({
            "flags": {
                "feature_a": {"enabled": True, "rollout": 100},
                "feature_b": {"enabled": False, "rollout": 0},
            }
        }, "keyed tabular feature flags")


# ===========================================================================
# 7. N-DIMENSIONAL MATRICES
# ===========================================================================

class TestMatrices:
    def test_2d_matrix_integers(self):
        assert_roundtrip({
            "coords": [[1, 2], [3, 4], [5, 6]]
        }, "2D integer matrix")

    def test_2d_matrix_floats(self):
        assert_roundtrip({
            "route": [[-23.5505, -46.6333], [-23.5501, -46.6341]]
        }, "2D float matrix")

    def test_3d_matrix(self):
        assert_roundtrip({
            "cube": [[[1, 0], [0, 1]], [[1, 1], [0, 0]]]
        }, "3D matrix")


# ===========================================================================
# 8. MIXED DATA FALLBACK (inline [])
# ===========================================================================

class TestMixedDataFallback:
    def test_array_of_strings(self):
        assert_roundtrip({"tags": ["python", "zeon", "llm"]}, "array of strings")

    def test_array_of_integers(self):
        assert_roundtrip({"ports": [80, 443, 8080]}, "array of integers")

    def test_array_of_mixed_types(self):
        assert_roundtrip({"mixed": [1, "hello", True, None]}, "mixed type array")

    def test_array_with_nested_object(self):
        assert_roundtrip({"items": [1, {"flag": True}, [2, 3]]}, "array with nested object")


# ===========================================================================
# 9. DEEPLY NESTED STRUCTURES
# ===========================================================================

class TestDeeplyNested:
    def test_3_levels_deep(self):
        assert_roundtrip({
            "a": {"b": {"c": 42}}
        }, "3 levels deep")

    def test_config_with_deep_nesting(self):
        assert_roundtrip({
            "config": {
                "db": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"user": "admin", "password": "secret123"}
                },
                "cache": {"ttl": 300, "enabled": True}
            }
        }, "deeply nested config")

    def test_nested_with_array_at_leaf(self):
        assert_roundtrip({
            "network": {
                "cluster": {
                    "nodes": ["192.168.0.1", "192.168.0.2", "192.168.0.3"]
                }
            }
        }, "nested with array at leaf")

    def test_five_levels_deep(self):
        assert_roundtrip({
            "l1": {"l2": {"l3": {"l4": {"l5": "deep_value"}}}}
        }, "5 levels deep")

    def test_cascading_sibling_arrays(self):
        assert_roundtrip({
            "a": [1, 2, 3],
            "b": [4, 5, 6],
            "c": [7, 8, 9],
        }, "cascading sibling arrays")

    def test_mixed_depth_siblings(self):
        assert_roundtrip({
            "name": "service",
            "version": 2,
            "active": True,
            "endpoints": ["/api/v1", "/api/v2"],
            "db": {"host": "localhost", "port": 5432},
            "owners": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ]
        }, "mixed depth siblings")

    def test_deeply_nested_config_worst_case(self):
        assert_roundtrip({
            "app": {
                "name": "myapp",
                "env": "production",
                "database": {
                    "primary": {"host": "db1.example.com", "port": 5432, "ssl": True},
                    "replica": {"host": "db2.example.com", "port": 5432, "ssl": True},
                    "pool": {"min": 5, "max": 20, "timeout": 30}
                },
                "cache": {
                    "redis": {"host": "redis.example.com", "port": 6379, "ttl": 3600},
                    "local": {"size_mb": 256, "eviction": "lru"}
                },
                "logging": {
                    "level": "info",
                    "outputs": ["stdout", "file"],
                    "file": {"path": "/var/log/app.log", "rotate": True, "max_mb": 100}
                }
            }
        }, "deeply nested config worst case")


# ===========================================================================
# 10. REAL-WORLD SHAPES
# ===========================================================================

class TestRealWorldShapes:
    def test_ecommerce_order(self):
        assert_roundtrip({
            "order_id": "ORD-99321",
            "status": "shipped",
            "customer": {"id": 8472, "name": "Maria Silva", "email": "maria@example.com"},
            "items": [
                {"sku": "SKU-001", "qty": 2, "price": 149.99},
                {"sku": "SKU-003", "qty": 1, "price": 34.50},
            ],
            "shipping": {"method": "express", "cost": 12.90, "estimated_days": 2},
            "total": 347.38,
        }, "e-commerce order")

    def test_github_repos(self):
        repos = [
            {"id": i, "name": f"repo-{i}", "stars": i * 100, "forks": i * 10, "private": False, "language": "Python"}
            for i in range(30)
        ]
        assert_roundtrip(repos, "30 GitHub repos")

    def test_employee_records(self):
        employees = [
            {"id": i, "name": f"Employee {i}", "department": "engineering", "salary": 5000 + i * 100, "active": True}
            for i in range(100)
        ]
        assert_roundtrip(employees, "100 employee records")

    def test_timeseries_data(self):
        series = [
            {"ts": f"2026-08-{str(i).zfill(2)}T00:00:00Z", "value": i * 1.5, "anomaly": i % 10 == 0}
            for i in range(1, 61)
        ]
        assert_roundtrip(series, "60 time-series rows")

    def test_feature_flags_large(self):
        flags = {f"flag_{i}": {"enabled": i % 2 == 0, "rollout": i * 2, "env": "prod"} for i in range(40)}
        zeon_text = dumps(flags)
        result = loads(zeon_text)
        assert result == flags

    def test_api_response_wrapper(self):
        assert_roundtrip({
            "success": True,
            "code": 200,
            "message": "OK",
            "data": [
                {"id": 1, "score": 90, "label": "A"},
                {"id": 2, "score": 75, "label": "B"},
                {"id": 3, "score": 60, "label": "C"},
            ],
            "meta": {"total": 3, "page": 1, "per_page": 10}
        }, "API response wrapper")

    def test_contacts_with_nested_address(self):
        contacts = [
            {"id": i, "name": f"Contact {i}", "address": {"city": "Sao Paulo", "country": "BR", "zip": f"0100{i}"}}
            for i in range(50)
        ]
        assert_roundtrip(contacts, "50 contacts with nested address")


# ===========================================================================
# 11. EDGE CASES
# ===========================================================================

class TestEdgeCases:
    def test_empty_dict(self):
        result, _ = roundtrip({})
        assert result == {}

    def test_empty_list_in_dict(self):
        assert_roundtrip({"items": []}, "empty list in dict")

    def test_single_item_array(self):
        assert_roundtrip([{"id": 1, "name": "solo"}], "single item array")

    def test_string_that_looks_like_number(self):
        assert_roundtrip({"code": "007"}, "string that looks like number")

    def test_string_that_looks_like_boolean(self):
        assert_roundtrip({"val": "true"}, "string that looks like boolean")

    def test_string_that_looks_like_none(self):
        assert_roundtrip({"val": "null"}, "string that looks like null")

    def test_all_none_values(self):
        assert_roundtrip({"a": None, "b": None, "c": None}, "all None values")

    def test_large_integer(self):
        assert_roundtrip({"big": 9999999999}, "large integer")

    def test_negative_floats_in_array(self):
        assert_roundtrip([
            {"x": -1.5, "y": 2.3},
            {"x": 0.0, "y": -99.9},
        ], "negative floats in array")

    def test_unicode_string(self):
        assert_roundtrip({"greeting": "Ola Mundo"}, "unicode string")

    def test_very_long_string(self):
        long_val = "x" * 200
        assert_roundtrip({"data": long_val}, "very long string (200 chars)")

    def test_mixed_key_types_at_top_level(self):
        assert_roundtrip({
            "count": 42,
            "label": "test",
            "active": True,
            "ratio": 0.75,
            "deleted_at": None,
        }, "mixed top-level key types")


# ===========================================================================
# 12. ZEON FORMAT VALIDATION
# ===========================================================================

class TestZeonFormatValidation:
    def test_array_uses_tabular_header(self):
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        zeon_text = dumps(data)
        lines = zeon_text.strip().splitlines()
        assert any("id" in line and "name" in line for line in lines), \
            f"Expected tabular header in ZEON output:\n{zeon_text}"

    def test_repeated_keys_eliminated(self):
        # With the root [] marker, bare root-level lists now also use tabular format.
        # The key should appear exactly once (in the header), not 20 times.
        data = [{"id": i, "role": "user"} for i in range(20)]
        zeon_text = dumps(data)
        assert zeon_text.startswith("[]"), f"Expected [] root marker:\n{zeon_text}"
        count_id = zeon_text.count("id")
        assert count_id == 1, f"Key 'id' appears {count_id} times (expected 1):\n{zeon_text}"

    def test_no_json_braces_in_tabular(self):
        data = [{"id": i, "name": f"user_{i}"} for i in range(10)]
        zeon_text = dumps(data)
        assert "{" not in zeon_text and "}" not in zeon_text, \
            f"JSON braces found in tabular ZEON output:\n{zeon_text}"

    def test_output_is_non_empty_string(self):
        zeon_text = dumps({"key": "value", "num": 42})
        assert isinstance(zeon_text, str) and len(zeon_text) > 0

    def test_double_serialization_is_stable(self):
        data = [{"id": i, "val": i * 2, "active": True} for i in range(5)]
        zeon1 = dumps(data)
        parsed = loads(zeon1)
        zeon2 = dumps(parsed)
        assert zeon1 == zeon2, (
            f"Double-serialization not stable:\nPass 1:\n{zeon1}\nPass 2:\n{zeon2}"
        )


# ===========================================================================
# 13. ROOT [] MARKER (new feature)
# ===========================================================================

class TestRootMarker:
    def test_stringifier_emits_root_marker(self):
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        zeon_text = dumps(data)
        assert zeon_text.startswith("[]"), \
            f"Expected [] root marker as first line:\n{zeon_text}"

    def test_root_marker_roundtrip_basic(self):
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        assert_roundtrip(data, "root marker basic roundtrip")

    def test_root_marker_eliminates_keys(self):
        data = [{"id": i, "role": "user"} for i in range(20)]
        zeon_text = dumps(data)
        count_id = zeon_text.count("id")
        assert count_id == 1, \
            f"Key 'id' appears {count_id} times in root tabular (expected 1):\n{zeon_text}"

    def test_root_marker_100_rows(self):
        data = [{"id": i, "name": f"user_{i}", "active": True} for i in range(100)]
        assert_roundtrip(data, "root marker 100 rows")

    def test_root_marker_semi_uniform(self):
        data = [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob",   "role": "user", "vip": True},
        ]
        assert_roundtrip(data, "root marker semi-uniform")

    def test_parse_handwritten_root_marker(self):
        zeon_text = "[]\n  id name score\n  1 Alice 95\n  2 Bob 87"
        result = loads(zeon_text)
        expected = [
            {"id": 1, "name": "Alice", "score": 95},
            {"id": 2, "name": "Bob",   "score": 87},
        ]
        assert result == expected, f"Handwritten [] parse failed:\n{result}"

# ZEON Stress Test Suite

This directory contains the comprehensive stress test suite for the ZEON parser and stringifier. The suite is designed to ensure mathematical roundtrip fidelity (`loads(dumps(data)) == data`) across all supported data shapes, edge cases, and deeply nested structures.

**Currently passing: 76/76 tests in ~0.15s.**

## Running the Tests

To run the suite, you need `pytest`:

```bash
pip install pytest
pytest tests/test_stress.py -v
```

## Test Coverage (13 Categories)

The tests simulate everything from basic primitives to complex, real-world corporate payloads.

### 1. Primitives (15 tests)
Ensures fundamental building blocks work perfectly without unnecessary quotes.
- Integers, floats, negative values, and large numbers.
- Booleans (`True`, `False`) and Nulls (`None`).
- Strings with spaces, paths, ISO dates, and URLs.

### 2. Flat Objects (4 tests)
Verifies basic indentation behavior and `{}` elimination.

### 3. Uniform Arrays (7 tests)
The core of ZEON's token economy. Tests arrays with 2, 10, and **100 rows**, handling missing fields (`None`), multi-word strings, and boolean matrices.

### 4. Nested Uniform Sub-Objects (Tuple Headers) (2 tests)
Ensures complex headers like `prefs(theme lang)` map positional data correctly.

### 5. Semi-Uniform Arrays (Hybrid Tabular-Inline) (2 tests)
Tests ZEON's unique ability to extract common keys into a header and append row-specific exceptions inline.

### 6. Keyed Tabular (`{}`) (2 tests)
Verifies dictionaries of uniform objects where the dictionary key becomes the first column.

### 7. N-Dimensional Matrices (3 tests)
Validates native support for 2D and 3D matrices via `[2]` and `[3]` suffixes.

### 8. Mixed Data Fallback (4 tests)
Ensures that arrays containing mixed types (e.g., `[1, "hello", {"flag": True}]`) gracefully fall back to inline format without corrupting data.

### 9. Deeply Nested Structures (7 tests)
Guarantees that the absence of `{}` and commas doesn't break the hierarchy. Tests up to **5 levels of depth**, cascading sibling arrays, and a worst-case deeply nested app configuration.

### 10. Real-World Shapes (7 tests)
Simulates actual LLM payloads:
- E-commerce orders (customers, items, shipping).
- 30 GitHub repositories.
- 100 employee records.
- 60 time-series anomaly records.
- Standard API response wrappers.

### 11. Edge Cases (12 tests)
Where most parsers break:
- Empty dictionaries and lists.
- Single-item arrays.
- Strings that look like primitives (`"007"`, `"true"`, `"null"`).
- Negative floats amidst strings.
- Unicode characters and extremely long strings (200+ chars).

### 12. ZEON Format Validation (5 tests)
Beyond roundtrip fidelity, these tests inspect the generated ZEON string to ensure token savings are actually achieved:
- Verifies that keys are eliminated and only appear in the header.
- Ensures no JSON braces `{}` leak into the output.
- Validates double-serialization stability (`dumps(loads(dumps(data)))`).

### 13. Root `[]` Marker (6 tests)
Validates the root-level array syntax, ensuring that bare lists at the root of the file properly trigger tabular formatting without needing a parent dictionary.

---
*Zero-overhead. 100% Roundtrip Fidelity.*

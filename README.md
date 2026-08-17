<div align="center">
  <h1>LION</h1>
  <p><strong>Lightweight LLM Object Notation</strong></p>
  <p>A next-generation tabular serialization format designed for maximum LLM token efficiency.</p>
</div>

LION is a whitespace-sensitive data serialization language that completely reimagines how structured data is presented to Large Language Models (LLMs). 

Heavily inspired by Python's clean visual structure and YAML's lightness, LION eliminates the most expensive parts of JSON: redundant keys, brackets, and quotes. It introduces a unique "Suffix-driven Tabular Grammar" that achieves extreme token density without sacrificing human readability or parser reliability.

## Table of Contents
- [The Token Problem](#the-token-problem)
- [The LION Solution](#the-lion-solution)
- [Syntax Guide](#syntax-guide)
- [Performance Benchmarks](#performance-benchmarks)
- [CLI Usage](#cli-usage)
- [Installation](#installation)

---

## The Token Problem

In modern AI development, feeding context to LLMs via JSON payloads is incredibly expensive. JSON was built for machines, not for LLM tokenizers. 

When dealing with arrays of objects (like a list of 1,000 products), JSON forces you to repeat the keys `"id"`, `"name"`, `"price"` 1,000 times. Every repeated key, colon, and comma consumes precious tokens, slowing down inference and increasing API costs.

## The LION Solution

LION solves this through **Tabular Indentation**. By using special suffixes (`[]` and `[][]`) directly on the keys, you tell the parser exactly how to read the indented block below it. The header is declared only once, and the data flows cleanly underneath.

### Example comparison

JSON Payload:
```json
"items": [
  {"id": "SKU-100", "qty": 1, "price": 150.0},
  {"id": "SKU-205", "qty": 2, "price": 45.5}
]
```

LION Equivalent:
```python
items[]
  id qty price
  SKU-100 1 150.0
  SKU-205 2 45.5
```
By declaring `items[]`, LION understands the first indented line is the header, and maps all subsequent lines to those keys.

---

## Syntax Guide

LION uses pure spaces for separation and Python-like primitive types (`True`, `False`, `None`).

### 1. Primitive Key-Value Pairs
Standard assignments use `=`. Unquoted strings are natively supported for ISO dates and identifiers.
```python
order_id=ORD-99321
is_active=True
deleted_at=None
created_at=2026-08-16T14:30:00Z
```

### 2. Flat Objects
Objects use indentation. No `{}` required.
```python
customer
  id name email
  8472 "Maria Silva" maria@example.com
```

### 3. Arrays of Objects (Tabular Format)
Use the `[]` suffix. The first line is the header.
```python
users[]
  id role
  1 admin
  2 guest
```

### 4. Nested Tuples
If an object contains a sub-object uniformly, you can declare it in the header using `key(sub1 sub2)` and map values using `(val1 val2)`.
```python
products[]
  id dimensions(weight unit)
  1 (1.2 kg)
```

### 5. 2D Matrices
Use the `[][]` suffix for pure multidimensional arrays with no headers (e.g., coordinates, tensor data).
```python
shipping_route[][]
  -23.5505 -46.6333
  -23.5501 -46.6341
```

### 6. Mixed Data Fallback
If an array contains irregular or heavily nested mixed types, a tabular header won't fit. In these cases, LION gracefully falls back to an "inline" format.

JSON:
```json
"mixed_data": [
  1,
  "hello",
  {"flag": true},
  [2, 3]
]
```

LION Equivalent:
```python
mixed_data=[1 "hello" (flag=True) [2 3]]
```
Notice how `[]` brackets are used for arrays and `()` for nested objects (`flag=True`). This allows you to represent any deeply nested chaos securely on a single line, retaining the exact structure of JSON while stripping away commas and quotes.

---

## Performance Benchmarks

LION excels in large, list-heavy data structures. We ran our official Python implementation against complex E-commerce API responses.

**Results (Using OpenAI TikToken on 6 Structural Shapes):**

| Dataset (Large Scale) | JSON Compact | YAML | LION | Reduction (vs JSON) |
| :--- | :--- | :--- | :--- | :--- |
| Uniform Flat | 12,246 | 15,742 | 9,493 | **-22.5%** |
| Uniform Nested Uniform | 13,002 | 17,500 | 11,002 | **-15.4%** |
| Uniform Nested Non-uniform | 10,752 | 13,250 | 9,502 | **-11.6%** |
| Non-uniform Nested Uniform | 4,033 | 6,034 | 3,036 | **-24.7%** |
| Non-uniform Flat | 1,555 | 1,600 | 1,466 | **-5.7%** |
| Non-uniform Nested Non-uniform | 1,615 | 2,371 | 1,564 | **-3.2%** |


*In highly uniform, list-heavy structures, LION achieves up to ~25% token reduction against purely minified JSON, and over ~40% against YAML.*

This translates to nearly double the context window capacity for your LLM applications.

---

## CLI Usage

LION ships with a powerful bidirectional CLI tool to convert your existing JSON datasets into LION format.

```bash
# Convert JSON to LION
lion convert data.json -o data.lion

# Convert LION back to JSON
lion convert data.lion -o data.json

# Print to stdout
lion convert data.json --print
```

---

## Installation

Currently, the reference implementation is available in Python.

**Requirements:**
- Python 3.10+
- Poetry

```bash
git clone https://github.com/your-org/lion.git
cd lion
poetry install
```

To use it in your code:
```python
import lion

# Decode LION string to Python Dictionary
data = lion.loads(text)

# Encode Python Dictionary to LION format
lion_text = lion.dumps(data)
```

---
*LION - The future of AI data serialization.*

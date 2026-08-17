<div align="center">
  <h1>ZEON</h1>
  <p><strong>Zero-overhead Encoding Object Notation</strong></p>
  <p>A next-generation tabular serialization format designed for maximum LLM token efficiency.</p>
</div>

ZEON is a whitespace-sensitive data serialization language that completely reimagines how structured data is presented to Large Language Models (LLMs). 

Heavily inspired by Python's clean visual structure and YAML's lightness, ZEON eliminates the most expensive parts of JSON: redundant keys, brackets, and quotes. It introduces a unique "Suffix-driven Tabular Grammar" that achieves extreme token density without sacrificing human readability or parser reliability.

## Table of Contents
- [The Token Problem](#the-token-problem)
- [The ZEON Solution](#the-zeon-solution)
- [Syntax Guide](#syntax-guide)
- [Performance Benchmarks](#performance-benchmarks)
- [CLI Usage](#cli-usage)
- [Installation](#installation)

---

## The Token Problem

In modern AI development, feeding context to LLMs via JSON payloads is incredibly expensive. JSON was built for machines, not for LLM tokenizers. 

When dealing with arrays of objects (like a list of 1,000 products), JSON forces you to repeat the keys `"id"`, `"name"`, `"price"` 1,000 times. Every repeated key, colon, and comma consumes precious tokens, slowing down inference and increasing API costs.

## The ZEON Solution

ZEON solves this through **Tabular Indentation**. By using special suffixes (`[]` and `[][]`) directly on the keys, you tell the parser exactly how to read the indented block below it. The header is declared only once, and the data flows cleanly underneath.

### Example comparison

JSON Payload:
```json
"items": [
  {"id": "SKU-100", "qty": 1, "price": 150.0},
  {"id": "SKU-205", "qty": 2, "price": 45.5}
]
```

ZEON Equivalent:
```python
items[]
  id qty price
  SKU-100 1 150.0
  SKU-205 2 45.5
```
By declaring `items[]`, ZEON understands the first indented line is the header, and maps all subsequent lines to those keys.

---

## Syntax Guide

ZEON uses pure spaces for separation and Python-like primitive types (`True`, `False`, `None`).

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

### 6. Visual Annotations (Ignored by Parser)
ZEON allows human-friendly annotations to enhance readability without affecting the actual parsed JSON data.
- **Suffixes `()` and `[]` on columns:** Mark complex columns explicitly.
- **Inline Annotations `[text]`:** Describe what a key belongs to.

```python
users[]
  id name preferences(theme) nicknames() aliases[]
  1 Maria (light) nicknames[Maria]=(1=M 2=Mah) [mary mah]
```
The parser completely ignores `()`, `[]` and `[Maria]`, resulting in pristine JSON keys. The ZEON stringifier automatically generates `()` and `[]` for deep objects and arrays.

### 7. Multiline Objects and Arrays
Unlike JSON which requires commas, ZEON allows beautiful multiline formatting inside `(...)` (dictionaries) and `[...]` (arrays) while natively ignoring indentation and line breaks, exactly like Python.

```python
config
  db_pool (
    host=localhost
    port=5432
    options=(
      ssl=True
      timeout=30
    )
  )
  nodes [
    192.168.0.1
    192.168.0.2
  ]
```

### 8. Hybrid Tabular-Inline
If an array contains semi-uniform objects (e.g., event logs where some rows have extra properties), ZEON finds the intersection of common keys for the header, and appends the extra properties inline at the end of each row.

```python
event_logs[]
  timestamp level message
  2026-08-17T10:00:00Z INFO "User logged in" user_id=405
  2026-08-17T10:01:00Z ERROR "DB Timeout" retry_count=3 context=(db=users)
```
This ensures high token savings even for messy data.

### 9. Keyed Tabular Format
When dealing with dictionaries of uniform objects (like feature flags or environment configs), ZEON uses the `{}` suffix. The first value of each row becomes the dictionary key, eliminating the need to repeat nested keys.

```python
environments{}
  region replicas debug
  production eu-central-1 6 False
  staging eu-central-1 2 True
```

### 10. Mixed Data Fallback
If an array contains irregular or heavily nested mixed types where no common header exists, ZEON gracefully falls back to an "inline" format.

JSON:
```json
"mixed_data": [
  1,
  "hello",
  {"flag": true},
  [2, 3]
]
```

ZEON Equivalent:
```python
mixed_data=[1 "hello" (flag=True) [2 3]]
```
Notice how `[]` brackets are used for arrays and `()` for nested objects (`flag=True`). This allows you to represent any deeply nested chaos securely, retaining the exact structure of JSON while stripping away commas and quotes.

---

## Performance Benchmarks

ZEON shines on uniform, list-heavy data structures. We ran our official Python implementation against 8 representative real-world dataset shapes.

**Results (Tokenizer: `cl100k_base` — GPT-4 / tiktoken):**

| Dataset | Tabular Eligibility | JSON Compact | YAML | **ZEON** | vs JSON | vs YAML |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: |
| Employee Records (100, uniform) | 100% | 2,804 | 3,702 | **1,709** | `-39.1%` | `-53.8%` |
| GitHub Repositories (30, uniform) | 100% | 2,083 | 2,461 | **1,188** | `-43.0%` | `-51.7%` |
| Time-series Analytics (60, uniform) | 100% | 2,332 | 2,870 | **1,498** | `-35.8%` | `-47.8%` |
| Contacts with nested address (50) | 100% | 2,603 | 3,302 | **1,716** | `-34.1%` | `-48.0%` |
| E-commerce Orders (50, nested) | 33% | 4,933 | 6,220 | **3,581** | `-27.4%` | `-42.4%` |
| Feature Flags (40, keyed map) | 100% | 825 | 963 | **487** | `-41.0%` | `-49.4%` |
| Semi-uniform Event Logs (75, mixed) | 50% | 2,944 | 3,617 | **2,303** | `-21.8%` | `-36.3%` |
| Deeply Nested Config (worst case) | 0% | 137 | 173 | **105** | `-23.4%` | `-39.3%` |
| **TOTAL (all 8 datasets)** | — | **18,661** | **23,308** | **12,587** | **`-32.5%`** | **`-46.0%`** |

> **Note:** For a detailed comparison between ZEON and other LLM-oriented formats (like TOON), please refer to our [BENCHMARKS.md](BENCHMARKS.md) file.

*On highly uniform, list-heavy data (100% tabular eligibility), ZEON achieves up to **-43%** token reduction against minified JSON, and over **-53%** against YAML.*
*Even on deeply nested or semi-uniform structures, ZEON never uses **more** tokens than YAML.*

This translates to significantly increased effective context window for your LLM applications, directly reducing API inference costs.

---

## When Not to Use ZEON (And Workarounds)

While ZEON is incredibly powerful for AI inference, it is highly sensitive to indentation and syntax. 

**1. Authoring Data Manually**
Writing data directly in ZEON by hand can be tricky because missing a single space or indentation level could alter the parsed output. 
**The Solution:** You don't have to write ZEON! Since ZEON is 100% losslessly compatible with JSON, you can write and maintain your data in standard JSON or YAML, and simply use our CLI tool or Python library to translate it to ZEON right before sending the prompt to the LLM.

**2. Purely Flat Tabular Data (No Nesting at All)**
If your data is 100% flat (like a classic spreadsheet with no nested objects or arrays), standard CSV might technically use slightly fewer tokens than ZEON. However, CSV breaks down completely the moment you need to include a nested array or object, whereas ZEON handles it flawlessly.

---

## CLI Usage

ZEON ships with a powerful bidirectional CLI tool to convert your existing datasets between ZEON, JSON and YAML formats.

```bash
# Convert JSON or YAML to ZEON
zeon convert data.json -> data.zeon
zeon convert config.yaml -> config.zeon

# Convert ZEON back to JSON or YAML
zeon convert data.zeon -> data.json
zeon convert config.zeon -> config.yaml

# Print to stdout
zeon convert data.yaml --print
```

---

## Installation

ZEON is officially available on PyPI and can be installed via `pip`:

```bash
pip install zeon-format
```

To use it in your code:
```python
import zeon

# Decode ZEON string to Python Dictionary
data = zeon.loads(text)

# Encode Python Dictionary to ZEON format
zeon_text = zeon.dumps(data)

# Direct string conversion
json_text = zeon.convert(zeon_text).to_json()
yaml_text = zeon.convert(zeon_text).to_yaml()
zeon_text = zeon.convert(yaml_text).to_zeon()

# Direct file conversion
# 1. Provide only the filename to save it automatically in the same directory as the original
zeon.convert("path/to/data.zeon").to_json("data.json")
zeon.convert("path/to/data.zeon").to_yaml("data.yaml")

# 2. Or provide a custom path to save it elsewhere
zeon.convert("path/to/data.zeon").to_json("exports/my_data.json")
zeon.convert("path/to/data.json").to_zeon("exports/my_data.zeon")
```

---
*ZEON - The future of AI data serialization.*

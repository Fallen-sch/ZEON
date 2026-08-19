<div align="center">
  <img src="vscode-zeon/icons/zeon-logo.png" alt="ZEON Logo" width="120" />
  <h1>ZEON</h1>
  <p><strong>Zero-overhead Encoding Object Notation</strong></p>
  <p>A tabular serialization format designed for maximum LLM token efficiency.</p>
  <p>
    <a href="https://pypi.org/project/zeon-format/"><img src="https://img.shields.io/pypi/v/zeon-format?color=ffd343&label=PyPI" alt="PyPI Version" /></a>
    <a href="https://www.npmjs.com/package/zeon-format"><img src="https://img.shields.io/npm/v/zeon-format?color=38bdf8&label=NPM" alt="NPM Version" /></a>
    <a href="https://marketplace.visualstudio.com/items?itemName=FallenBR.zeon-vscode"><img src="https://img.shields.io/badge/VS%20Code-v1.0.0-0ea5e9?logo=visualstudiocode" alt="VS Code Extension" /></a>
    <a href="https://open-vsx.org/extension/FallenBR/zeon-vscode"><img src="https://img.shields.io/open-vsx/v/FallenBR/zeon-vscode?color=8b5cf6&label=Open%20VSX" alt="Open VSX Registry" /></a>
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" />
  </p>
</div>

---

ZEON is a whitespace-sensitive serialization language that eliminates the most token-expensive parts of JSON — redundant keys, brackets, and commas — through a **Suffix-driven Tabular Grammar**. Declare your schema once, stream your data cleanly below it.

## Table of Contents

- [Why ZEON](#why-zeon)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Syntax Guide](#syntax-guide)
- [Using ZEON with LLMs](#using-zeon-with-llms)
- [Performance Benchmarks](#performance-benchmarks)
- [Developer Tooling](#developer-tooling)
- [CLI Reference](#cli-reference)

---

## Why ZEON

When you feed structured data to an LLM, JSON forces you to repeat every key on every row. A list of 1,000 products repeats `"id"`, `"name"`, `"price"` — and their surrounding quotes, colons, and commas — 1,000 times each. Every one of those characters costs tokens.

ZEON solves this with **tabular indentation**: declare the header once, list the rows below.

**JSON** — 1,100 tokens (~$0.0110 per call with GPT-4o):
```json
"products": [
  {"id": "SKU-001", "name": "Wireless Headphones", "category": "electronics", "price": 149.99, "in_stock": true},
  {"id": "SKU-002", "name": "Mechanical Keyboard", "category": "electronics", "price": 89.90, "in_stock": true},
  {"id": "SKU-003", "name": "USB-C Hub", "category": "accessories", "price": 34.50, "in_stock": false},
  {"id": "SKU-004", "name": "Monitor Stand", "category": "accessories", "price": 45.00, "in_stock": true},
  {"id": "SKU-005", "name": "Webcam 4K", "category": "electronics", "price": 119.00, "in_stock": true},
  {"id": "SKU-006", "name": "Desk Lamp", "category": "furniture", "price": 29.99, "in_stock": true},
  {"id": "SKU-007", "name": "Laptop Sleeve", "category": "accessories", "price": 19.90, "in_stock": false},
  {"id": "SKU-008", "name": "Ergonomic Mouse", "category": "electronics", "price": 55.00, "in_stock": true},
  {"id": "SKU-009", "name": "Cable Organizer", "category": "accessories", "price": 12.50, "in_stock": true},
  {"id": "SKU-010", "name": "Portable SSD", "category": "electronics", "price": 79.99, "in_stock": true}
]
```

**ZEON** — 640 tokens (~$0.0064 per call with GPT-4o) — **42% fewer tokens, identical data:**
```
products[]
  id name category price in_stock
  SKU-001 "Wireless Headphones" electronics 149.99 True
  SKU-002 "Mechanical Keyboard" electronics 89.90 True
  SKU-003 "USB-C Hub" accessories 34.50 False
  SKU-004 "Monitor Stand" accessories 45.00 True
  SKU-005 "Webcam 4K" electronics 119.00 True
  SKU-006 "Desk Lamp" furniture 29.99 True
  SKU-007 "Laptop Sleeve" accessories 19.90 False
  SKU-008 "Ergonomic Mouse" electronics 55.00 True
  SKU-009 "Cable Organizer" accessories 12.50 True
  SKU-010 "Portable SSD" electronics 79.99 True
```

At scale (1,000 products), ZEON saves ~46,000 tokens per call — roughly **$0.46 per call, or $460 per 1,000 calls**.

---

## Quick Start

## Installation

### Python

```bash
pip install zeon-format
```

```python
import zeon

# Parse and serialize
data = zeon.loads(text)
zeon_text = zeon.dumps(data)

# String conversion
json_text  = zeon.convert(zeon_text).to_json()
yaml_text  = zeon.convert(zeon_text).to_yaml()
zeon_text  = zeon.convert(json_text).to_zeon()

# File conversion — saves alongside the original by default
zeon.convert("path/to/data.zeon").to_json("data.json")
zeon.convert("path/to/data.json").to_zeon("data.zeon")

# Or specify a custom output path
zeon.convert("path/to/data.json").to_zeon("exports/my_data.zeon")
```

### Node.js / TypeScript

```bash
npm install zeon-parser
```

```typescript
import { parse } from 'zeon-parser';

const result = parse(`
project_name="ZEON"
config
  timeout retries
  30 5
`);

console.log(result.project_name); // ZEON
console.log(result.config.timeout); // 30
```

> Full NPM documentation: [parsers/javascript/README.md](parsers/javascript/README.md)

---

## Syntax Guide

ZEON uses spaces for separation and Python-style literals (`True`, `False`, `None`).

### 1. Primitive Key-Value Pairs

Standard assignments use `=`. ISO dates and identifiers are natively supported without quotes.

```
order_id=ORD-99321
is_active=True
deleted_at=None
created_at=2026-08-16T14:30:00Z
```

### 2. Flat Objects

Objects use indentation. No `{}` required.

```
customer
  id name email
  8472 "Maria Silva" maria@example.com
```

### 3. Arrays of Objects (Tabular Format)

Use the `[]` suffix. The first indented line is the header; all subsequent lines are rows.

```
users[]
  id role
  1 admin
  2 guest
```

### 4. Nested Sub-Objects (Tuple Headers)

Declare a nested object in the header using `key(sub1 sub2)` and map values positionally.

```
products[]
  id dimensions(weight unit)
  1 (1.2 kg)
```

You can also append extra key-value pairs inline at the end of any row:

```
items[]
  name attributes(damage defense)
  sword (10 10 extra_fire=5)
```

Parses to `{"damage": 10, "defense": 10, "extra_fire": 5}`.

### 5. N-Dimensional Matrices

Use `[2]` for 2D arrays and `[3]` for 3D arrays (layers separated by a blank line).

```
shipping_route[2]
  -23.5505 -46.6333
  -23.5501 -46.6341

cube_data[3]
  1 1
  1 1

  0 0
  0 0
```

### 6. Keyed Tabular Format (Dict of Objects)

Use the `{}` suffix for dictionaries of uniform objects. The first column becomes the key.

```
environments{}
  region replicas debug
  production eu-central-1 6 False
  staging eu-central-1 2 True
```

For dictionaries of primitive arrays, use `{[]}` and skip the header row entirely:

```
user_roles{[]}
  "admin" 1 2 3
  "guest" 4 5
```

### 7. Hybrid Tabular-Inline (Semi-Uniform Data)

For arrays where rows share some keys but not all, ZEON uses the common keys as the header and appends the extra properties inline at the end of each row.

```
event_logs[]
  timestamp level message
  2026-08-17T10:00:00Z INFO "User logged in" user_id=405
  2026-08-17T10:01:00Z ERROR "DB Timeout" retry_count=3 context=(db=users)
```

### 8. Multiline Inline Objects and Arrays

`(...)` for objects, `[...]` for arrays. Indentation and line breaks inside them are ignored.

```
config=(
  db_pool=(
    host=localhost
    port=5432
    options=(
      ssl=True
      timeout=30
    )
  )
  nodes=[
    192.168.0.1
    192.168.0.2
  ]
)
```

### 9. Mixed Data Fallback

For irregular arrays with no common schema, ZEON uses inline notation:

```
mixed_data=[1 "hello" (flag=True) [2 3]]
```

`[]` for arrays, `()` for inline objects — no commas, no quotes where unnecessary.

### 10. Visual Annotations (Ignored by Parser)

Add `[label]` annotations to column headers for human readability. The parser ignores them completely.

```
users[]
  id[Number] name preferences(theme) aliases[]
  1 Maria (light) [mary mah]
```

---

## Using ZEON with LLMs

Include a brief reference block in your **System Prompt** so the model knows how to generate ZEON output.

> **Does the reference block eat into my savings?**
> The block below costs ~120 tokens — a fixed, one-time overhead recovered after just 4–5 data rows. Any response with 10+ rows is already net-positive. The more rows, the greater the gain.

```text
Return all structured data strictly in ZEON format.
ZEON uses tabular indentation: declare a header once, list data below it.
Suffixes: [] = array of objects, {} = keyed dict, () = inline object, [2]/[3] = matrices.
No JSON braces, no commas, no repeated keys.

<reference.zeon>
project_name="ZEON Demo"
is_active=True

# Flat objects use indentation
config
  timeout retries
  30 5

# Tabular arrays: first indented line is the header
users[]
  id name preferences(theme)
  1 "Alice" (dark)
  2 "Bob" (light)

# Extra dynamic attributes go inline at the end of the row
logs[]
  level message
  INFO "System started" timestamp=2026-08-18T10:00:00Z
  ERROR "DB Failed" retry=True
</reference.zeon>
```

This single example is sufficient for GPT-4, Claude, and Gemini to generate valid ZEON for any data shape.

> **Pro Tip:** For complex schemas, convert one of your own JSON files first: `zeon convert data.json --print`. Use that output as the reference — the model will replicate your exact schema perfectly.

---

## Performance Benchmarks

![Ecosystem Savings](vscode-zeon/icons/ecosystem-savings.png)

Benchmarked against 8 real-world dataset shapes using the `cl100k_base` tokenizer (GPT-4 / tiktoken):

| Dataset | Tabular Eligibility | JSON Compact | YAML | **ZEON** | vs JSON | vs YAML |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: |
| Employee Records (100 rows, flat) | 100% | 2,804 | 3,702 | **1,709** | `-39.1%` | `-53.8%` |
| GitHub Repositories (30 rows, flat) | 100% | 2,083 | 2,461 | **1,188** | `-43.0%` | `-51.7%` |
| Time-series Analytics (60 rows, flat) | 100% | 2,332 | 2,870 | **1,498** | `-35.8%` | `-47.8%` |
| Contacts with nested address (50 rows) | 100% | 2,603 | 3,302 | **1,716** | `-34.1%` | `-48.0%` |
| E-commerce Orders (50 rows, nested) | 33% | 4,933 | 6,220 | **3,581** | `-27.4%` | `-42.4%` |
| Feature Flags (40 keys, keyed map) | 100% | 825 | 963 | **487** | `-41.0%` | `-49.4%` |
| Semi-uniform Event Logs (75 rows) | 50% | 2,944 | 3,617 | **2,303** | `-21.8%` | `-36.3%` |
| Deeply Nested Config (worst case) | 0% | 137 | 173 | **105** | `-23.4%` | `-39.3%` |
| **TOTAL** | — | **18,661** | **23,308** | **12,587** | **`-32.5%`** | **`-46.0%`** |

On 100% tabular data, ZEON achieves up to **-43%** vs minified JSON and **-53%** vs YAML. Even in the worst-case deeply-nested scenario, ZEON never uses more tokens than JSON.

---

## Developer Tooling

The **Official VS Code Extension** provides a full editing experience for `.zeon` files:

- **Syntax Highlighting** — colorization for tables, matrices, primitives, and inline objects.
- **Real-time Linter** — catches syntax errors and incorrect suffixes as you type.
- **Interactive Live Preview** — renders your file as a visual grid. Edit values directly in the grid and press `Ctrl+S` to write changes back to the file.

Install from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=FallenBR.zeon-vscode) or [Open VSX](https://open-vsx.org/extension/FallenBR/zeon-vscode).

---

## CLI Reference

Convert between ZEON, JSON, and YAML from the command line:

```bash
# JSON / YAML -> ZEON
zeon convert data.json -> data.zeon
zeon convert config.yaml -> config.zeon

# ZEON -> JSON / YAML
zeon convert data.zeon -> data.json
zeon convert data.zeon -> data.yaml

# Print to stdout (useful for piping or previewing)
zeon convert data.json --print
```

---

*ZEON — Less tokens. Same data. Lower costs.*

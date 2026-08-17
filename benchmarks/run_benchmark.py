"""
Benchmark completo ZEON vs JSON vs YAML.
Usa datasets reais e representativos para gerar resultados de README.
Roda com: python benchmarks/run_benchmark.py
"""
import json
import yaml
import tiktoken
import os
import sys
import random
import string

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zeon.stringify import dumps as zeon_dumps

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# ---------------------------------------------------------------
# DATASETS REAIS E REPRESENTATIVOS
# ---------------------------------------------------------------

def dataset_ecommerce_orders():
    """E-commerce orders with nested structures (50 records)."""
    random.seed(42)
    statuses = ["pending", "shipped", "delivered", "cancelled"]
    categories = ["electronics", "clothing", "books", "home", "sports"]
    orders = []
    for i in range(50):
        orders.append({
            "order_id": f"ORD-{10000 + i}",
            "customer": {
                "id": 1000 + i,
                "name": f"Customer {i}",
                "email": f"user{i}@example.com"
            },
            "status": statuses[i % 4],
            "total": round(random.uniform(9.99, 999.99), 2),
            "items": [
                {"sku": f"SKU-{100+j}", "qty": random.randint(1, 5), "price": round(random.uniform(9.99, 199.99), 2)}
                for j in range(random.randint(1, 3))
            ],
            "shipping": {
                "method": "express" if i % 3 == 0 else "standard",
                "days": 1 if i % 3 == 0 else 5
            },
            "created_at": f"2026-{(i%12)+1:02d}-{(i%28)+1:02d}T10:00:00Z"
        })
    return {"orders": orders}


def dataset_employee_records():
    """Uniform employee records (100 records) - best case for tabular."""
    random.seed(42)
    depts = ["engineering", "marketing", "sales", "support", "finance"]
    employees = []
    for i in range(100):
        employees.append({
            "id": 1000 + i,
            "name": f"Employee {i}",
            "department": depts[i % 5],
            "salary": 50000 + (i * 500),
            "active": i % 7 != 0,
            "level": (i % 5) + 1
        })
    return {"employees": employees}


def dataset_github_repos():
    """Top GitHub repositories (uniform, 30 records)."""
    random.seed(42)
    langs = ["Python", "JavaScript", "Go", "Rust", "TypeScript", "Java"]
    repos = []
    for i in range(30):
        repos.append({
            "id": 100000 + i,
            "name": f"repo-{i}",
            "full_name": f"org{i}/repo-{i}",
            "language": langs[i % len(langs)],
            "stars": random.randint(1000, 200000),
            "forks": random.randint(100, 20000),
            "open_issues": random.randint(0, 500),
            "is_fork": False,
            "archived": i % 15 == 0,
            "created_at": f"2018-0{(i%9)+1}-01T00:00:00Z"
        })
    return {"repositories": repos}


def dataset_time_series():
    """Time-series analytics data (60 records)."""
    random.seed(42)
    metrics = []
    for i in range(60):
        metrics.append({
            "date": f"2026-{(i//30)+1:02d}-{(i%30)+1:02d}",
            "views": random.randint(1000, 15000),
            "clicks": random.randint(50, 800),
            "conversions": random.randint(1, 50),
            "revenue": round(random.uniform(100.0, 5000.0), 2),
            "bounce_rate": round(random.uniform(0.2, 0.8), 2)
        })
    return {"metrics": metrics}


def dataset_feature_flags():
    """Feature flags keyed by name (40 items)."""
    random.seed(42)
    flags = {}
    for i in range(40):
        flags[f"feature_{chr(65 + i % 26)}_{i}"] = {
            "enabled": i % 3 != 0,
            "rollout": round(random.uniform(0.0, 1.0), 2),
            "env": "production" if i % 2 == 0 else "staging"
        }
    return {"feature_flags": flags}


def dataset_deep_config():
    """Deeply nested configuration (worst case for ZEON)."""
    return {
        "app": {
            "name": "MyApp",
            "version": "2.0.0",
            "debug": False,
            "database": {
                "primary": {
                    "host": "db-primary.internal",
                    "port": 5432,
                    "name": "myapp_prod",
                    "pool": {
                        "min": 5,
                        "max": 20,
                        "idle_timeout": 600
                    }
                },
                "replica": {
                    "host": "db-replica.internal",
                    "port": 5432,
                    "name": "myapp_prod",
                    "pool": {
                        "min": 2,
                        "max": 10,
                        "idle_timeout": 300
                    }
                }
            },
            "cache": {
                "backend": "redis",
                "host": "redis.internal",
                "port": 6379,
                "ttl": 3600
            },
            "features": {
                "signup": True,
                "oauth": True,
                "two_factor": False,
                "api_v2": True
            }
        }
    }


def dataset_contacts():
    """Contacts with nested address and plan (50 records)."""
    random.seed(42)
    plans = ["free", "pro", "enterprise"]
    contacts = []
    for i in range(50):
        contacts.append({
            "id": i + 1,
            "name": f"Contact {i}",
            "email": f"contact{i}@example.com",
            "phone": f"+1-555-{1000 + i:04d}",
            "plan": plans[i % 3],
            "address": {
                "street": f"{100 + i} Main St",
                "city": "New York",
                "country": "US"
            },
            "tags": ["vip"] if i % 5 == 0 else ["regular"]
        })
    return {"contacts": contacts}


def dataset_semi_uniform_events():
    """Semi-uniform event logs (75 records) - mixed structure."""
    random.seed(42)
    event_types = ["login", "purchase", "error", "signup", "logout"]
    events = []
    for i in range(75):
        ev_type = event_types[i % 5]
        base = {
            "id": i + 1,
            "type": ev_type,
            "timestamp": f"2026-08-{(i%30)+1:02d}T{i%24:02d}:00:00Z",
            "user_id": 1000 + (i % 20)
        }
        # Semi-uniform: extra fields per type
        if ev_type == "purchase":
            base["amount"] = round(random.uniform(10, 500), 2)
            base["product_id"] = f"P-{100 + i}"
        elif ev_type == "error":
            base["code"] = 500
            base["message"] = "Internal server error"
            base["stack_trace"] = f"Error at line {random.randint(1, 300)}"
        elif ev_type == "login":
            base["ip"] = f"192.168.1.{i % 255}"
            base["success"] = i % 7 != 0
        events.append(base)
    return {"events": events}


# ---------------------------------------------------------------
# BENCHMARKING ENGINE
# ---------------------------------------------------------------

DATASETS = [
    ("Employee Records (100, uniform flat)", dataset_employee_records, "100%"),
    ("E-commerce Orders (50, nested)", dataset_ecommerce_orders, "33%"),
    ("Time-series Analytics (60, uniform flat)", dataset_time_series, "100%"),
    ("GitHub Repositories (30, uniform flat)", dataset_github_repos, "100%"),
    ("Contacts with Address (50, nested)", dataset_contacts, "100%"),
    ("Feature Flags (40, keyed map)", dataset_feature_flags, "100%"),
    ("Semi-uniform Event Logs (75, mixed)", dataset_semi_uniform_events, "50%"),
    ("Deeply Nested Config (1, deep)", dataset_deep_config, "0%"),
]


def bar(tok, max_tok, width=20):
    filled = int((tok / max_tok) * width) if max_tok > 0 else 0
    return "#" * filled + "." * (width - filled)


def run():
    print("=" * 80)
    print("ZEON BENCHMARK vs JSON vs YAML")
    print("Tokenizer: cl100k_base (GPT-4 / tiktoken)")
    print("=" * 80)

    all_results = []
    total_json = total_yaml = total_zeon = 0

    for name, generator, eligibility in DATASETS:
        data = generator()

        json_str = json.dumps(data, separators=(',', ':'))
        json_pretty_str = json.dumps(data, indent=2)
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
        zeon_str = zeon_dumps(data)

        j_tok = count_tokens(json_str)
        jp_tok = count_tokens(json_pretty_str)
        y_tok = count_tokens(yaml_str)
        z_tok = count_tokens(zeon_str)

        vs_json = (z_tok - j_tok) / j_tok * 100
        vs_yaml = (z_tok - y_tok) / y_tok * 100
        vs_jp   = (z_tok - jp_tok) / jp_tok * 100

        total_json += j_tok
        total_yaml += y_tok
        total_zeon += z_tok

        all_results.append({
            "name": name,
            "eligibility": eligibility,
            "json_compact": j_tok,
            "json_pretty": jp_tok,
            "yaml": y_tok,
            "zeon": z_tok,
            "vs_json_compact": vs_json,
            "vs_json_pretty": vs_jp,
            "vs_yaml": vs_yaml,
            "zeon_text": zeon_str,
            "json_pretty_text": json_pretty_str,
        })

    # --- Console output ---
    max_tok = max(r["json_pretty"] for r in all_results)

    for r in all_results:
        print(f"\n{'-'*60}")
        print(f"  {r['name']}  |  Tabular Eligibility: {r['eligibility']}")
        print(f"{'-'*60}")
        j_b  = bar(r["json_compact"], max_tok)
        jp_b = bar(r["json_pretty"], max_tok)
        y_b  = bar(r["yaml"], max_tok)
        z_b  = bar(r["zeon"], max_tok)
        print(f"  ZEON         {z_b}  {r['zeon']:>7} tokens")
        print(f"  JSON compact {j_b}  {r['json_compact']:>7} tokens  ({r['vs_json_compact']:+.1f}% vs ZEON)")
        print(f"  JSON pretty  {jp_b}  {r['json_pretty']:>7} tokens  ({r['vs_json_pretty']:+.1f}% vs ZEON)")
        print(f"  YAML         {y_b}  {r['yaml']:>7} tokens  ({r['vs_yaml']:+.1f}% vs ZEON)")

    # --- Totals ---
    print(f"\n{'='*60}")
    print(f"  TOTALS (all {len(DATASETS)} datasets combined)")
    print(f"{'='*60}")
    vs_json_total  = (total_zeon - total_json) / total_json * 100
    vs_yaml_total  = (total_zeon - total_yaml) / total_yaml * 100
    print(f"  ZEON total:         {total_zeon:>7} tokens")
    print(f"  JSON compact total: {total_json:>7} tokens  ({vs_json_total:+.1f}% vs ZEON)")
    print(f"  YAML total:         {total_yaml:>7} tokens  ({vs_yaml_total:+.1f}% vs ZEON)")
    print(f"{'='*60}")

    # --- Save markdown report ---
    _save_markdown(all_results, total_json, total_yaml, total_zeon)

    # --- Save ZEON examples for README ---
    _save_examples(all_results)


def _save_markdown(results, total_json, total_yaml, total_zeon):
    vs_json_total = (total_zeon - total_json) / total_json * 100
    vs_yaml_total = (total_zeon - total_yaml) / total_yaml * 100

    lines = []
    lines.append("# ZEON Benchmark Results\n")
    lines.append("> Generated automatically. Tokenizer: `cl100k_base` (GPT-4 / tiktoken)\n")

    lines.append("## Token Efficiency Summary\n")
    lines.append("| Dataset | Tabular | JSON (compact) | YAML | **ZEON** | vs JSON | vs YAML |")
    lines.append("| :--- | :---: | ---: | ---: | ---: | ---: | ---: |")
    for r in results:
        lines.append(
            f"| {r['name']} | {r['eligibility']} | {r['json_compact']:,} | {r['yaml']:,} | **{r['zeon']:,}** | "
            f"`{r['vs_json_compact']:+.1f}%` | `{r['vs_yaml']:+.1f}%` |"
        )

    lines.append(f"\n**TOTAL** | | {total_json:,} | {total_yaml:,} | **{total_zeon:,}** | "
                 f"`{vs_json_total:+.1f}%` | `{vs_yaml_total:+.1f}%`\n")

    lines.append("\n## Detailed Token Counts per Dataset\n")
    max_tok = max(r["json_pretty"] for r in results)
    for r in results:
        lines.append(f"### {r['name']}")
        lines.append(f"> Tabular eligibility: {r['eligibility']}\n")
        z_b = bar(r['zeon'], max_tok)
        j_b = bar(r['json_compact'], max_tok)
        y_b = bar(r['yaml'], max_tok)
        lines.append(f"```")
        lines.append(f"ZEON         {z_b}  {r['zeon']:>7} tokens")
        lines.append(f"JSON compact {j_b}  {r['json_compact']:>7} tokens  ({r['vs_json_compact']:+.1f}% vs ZEON)")
        lines.append(f"YAML         {y_b}  {r['yaml']:>7} tokens  ({r['vs_yaml']:+.1f}% vs ZEON)")
        lines.append(f"```\n")

    out_path = os.path.join(os.path.dirname(__file__), 'results', 'benchmark_results.md')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\nMarkdown report saved: {out_path}")


def _save_examples(results):
    """Save side-by-side JSON vs ZEON examples for the best 2 cases (highest reduction)."""
    sorted_r = sorted(results, key=lambda x: x["vs_json_compact"])
    best = sorted_r[0]

    example_path = os.path.join(os.path.dirname(__file__), 'results', 'best_example.md')
    os.makedirs(os.path.dirname(example_path), exist_ok=True)

    # Take only first 3 records of the JSON for brevity
    try:
        data_snippet = json.loads('{}')
    except Exception:
        pass

    content = [
        f"# Best ZEON Example: {best['name']}",
        f"\n> Tabular eligibility: {best['eligibility']} | ZEON saves `{best['vs_json_compact']:.1f}%` vs JSON compact\n",
        "## JSON (compact)",
        f"Tokens: **{best['json_compact']:,}**\n",
        "## ZEON",
        f"Tokens: **{best['zeon']:,}**\n",
        "```",
        best["zeon_text"][:2000] + ("..." if len(best["zeon_text"]) > 2000 else ""),
        "```",
    ]
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    print(f"Best example saved: {example_path}")


if __name__ == "__main__":
    run()

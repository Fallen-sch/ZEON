import json
import yaml
import csv
import io
import tiktoken
import os
import sys

# Import our ZEON dumps function
sys.path.append(r"c:\Users\evera\projects\lion")
from zeon import dumps as zeon_dumps

def dict_to_xml(tag, d):
    elem = f"<{tag}>"
    if isinstance(d, dict):
        for key, val in d.items():
            elem += dict_to_xml(key, val)
    elif isinstance(d, list):
        for item in d:
            elem += dict_to_xml("item", item)
    else:
        elem += str(d)
    elem += f"</{tag}>"
    return elem

# Ensure output dir exists
out_dir = r"c:\Users\evera\projects\lion\benchmark_datasets"
os.makedirs(out_dir, exist_ok=True)

# Datasets
datasets = []

# 1. Employee Records (100 rows)
ds1 = []
for i in range(1, 101):
    ds1.append({
        "id": i,
        "name": f"Employee_{i}",
        "role": "Developer" if i % 2 == 0 else "Designer",
        "department": "Engineering" if i % 2 == 0 else "Design",
        "salary": 50000 + (i * 1000)
    })
datasets.append({"name": "employee_records_100", "title": "Employee Records (100)", "sub": "uniform-flat", "data": ds1})

# 2. GitHub Repos (30 items)
ds2 = []
for i in range(1, 31):
    ds2.append({
        "repo": f"Project_X{i}",
        "owner": {"login": f"user{i}", "type": "User"},
        "stars": i * 15,
        "tags": ["code", "python", f"tag{i}"]
    })
datasets.append({"name": "github_repos_30", "title": "GitHub Repositories (30)", "sub": "uniform-nested-uniform", "data": ds2})

# 3. Time Series Analytics (60 rows)
ds3 = []
for i in range(1, 61):
    ds3.append({
        "ts": 1600000000 + i*60,
        "metric": "cpu_usage",
        "value": round(10.0 + (i * 0.5), 2),
        "status": "OK" if i < 50 else "WARN"
    })
datasets.append({"name": "time_series_60", "title": "Time Series Analytics (60)", "sub": "uniform-flat", "data": ds3})

# 4. Contacts + Nested Address (50 rows)
ds4 = []
for i in range(1, 51):
    ds4.append({
        "contact_id": f"C_{i}",
        "email": f"user{i}@example.com",
        "address": {"city": f"City_{i}", "zip": f"{1000+i}", "country": "US"}
    })
datasets.append({"name": "contacts_address_50", "title": "Contacts + Nested Address (50)", "sub": "uniform-nested-uniform", "data": ds4})

# 5. E-commerce Orders (Mixed)
ds5 = {
    "metadata": {"version": 1.2, "export_date": "2023-10-01"},
    "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
    "orders": []
}
for i in range(1, 15):
    ds5["orders"].append({
        "order_id": f"ORD-{i}",
        "user_id": 1 if i % 2 != 0 else 2,
        "items": [{"sku": f"ITEM-{i}", "qty": i}, {"sku": f"ITEM-{i+10}", "qty": 1}],
        "total": i * 15.5
    })
datasets.append({"name": "ecommerce_orders", "title": "E-commerce Orders (Nested)", "sub": "nonuniform-nested-nonuniform", "data": ds5})

# 6. Deeply Nested Config
ds6 = {
    "server": {
        "host": "localhost",
        "port": 8080,
        "ssl": {
            "enabled": True,
            "cert": "/etc/ssl/cert.pem",
            "key": "/etc/ssl/key.pem",
            "options": {
                "verify_peer": False,
                "depth": 2
            }
        },
        "logging": {
            "level": "INFO",
            "file": "/var/log/app.log",
            "rotation": {
                "max_size": "10MB",
                "keep": 5
            }
        }
    },
    "database": {
        "url": "postgres://user:pass@localhost:5432/db",
        "pool": {
            "min": 2,
            "max": 10,
            "timeout": 3000
        }
    }
}
datasets.append({"name": "deeply_nested_config", "title": "Deeply Nested Config", "sub": "nonuniform-nested-nonuniform", "data": ds6})

# 7. User Sessions (80 rows)
ds7 = [{"session": f"S{i}", "duration": i*10, "browser": "Chrome", "events": i+5} for i in range(1, 81)]
datasets.append({"name": "user_sessions", "title": "User Sessions (80)", "sub": "uniform-flat", "data": ds7})

# 8. Weather API (7 days)
ds8 = [{"date": f"2023-10-0{i}", "temp": 20+i, "conditions": "Sunny"} for i in range(1, 8)]
datasets.append({"name": "weather_api", "title": "Weather API (7 days)", "sub": "uniform-flat", "data": ds8})

# 9. Product Catalog (40 items)
ds9 = [{"sku": f"PRD-{i}", "name": f"Product {i}", "price": round(9.99 * i, 2), "stock": i*5} for i in range(1, 41)]
datasets.append({"name": "product_catalog", "title": "Product Catalog (40)", "sub": "uniform-flat", "data": ds9})

# 10. Translation Strings
ds10 = {"en": {"hello": "Hello", "bye": "Goodbye"}, "pt": {"hello": "Olá", "bye": "Tchau"}, "es": {"hello": "Hola", "bye": "Adiós"}}
datasets.append({"name": "translation_strings", "title": "Translation Strings", "sub": "uniform-nested-uniform", "data": ds10})

# 11. Financial Transactions (50)
ds11 = [{"txid": f"TXN{i}", "amt": i*100.5, "type": "CREDIT" if i%2==0 else "DEBIT", "status": "CLEARED"} for i in range(1, 51)]
datasets.append({"name": "financial_tx", "title": "Financial Transactions (50)", "sub": "uniform-flat", "data": ds11})

# 12. Sensor Telemetry (100)
ds12 = [{"id": i, "x": i*0.1, "y": i*0.2, "z": i*0.3} for i in range(1, 101)]
datasets.append({"name": "sensor_telemetry", "title": "Sensor Telemetry (100)", "sub": "uniform-flat", "data": ds12})

# 13. Chat Messages (30)
ds13 = [{"msg_id": i, "sender": "UserA" if i%2==0 else "UserB", "text": f"This is message {i}"} for i in range(1, 31)]
datasets.append({"name": "chat_messages", "title": "Chat Messages (30)", "sub": "uniform-flat", "data": ds13})

# 14. Vector Embeddings (10 vectors of size 5)
ds14 = [{"id": f"vec_{i}", "emb": [i*0.1, i*0.2, i*0.3, i*0.4, i*0.5]} for i in range(1, 11)]
datasets.append({"name": "vector_embeddings", "title": "Vector Embeddings (10)", "sub": "uniform-nested-uniform", "data": ds14})

# 15. GeoJSON Polygons (5)
ds15 = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [i, i*2]}} for i in range(1, 6)]}
datasets.append({"name": "geojson_points", "title": "GeoJSON Points (5)", "sub": "uniform-nested-uniform", "data": ds15})

# 16. Server Health Check
ds16 = {"status": "up", "checks": {"cpu": "ok", "mem": "ok", "disk": "warn"}, "uptime": 123456}
datasets.append({"name": "health_check", "title": "Server Health Check", "sub": "uniform-nested-nonuniform", "data": ds16})

# Setup tokenizer
enc = tiktoken.get_encoding("cl100k_base")

def get_tokens(text):
    if text is None: return "N/A"
    return len(enc.encode(text))

def to_csv_tsv(data, delimiter):
    if not isinstance(data, list):
        return None
    if len(data) == 0:
        return ""
    # Ensure it's uniform flat
    for item in data:
        for val in item.values():
            if isinstance(val, (dict, list)):
                return None
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys(), delimiter=delimiter)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

results = []

for d in datasets:
    name = d["name"]
    title = d["title"]
    sub = d["sub"]
    data = d["data"]
    
    # Generate formats
    pretty_json = json.dumps(data, indent=2)
    min_json = json.dumps(data, separators=(',', ':'))
    yml = yaml.dump(data, default_flow_style=False)
    csv_str = to_csv_tsv(data, ',')
    tsv_str = to_csv_tsv(data, '\t')
    xml_str = dict_to_xml("root", data)
    try:
        zeon_str = zeon_dumps(data)
    except Exception as e:
        print(f"Error dumping zeon for {name}: {e}")
        zeon_str = ""
        
    # Save to files
    with open(os.path.join(out_dir, f"{name}.json"), "w") as f: f.write(pretty_json)
    with open(os.path.join(out_dir, f"{name}.yaml"), "w") as f: f.write(yml)
    if csv_str:
        with open(os.path.join(out_dir, f"{name}.csv"), "w") as f: f.write(csv_str)
        with open(os.path.join(out_dir, f"{name}.tsv"), "w") as f: f.write(tsv_str)
    with open(os.path.join(out_dir, f"{name}.xml"), "w") as f: f.write(xml_str)
    with open(os.path.join(out_dir, f"{name}.zeon"), "w") as f: f.write(zeon_str)
        
    # Tokens
    tok_pretty = get_tokens(pretty_json)
    tok_min = get_tokens(min_json)
    tok_yaml = get_tokens(yml)
    tok_csv = get_tokens(csv_str)
    tok_tsv = get_tokens(tsv_str)
    tok_xml = get_tokens(xml_str)
    tok_zeon = get_tokens(zeon_str)
    
    def format_res(tok, baseline):
        if tok == "N/A": return {"tokens": "N/A", "pct": ""}
        diff = ((tok - baseline) / baseline) * 100
        sign = "+" if diff > 0 else ""
        return {"tokens": str(tok), "pct": f"{sign}{diff:.1f}%"}
        
    results.append({
        "dataset": title,
        "sub": sub,
        "pretty_json": {"tokens": str(tok_pretty), "pct": "baseline"},
        "json": format_res(tok_min, tok_pretty),
        "yaml": format_res(tok_yaml, tok_pretty),
        "csv": format_res(tok_csv, tok_pretty) if tok_csv != "N/A" else {"tokens": "N/A", "pct": ""},
        "tsv": format_res(tok_tsv, tok_pretty) if tok_tsv != "N/A" else {"tokens": "N/A", "pct": ""},
        "tson": format_res(tok_zeon, tok_pretty),
        "xml": format_res(tok_xml, tok_pretty),
        "slim": {"tokens": "N/A", "pct": ""} # not supported in this script, will just hide
    })

# Write the JSON array for Benchmarks.tsx
with open(os.path.join(out_dir, "benchmarkData.json"), "w") as f:
    json.dump(results, f, indent=2)

print("Datasets and token counts generated successfully.")

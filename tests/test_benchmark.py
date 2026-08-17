import json
import yaml
import tiktoken
import os
import random
import string
import sys

# Add parent dir to path so we can import lion
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lion.stringify import dumps as lion_dumps

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# Dataset generators
def rand_str(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_uniform_flat(size):
    count = 5 if size == 'small' else 50 if size == 'medium' else 500
    return [{"id": i, "name": rand_str(), "role": "user", "active": True, "score": random.randint(0, 100)} for i in range(count)]

def generate_non_uniform_flat(size):
    count = 5 if size == 'small' else 20 if size == 'medium' else 100
    data = {}
    for i in range(count):
        data[f"key_{i}"] = rand_str()
        if i % 2 == 0:
            data[f"num_{i}"] = i * 10
        if i % 3 == 0:
            data[f"flag_{i}"] = True
    return data

def generate_uniform_nested_uniform(size):
    count = 5 if size == 'small' else 50 if size == 'medium' else 500
    return [
        {"id": i, "prefs": {"theme": "dark", "lang": "en"}, "stats": {"logins": i, "errors": 0}}
        for i in range(count)
    ]

def generate_uniform_nested_nonuniform(size):
    count = 5 if size == 'small' else 50 if size == 'medium' else 500
    res = []
    for i in range(count):
        meta = {"last_login": "2026-08-16"}
        if i % 2 == 0:
            meta["visits"] = i
            meta["source"] = "organic"
        res.append({"id": i, "meta": meta})
    return res

def generate_nonuniform_nested_nonuniform(size):
    count = 5 if size == 'small' else 20 if size == 'medium' else 100
    data = {}
    for i in range(count):
        data[f"user_{i}"] = {"a": i, "b": {"c": i*2} if i%2==0 else [1,2,3]}
    data["global_config"] = {"host": "localhost", "ports": [80, 443]}
    return data

def generate_nonuniform_nested_uniform(size):
    count = 5 if size == 'small' else 50 if size == 'medium' else 500
    return {
        "status": "success",
        "metadata": {"timestamp": "2026-08-16T14:30:00Z", "server": "us-east-1"},
        "data": [{"id": i, "score": random.randint(0, 100)} for i in range(count)]
    }

def generate_html_report(results):
    html = '''
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #111; color: #fff; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
        </style>
    </head>
    <body class="p-8">
        <h1 class="text-3xl font-bold mb-6 text-center">LION Benchmark vs JSON & YAML</h1>
        <div class="overflow-x-auto border border-gray-800 rounded-lg shadow-2xl">
            <table class="w-full text-sm text-left">
                <thead class="bg-gray-900 border-b border-gray-800">
                    <tr>
                        <th class="p-4 text-gray-400 font-semibold">Dataset</th>
                        <th class="p-4 text-center text-gray-400 font-semibold">JSON Compact</th>
                        <th class="p-4 text-center text-gray-400 font-semibold">YAML</th>
                        <th class="p-4 text-center text-blue-400 font-bold">LION</th>
                    </tr>
                </thead>
                <tbody>
    '''
    
    for r in results:
        j_tok = r['json_tok']
        y_tok = r['yaml_tok']
        l_tok = r['lion_tok']
        
        lion_vs_json = (l_tok - j_tok) / j_tok * 100 if j_tok > 0 else 0
        lion_vs_yaml = (l_tok - y_tok) / y_tok * 100 if y_tok > 0 else 0
        
        html += f'''
                <tr class="border-b border-gray-800 hover:bg-gray-800/50">
                    <td class="p-4">
                        <div class="font-bold text-white text-base">{r['size'].capitalize()}</div>
                        <div class="text-xs text-gray-500 mt-1">{r['type']}</div>
                    </td>
                    <td class="p-4 text-center">
                        <div class="font-mono text-lg">{j_tok}</div>
                        <div class="text-[10px] text-gray-500 mt-1">baseline</div>
                    </td>
                    <td class="p-4 text-center border-l border-gray-800/50">
                        <div class="font-mono text-lg text-gray-300">{y_tok}</div>
                        <div class="text-[10px] text-gray-500 mt-1">baseline</div>
                    </td>
                    <td class="p-4 text-center bg-blue-900/10 border-l border-gray-800">
                        <div class="font-mono font-bold text-xl text-blue-300">{l_tok}</div>
                        <div class="flex justify-center gap-2 mt-2">
                            <div class="text-xs text-green-400 font-bold bg-gray-900 px-2 py-1 rounded border border-gray-700">{lion_vs_json:+.1f}% vs JSON</div>
                            <div class="text-xs text-green-400 font-bold bg-gray-900 px-2 py-1 rounded border border-gray-700">{lion_vs_yaml:+.1f}% vs YAML</div>
                        </div>
                    </td>
                </tr>
        '''
        
    html += '''
                </tbody>
            </table>
        </div>
    </body>
    </html>
    '''
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'benchmarks'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'benchmarks', 'comparative.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Report generated at {out_path}")


def run_benchmarks():
    random.seed(42) # For reproducible datasets
    
    sizes = ['small', 'medium', 'large']
    types = [
        ('uniform-flat', generate_uniform_flat),
        ('non-uniform-flat', generate_non_uniform_flat),
        ('uniform-nested-uniform', generate_uniform_nested_uniform),
        ('uniform-nested-nonuniform', generate_uniform_nested_nonuniform),
        ('nonuniform-nested-nonuniform', generate_nonuniform_nested_nonuniform),
        ('nonuniform-nested-uniform', generate_nonuniform_nested_uniform)
    ]
    
    results = []
    
    print(f"{'Dataset':<40} | {'JSON':<8} | {'YAML':<8} | {'LION':<8} | {'% vs JSON':<10}")
    print("-" * 85)
    
    for size in sizes:
        for t_name, generator in types:
            data = generator(size)
            
            json_str = json.dumps(data, separators=(',', ':'))
            yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
            lion_str = lion_dumps(data)
            
            j_tok = count_tokens(json_str)
            y_tok = count_tokens(yaml_str)
            l_tok = count_tokens(lion_str)
            
            red_j = (l_tok - j_tok) / j_tok * 100 if j_tok > 0 else 0
            
            print(f"{size + ' ' + t_name:<40} | {j_tok:<8} | {y_tok:<8} | {l_tok:<8} | {red_j:<+.1f}%")
            
            results.append({
                'size': size,
                'type': t_name,
                'json_tok': j_tok,
                'yaml_tok': y_tok,
                'lion_tok': l_tok
            })
            
    generate_html_report(results)

if __name__ == "__main__":
    run_benchmarks()

"""
Analise completa de conversao ZEON - testa todos os casos criticos de roundtrip.
Roda com: python tests/analysis/test_roundtrip_analysis.py
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from zeon.stringify import dumps
from zeon.parse import loads

PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"

results = []

def roundtrip(name: str, data: dict):
    """Converte dict -> ZEON -> dict e verifica se o resultado e identico ao original."""
    try:
        zeon_text = dumps(data)
        recovered = loads(zeon_text)
        if recovered == data:
            results.append((PASS, name, zeon_text))
        else:
            results.append((FAIL, name, f"ORIGINAL:\n{json.dumps(data, indent=2)}\n\nZEON:\n{zeon_text}\n\nRECOVERED:\n{json.dumps(recovered, indent=2)}"))
    except Exception as e:
        results.append((FAIL, name, f"EXCECAO: {type(e).__name__}: {e}"))


# ------------------------------------------------------------------
# CASOS 1: Primitivos simples
# ------------------------------------------------------------------
roundtrip("string simples", {"key": "value"})
roundtrip("string com espacos", {"key": "hello world"})
roundtrip("string vazia", {"key": ""})
roundtrip("inteiro", {"key": 42})
roundtrip("float", {"key": 3.14})
roundtrip("booleano True", {"key": True})
roundtrip("booleano False", {"key": False})
roundtrip("null / None", {"key": None})
roundtrip("string que parece numero", {"key": "123"})
roundtrip("string que parece booleano", {"key": "true"})
roundtrip("string com aspas duplas internas", {"key": 'diga "ola"'})
roundtrip("url com dois pontos", {"key": "https://example.com"})
roundtrip("data ISO", {"key": "2026-08-17T14:30:00Z"})

# ------------------------------------------------------------------
# CASOS 2: Dicts planos
# ------------------------------------------------------------------
roundtrip("dict plano multiplas chaves", {"a": 1, "b": "texto", "c": True, "d": None})
roundtrip("dict com chave numerica", {"1": "um", "2": "dois"})

# ------------------------------------------------------------------
# CASOS 3: Listas simples (1D)
# ------------------------------------------------------------------
roundtrip("lista de strings", {"tags": ["alpha", "beta", "gamma"]})
roundtrip("lista de inteiros", {"ids": [1, 2, 3, 4]})
roundtrip("lista de floats", {"coords": [1.1, 2.2, 3.3]})
roundtrip("lista mista primitivos", {"mixed": [1, "dois", True, None]})
roundtrip("lista vazia", {"items": []})
roundtrip("lista com string vazia", {"items": ["", "ok"]})
roundtrip("lista com string que parece numero", {"items": ["1", "2", "3"]})

# ------------------------------------------------------------------
# CASOS 4: Matrizes 2D (lista de listas de primitivos)
# ------------------------------------------------------------------
roundtrip("matriz 2d inteiros", {"grid": [[1, 2], [3, 4]]})
roundtrip("matriz 2d floats", {"coords": [[-23.5, -46.6], [-22.9, -43.1]]})
roundtrip("matriz 2d 3 colunas", {"tensor": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]})

# ------------------------------------------------------------------
# CASOS 5: Lista uniforme de dicts (tabular)
# ------------------------------------------------------------------
roundtrip("tabela simples 2 colunas", {"users": [{"id": 1, "name": "Ana"}, {"id": 2, "name": "Bob"}]})
roundtrip("tabela com bool e null", {"items": [{"x": True, "y": None}, {"x": False, "y": 42}]})
roundtrip("tabela com float", {"products": [{"sku": "A1", "price": 9.99}, {"sku": "B2", "price": 14.5}]})
roundtrip("tabela com lista inline", {
    "users": [
        {"id": 1, "tags": ["admin", "user"]},
        {"id": 2, "tags": ["guest"]},
    ]
})

# ------------------------------------------------------------------
# CASOS 6: Dicts aninhados (objetos dentro de tabelas)
# ------------------------------------------------------------------
roundtrip("tabela com dict plano aninhado (tupla)", {
    "users": [
        {"id": 1, "prefs": {"theme": "dark", "lang": "pt"}},
        {"id": 2, "prefs": {"theme": "light", "lang": "en"}},
    ]
})

# ------------------------------------------------------------------
# CASOS 7: Dicts profundamente aninhados
# ------------------------------------------------------------------
roundtrip("dict profundamente aninhado", {
    "a": {"b": {"c": {"d": 42}}}
})
roundtrip("dict com lista e sub-dict", {
    "config": {
        "db": {"host": "localhost", "port": 5432},
        "servers": ["192.168.0.1", "192.168.0.2"]
    }
})

# ------------------------------------------------------------------
# CASOS 8: Listas mistas (fallback inline)
# ------------------------------------------------------------------
roundtrip("lista com dict e primitivo", {"data": [1, {"flag": True}, "ok"]})
roundtrip("lista com sub-lista e dict", {"data": [[1, 2], {"a": 1}]})

# ------------------------------------------------------------------
# CASOS 9: Edge cases de chaves especiais
# ------------------------------------------------------------------
roundtrip("chave com underscores", {"my_key_name": "value"})
roundtrip("chave com numeros no meio", {"key2value": 10})
roundtrip("multiplos campos raiz", {"name": "ZEON", "version": "0.1.0", "stable": True})

# ------------------------------------------------------------------
# CASOS 10: Listas de listas de dicts (3D misto)
# ------------------------------------------------------------------
roundtrip("lista uniforme nao-aninhada com sub-dict aninhado complexo", {
    "matrix_of_groups": [
        [{"node": "A1", "active": True}, {"node": "A2", "active": False}],
        [{"node": "B1", "active": True}, {"node": "B2", "active": True}]
    ]
})

# ------------------------------------------------------------------
# IMPRIME O RELATORIO FINAL
# ------------------------------------------------------------------
passes = [r for r in results if r[0] == PASS]
fails = [r for r in results if r[0] == FAIL]

print("=" * 60)
print(f"RELATORIO DE ANALISE ZEON ROUNDTRIP")
print(f"Total: {len(results)}  |  PASS: {len(passes)}  |  FAIL: {len(fails)}")
print("=" * 60)

if fails:
    print("\n--- FALHAS DETECTADAS ---")
    for status, name, detail in fails:
        print(f"\n{FAIL} {name}")
        print(detail)

print("\n--- RESUMO ---")
for status, name, detail in results:
    if status == PASS:
        print(f"  {PASS} {name}")
    else:
        print(f"  {FAIL} {name}  <---")

print("\n" + "=" * 60)
if not fails:
    print("TODOS OS TESTES PASSARAM! ZEON esta 100% funcional para roundtrip.")
else:
    print(f"ATENCAO: {len(fails)} caso(s) precisam de revisao.")
print("=" * 60)

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import zeon

extreme_json = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extreme_cases.json'))
extreme_zeon = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extreme_cases.zeon'))

print(f"Lendo o JSON extremo: {extreme_json}")
with open(extreme_json, 'r', encoding='utf-8') as f:
    import json
    data = json.load(f)

print("Convertendo para ZEON...")
zeon_str = zeon.dumps(data)

print(f"Salvando em: {extreme_zeon}")
with open(extreme_zeon, 'w', encoding='utf-8') as f:
    f.write(zeon_str)

print("\n--- CONTEÚDO ZEON GERADO ---")
print(zeon_str)
print("----------------------------\n")

print("Verificando se o ZEON gerado é válido (Roundtrip de volta para JSON)...")
try:
    parsed_back = zeon.loads(zeon_str)
    if parsed_back == data:
        print("SUCESSO ABSOLUTO! O parser leu o ZEON de volta e o resultado é idêntico ao JSON original!")
    else:
        print("ERRO: O roundtrip falhou, os dados não são idênticos.")
except Exception as e:
    print(f"ERRO FATAL no Parser: {e}")

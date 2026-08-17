import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import lion

extreme_json = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extreme_cases.json'))
extreme_lion = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extreme_cases.lion'))

print(f"Lendo o JSON extremo: {extreme_json}")
with open(extreme_json, 'r', encoding='utf-8') as f:
    import json
    data = json.load(f)

print("Convertendo para LION...")
lion_str = lion.dumps(data)

print(f"Salvando em: {extreme_lion}")
with open(extreme_lion, 'w', encoding='utf-8') as f:
    f.write(lion_str)

print("\n--- CONTEÚDO LION GERADO ---")
print(lion_str)
print("----------------------------\n")

print("Verificando se o LION gerado é válido (Roundtrip de volta para JSON)...")
try:
    parsed_back = lion.loads(lion_str)
    if parsed_back == data:
        print("SUCESSO ABSOLUTO! O parser leu o LION de volta e o resultado é idêntico ao JSON original!")
    else:
        print("ERRO: O roundtrip falhou, os dados não são idênticos.")
except Exception as e:
    print(f"ERRO FATAL no Parser: {e}")

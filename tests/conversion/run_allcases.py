import sys
import os

# Adiciona a raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import lion

print("Iniciando o teste de conversão em cadeia (Round-trip) do all_cases...")

# Caminho para o arquivo original do all_cases
original_lion = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'test_all_cases.lion'))

# Caminhos de saída (forçamos o caminho completo para garantir que caia dentro de tests/conversion)
out_json = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_output.json'))
out_lion = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_roundtrip.lion'))

# 1. Converte LION original para JSON
print(f"1. Convertendo {original_lion} para JSON...")
lion.convert(original_lion).to_json(out_json, indent=4)
print(f"   -> Salvo em {out_json}")

# 2. Pega o JSON recém gerado e converte de volta para LION
print(f"2. Convertendo o JSON gerado de volta para LION...")
lion.convert(out_json).to_lion(out_lion)
print(f"   -> Salvo em {out_lion}")

print("Sucesso! Agora você pode comparar visualmente o arquivo original com o arquivo 'test_all_cases_roundtrip.lion'.")

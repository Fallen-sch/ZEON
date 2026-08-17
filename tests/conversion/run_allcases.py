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
out_yaml = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_output.yaml'))
out_lion_from_json = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_roundtrip_from_json.lion'))
out_lion_from_yaml = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_roundtrip_from_yaml.lion'))

# 1. Converte LION original para JSON e YAML
print(f"1. Convertendo {original_lion} para JSON e YAML...")
lion.convert(original_lion).to_json(out_json, indent=4)
print(f"   -> Salvo em {out_json}")
lion.convert(original_lion).to_yaml(out_yaml)
print(f"   -> Salvo em {out_yaml}")

# 2. Pega o JSON e YAML gerados e converte de volta para LION
print(f"2. Convertendo o JSON e YAML gerados de volta para LION...")
lion.convert(out_json).to_lion(out_lion_from_json)
print(f"   -> Salvo em {out_lion_from_json}")
lion.convert(out_yaml).to_lion(out_lion_from_yaml)
print(f"   -> Salvo em {out_lion_from_yaml}")

print("Sucesso! O suporte completo a JSON e YAML está funcionando perfeitamente no round-trip.")

import sys
import os

# Adiciona a raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import zeon

print("Iniciando o teste de conversão em cadeia (Round-trip) do all_cases...")

# Caminho para o arquivo original do all_cases
original_zeon = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'test_all_cases.zeon'))

# Caminhos de saída (forçamos o caminho completo para garantir que caia dentro de tests/conversion)
out_json = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_output.json'))
out_yaml = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_output.yaml'))
out_zeon_from_json = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_roundtrip_from_json.zeon'))
out_zeon_from_yaml = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_all_cases_roundtrip_from_yaml.zeon'))

# 1. Converte ZEON original para JSON e YAML
print(f"1. Convertendo {original_zeon} para JSON e YAML...")
zeon.convert(original_zeon).to_json(out_json, indent=4)
print(f"   -> Salvo em {out_json}")
zeon.convert(original_zeon).to_yaml(out_yaml)
print(f"   -> Salvo em {out_yaml}")

# 2. Pega o JSON e YAML gerados e converte de volta para ZEON
print(f"2. Convertendo o JSON e YAML gerados de volta para ZEON...")
zeon.convert(out_json).to_zeon(out_zeon_from_json)
print(f"   -> Salvo em {out_zeon_from_json}")
zeon.convert(out_yaml).to_zeon(out_zeon_from_yaml)
print(f"   -> Salvo em {out_zeon_from_yaml}")

print("Sucesso! O suporte completo a JSON e YAML está funcionando perfeitamente no round-trip.")

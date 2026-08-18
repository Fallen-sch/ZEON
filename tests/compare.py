import sys
import json
import os

sys.path.insert(0, r'c:\Users\evera\projects\lion')
import zeon

with open('tests/campeoes.json', encoding='utf-8') as f:
    json_data = json.load(f)

with open('tests/campeoes.zeon', encoding='utf-8') as f:
    zeon_text = f.read()

zeon_data = zeon.loads(zeon_text)

print('São EXATAMENTE iguais?', json_data == zeon_data)

if json_data != zeon_data:
    print("Diferenças detectadas! Salvando ambos em arquivos para diff...")
    with open('tests/campeoes_roundtrip.json', 'w', encoding='utf-8') as f:
        json.dump(zeon_data, f, indent=2, ensure_ascii=False)
    with open('tests/campeoes_original_normalized.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
else:
    print("JSON original e dados parseados do ZEON são 100% idênticos!")

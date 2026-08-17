import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import lion

json_data = """
{
  "users": [
    {
      "id": 1,
      "name": "Maria",
      "preferences": {
        "theme": "light",
        "notifications": true
      },
      "nicknames": {
        "1": "Mariazinha",
        "2": "Mariazinha",
        "3": {
          "4": "Mariazinha",
          "5": "Mariazinha"
        }
      }
    }
  ]
}
"""

try:
    lion_text = lion.convert(json_data).to_lion()
    print("=== LION GERADO COM SUCESSO ===")
    print(lion_text)
    print("===============================")
    
    print("\nVerificando Roundtrip...")
    parsed_data = lion.loads(lion_text)
    import json
    print(json.dumps(parsed_data, indent=2))

except Exception as e:
    print(f"ERRO AO CONVERTER: {e}")
    import traceback
    traceback.print_exc()

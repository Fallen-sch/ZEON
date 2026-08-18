import os
import sys

# Adiciona o diretório raiz (onde a pasta zeon está) ao PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

import zeon

def test_matrices_and_arrays():
    data = """
matriz2D[2]
  1 0
  0 1
  
matriz3D[3]
  1 1
  1 1
  
  0 0
  0 0
  
keyed{[]}
  "x" 1 2 3
  "y" 4 5 6
"""

    print("====================================")
    print("PYTHON TEST - MATRICES AND KEYED ARRAYS")
    print("====================================\n")

    print("1. ZEON Original:")
    print(data)
    
    # Test Parse
    obj = zeon.loads(data)
    
    print("2. Parse Result (Python dict):")
    import json
    print(json.dumps(obj, indent=2))
    
    # Test Stringify
    out_zeon = zeon.dumps(obj)
    
    print("\n3. Dump Result (ZEON string):")
    print(out_zeon)
    
    print("\n====================================")
    print("PYTHON TEST COMPLETE")
    print("====================================")

if __name__ == '__main__':
    test_matrices_and_arrays()

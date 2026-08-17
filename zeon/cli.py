import argparse
import sys
import os
import json
import zeon

def convert(args):
    in_path = args.input
    out_path = args.out
    
    if not os.path.exists(in_path):
        print(f"Error: File '{in_path}' not found.")
        sys.exit(1)
        
    _, ext = os.path.splitext(in_path)
    ext = ext.lower()
    
    try:
        with open(in_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if ext == '.json':
            # JSON to ZEON
            data = json.loads(content)
            output = zeon.dumps(data)
            default_out_ext = '.zeon'
        elif ext in ('.yaml', '.yml'):
            # YAML to ZEON
            import yaml
            data = yaml.safe_load(content)
            output = zeon.dumps(data)
            default_out_ext = '.zeon'
        elif ext == '.zeon':
            data = zeon.loads(content)
            
            # Define o formato de saída baseado na extensão do out_path, ou default json
            out_ext = '.json'
            if out_path:
                _, actual_ext = os.path.splitext(out_path)
                if actual_ext.lower() in ('.yaml', '.yml'):
                    out_ext = actual_ext.lower()
                    
            if out_ext in ('.yaml', '.yml'):
                import yaml
                output = yaml.safe_dump(data, sort_keys=False)
            else:
                output = json.dumps(data, indent=2)
                
            default_out_ext = out_ext
        else:
            print(f"Error: Unsupported file extension '{ext}'. Use .json, .yaml, .yml or .zeon")
            sys.exit(1)
            
        if args.print:
            print(output)
            return
            
        if not out_path:
            base, _ = os.path.splitext(in_path)
            out_path = base + default_out_ext
            
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)
            
        print(f"Successfully converted '{in_path}' to '{out_path}'.")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="ZEON (Lightweight LLM Object Notation) CLI",
        prog="zeon"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert between JSON and ZEON formats")
    convert_parser.add_argument("input", help="Input file path (.json or .zeon)")
    convert_parser.add_argument("--out", "-o", help="Output file path (optional)")
    convert_parser.add_argument("--print", "-p", action="store_true", help="Print output to console instead of saving to a file")
    
    args = parser.parse_args()
    
    if args.command == "convert":
        convert(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

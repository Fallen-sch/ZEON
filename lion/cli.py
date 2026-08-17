import argparse
import sys
import os
import json
import lion

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
            # JSON to LION
            data = json.loads(content)
            output = lion.dumps(data)
            default_out_ext = '.lion'
        elif ext == '.lion':
            # LION to JSON
            data = lion.loads(content)
            output = json.dumps(data, indent=2)
            default_out_ext = '.json'
        else:
            print(f"Error: Unsupported file extension '{ext}'. Use .json or .lion")
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
        description="LION (Lightweight LLM Object Notation) CLI",
        prog="lion"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert between JSON and LION formats")
    convert_parser.add_argument("input", help="Input file path (.json or .lion)")
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

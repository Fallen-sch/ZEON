import json
import os
from .parse import loads
from .stringify import dumps

class Converter:
    def __init__(self, data_or_path: str):
        self.raw_data = data_or_path
        self.is_file = False
        self.file_path = None
        
        # Check if the input is an existing file path
        if isinstance(data_or_path, str) and len(data_or_path) < 1000 and os.path.exists(data_or_path):
            self.is_file = True
            self.file_path = data_or_path
            with open(data_or_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
        else:
            self.content = data_or_path

    def to_json(self, out_path: str = None, **kwargs) -> str:
        """
        Parses ZEON content and returns JSON string.
        If out_path is provided, it saves to the file.
        """
        parsed_data = loads(self.content)
        
        if not kwargs and 'indent' not in kwargs:
            result = json.dumps(parsed_data, separators=(',', ':'))
        else:
            result = json.dumps(parsed_data, **kwargs)
            
        if out_path:
            # Se for apenas um nome de arquivo (sem barra de pasta) e a origem for um arquivo,
            # salva na mesma pasta do arquivo original.
            if self.is_file and not os.path.dirname(out_path):
                original_dir = os.path.dirname(self.file_path)
                out_path = os.path.join(original_dir, out_path)
                
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(result)
                
        return result

    def to_yaml(self, out_path: str = None, **kwargs) -> str:
        """
        Parses ZEON content and returns YAML string.
        If out_path is provided, it saves to the file.
        """
        import yaml
        parsed_data = loads(self.content)
        
        if not kwargs and 'sort_keys' not in kwargs:
            result = yaml.safe_dump(parsed_data, sort_keys=False)
        else:
            result = yaml.safe_dump(parsed_data, **kwargs)
            
        if out_path:
            if self.is_file and not os.path.dirname(out_path):
                original_dir = os.path.dirname(self.file_path)
                out_path = os.path.join(original_dir, out_path)
                
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(result)
                
        return result

    def to_zeon(self, out_path: str = None, **kwargs) -> str:
        """
        Parses JSON or YAML content and returns ZEON string.
        If out_path is provided, it saves to the file.
        """
        try:
            parsed_data = json.loads(self.content)
        except json.JSONDecodeError:
            import yaml
            parsed_data = yaml.safe_load(self.content)
            
        result = dumps(parsed_data, **kwargs)
        
        if out_path:
            if self.is_file and not os.path.dirname(out_path):
                original_dir = os.path.dirname(self.file_path)
                out_path = os.path.join(original_dir, out_path)
                
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(result)
                
        return result

def convert(data_or_path: str) -> Converter:
    """
    Starts a fluent conversion process. 
    Accepts either a raw string or a file path.
    """
    return Converter(data_or_path)

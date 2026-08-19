import re

class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.line = 1
        self.indent_stack = [0]
        
    def tokenize(self):
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            self.line = i + 1
            
            # Handle comments
            if '#' in line:
                line = line.split('#')[0]
                
            stripped = line.lstrip()
            if not stripped:
                self.tokens.append(Token('NEWLINE', '\n', self.line, 0))
                continue
                
            indent = len(line) - len(stripped)
            
            if indent > self.indent_stack[-1]:
                self.indent_stack.append(indent)
                self.tokens.append(Token('INDENT', indent, self.line, 0))
            elif indent < self.indent_stack[-1]:
                while self.indent_stack[-1] > indent:
                    self.indent_stack.pop()
                    self.tokens.append(Token('DEDENT', self.indent_stack[-1], self.line, 0))
            
            self._tokenize_line(stripped)
            self.tokens.append(Token('NEWLINE', '\n', self.line, len(line)))
            
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token('DEDENT', 0, self.line, 0))
            
        self.tokens.append(Token('EOF', None, self.line, 0))
        return self.tokens

    def _tokenize_line(self, line):
        pos = 0
        while pos < len(line):
            c = line[pos]
            start_col = pos
            if c.isspace():
                pos += 1
                continue
            if c in '()[]={}':
                self.tokens.append(Token(c, c, self.line, start_col))
                pos += 1
                continue
            if c == '\"':
                end = pos + 1
                while end < len(line) and not (line[end] == '\"' and line[end-1] != '\\'):
                    end += 1
                val = line[pos+1:end].replace('\\\"', '\"')
                self.tokens.append(Token('STRING', val, self.line, start_col + pos))
                pos = end + 1
                continue
                
            match = re.match(r'[^\s()\[\]={}]+', line[pos:])
            if match:
                val = match.group(0)
                if val in ('True', 'true'):
                    self.tokens.append(Token('BOOLEAN', True, self.line, start_col + pos))
                elif val in ('False', 'false'):
                    self.tokens.append(Token('BOOLEAN', False, self.line, start_col + pos))
                elif val in ('None', 'null'):
                    self.tokens.append(Token('NONE', None, self.line, start_col + pos))
                else:
                    try:
                        if '.' in val:
                            self.tokens.append(Token('NUMBER', float(val), self.line, start_col + pos))
                        else:
                            self.tokens.append(Token('NUMBER', int(val), self.line, start_col + pos))
                    except ValueError:
                        self.tokens.append(Token('IDENTIFIER', val, self.line, start_col + pos))
                pos += len(val)
            else:
                raise ValueError(f"Unexpected character '{c}' at line {self.line}")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]
        
    def consume(self, expected_type=None):
        tok = self.peek()
        if expected_type and tok.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok.type} at line {tok.line}")
        self.pos += 1
        return tok

    def _skip_newlines(self):
        while self.peek().type == 'NEWLINE':
            self.consume('NEWLINE')

    def parse(self):
        self._skip_newlines()
        tok1 = self.peek()
        if tok1.type == '[':
            # Check if this is the root array marker `[]` on its own line
            if (self.pos + 1 < len(self.tokens)
                    and self.tokens[self.pos + 1].type == ']'
                    and (self.pos + 2 >= len(self.tokens)
                         or self.tokens[self.pos + 2].type in ('NEWLINE', 'EOF'))):
                return self.parse_root_tabular()
            return self.parse_list()
        return self.parse_dict()

    def _skip_key_annotation(self):
        # Ignora anotações visuais estilo chave[anotacao], mas NÃO consome colchetes vazios [] nem atalhos de matriz como [2]
        if self.peek().type == '[':
            # Verifica se o próximo token não é ']' e não é um NUMBER seguido de ']'
            if self.pos + 1 < len(self.tokens):
                next_tok = self.tokens[self.pos+1]
                if next_tok.type == ']':
                    return
                if next_tok.type == 'NUMBER':
                    if self.pos + 2 < len(self.tokens) and self.tokens[self.pos+2].type == ']':
                        return
                        
                self.consume('[')
                while self.peek().type not in (']', 'NEWLINE', 'EOF'):
                    self.consume()
                if self.peek().type == ']':
                    self.consume(']')

    def parse_dict(self, end_tokens=('EOF', 'DEDENT', ')', ']')):
        res = {}
        while self.peek().type not in end_tokens:
            self._skip_newlines()
            if self.peek().type in end_tokens:
                break
            
            key_tok = self.peek()
            if key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                raise ValueError(f"Expected IDENTIFIER, NUMBER or STRING as dict key, got {key_tok.type} at line {key_tok.line}")
            self.consume()
            key = str(key_tok.value)
            
            # Ignora [anotacao] se houver
            self._skip_key_annotation()
            
            array_depth = 0
            is_keyed_tabular = False
            while True:
                if self.peek().type == '[':
                    if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == ']':
                        self.consume('[')
                        self.consume(']')
                        array_depth += 1
                    elif self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == 'NUMBER':
                        if self.pos + 2 < len(self.tokens) and self.tokens[self.pos+2].type == ']':
                            self.consume('[')
                            num = int(self.consume('NUMBER').value)
                            self.consume(']')
                            array_depth += num
                        else:
                            break
                    else:
                        break
                elif self.peek().type == '{':
                    if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == '}':
                        self.consume('{')
                        self.consume('}')
                        is_keyed_tabular = True
                    elif self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == '[':
                        if self.pos + 2 < len(self.tokens) and self.tokens[self.pos+2].type == ']':
                            if self.pos + 3 < len(self.tokens) and self.tokens[self.pos+3].type == '}':
                                self.consume('{')
                                self.consume('[')
                                self.consume(']')
                                self.consume('}')
                                is_keyed_tabular = True
                                array_depth += 1
                            else:
                                break
                        else:
                            break
                    else:
                        break
                else:
                    break

            if self.peek().type == 'NEWLINE':
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == 'INDENT':
                    res[key] = self.parse_tabular_block(array_depth, is_keyed_tabular)
                    continue
                else:
                    if array_depth > 0:
                        res[key] = []
                    else:
                        res[key] = {}
                    continue

            if self.peek().type == '=':
                self.consume('=')
                res[key] = self.parse_value()
            elif self.peek().type == '[':
                res[key] = self.parse_list()
            elif self.peek().type == '(':
                res[key] = self.parse_inline_group()
            else:
                res[key] = self.parse_value()
                
        return res

    def parse_tabular_block(self, array_depth, is_keyed_tabular=False):
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        if array_depth >= 2 or (is_keyed_tabular and array_depth >= 1):
            res = {} if is_keyed_tabular else []
            current_slice = []
            
            # Initial newline skipping
            newline_count = 0
            while self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
                newline_count += 1
                
            while self.peek().type not in ('DEDENT', 'EOF'):
                if self.peek().type == 'DEDENT':
                    break
                    
                if array_depth >= 3 and newline_count >= 2 and current_slice:
                    if not is_keyed_tabular:
                        res.append(current_slice)
                    current_slice = []
                    
                dict_key = None
                if is_keyed_tabular:
                    key_tok = self.peek()
                    if key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                        raise ValueError(f"Expected dict key for keyed matrix row, got {key_tok.type} at line {key_tok.line}")
                    self.consume()
                    dict_key = str(key_tok.value)
                    
                row = self.parse_tuple_row()
                
                if array_depth >= 3:
                    current_slice.append(row)
                else:
                    if is_keyed_tabular:
                        res[dict_key] = row
                    else:
                        res.append(row)
                
                # After row, parse any newlines for the next iteration
                newline_count = 0
                while self.peek().type == 'NEWLINE':
                    self.consume('NEWLINE')
                    newline_count += 1
                    
            if array_depth >= 3 and current_slice:
                res.append(current_slice)
                
            self.consume('DEDENT')
            return res
            
        headers = []
        while self.peek().type not in ('NEWLINE', 'EOF'):
            key_tok = self.peek()
            if key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                raise ValueError(f"Expected header key, got {key_tok.type} at line {key_tok.line}")
            self.consume()
            col_key = str(key_tok.value)
            
            self._skip_key_annotation()
            
            # Ignora indicadores de array no cabeçalho, como chave[] ou chave[][]
            while self.peek().type == '[':
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == ']':
                    self.consume('[')
                    self.consume(']')
                else:
                    break
                    
            # Ignora indicadores de dicionário vazio no cabeçalho, como chave()
            while self.peek().type == '(':
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == ')':
                    self.consume('(')
                    self.consume(')')
                else:
                    break
            
            if self.peek().type == '(':
                self.consume('(')
                sub_keys = []
                while self.peek().type not in (')', 'NEWLINE', 'EOF'):
                    sub_key_tok = self.peek()
                    if sub_key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                        raise ValueError(f"Expected sub header key, got {sub_key_tok.type}")
                    self.consume()
                    sub_key_str = str(sub_key_tok.value)
                    self._skip_key_annotation()
                    sub_keys.append(sub_key_str)
                self.consume(')')
                headers.append((col_key, sub_keys))
            else:
                headers.append(col_key)
                
        self.consume('NEWLINE')
        
        res = {} if is_keyed_tabular else []
        while self.peek().type not in ('DEDENT', 'EOF'):
            self._skip_newlines()
            if self.peek().type == 'DEDENT':
                break
            
            dict_key = None
            if is_keyed_tabular:
                key_tok = self.peek()
                if key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                    raise ValueError(f"Expected dict key for keyed tabular row, got {key_tok.type} at line {key_tok.line}")
                self.consume()
                dict_key = str(key_tok.value)
                
            row_dict = {}
            for header in headers:
                if isinstance(header, tuple):
                    main_k, sub_k = header
                    val = self.parse_value()
                    if isinstance(val, (tuple, list)):
                        row_dict[main_k] = dict(zip(sub_k, val))
                    elif isinstance(val, dict):
                        sub_dict = val.copy()
                        for i, sk in enumerate(sub_k):
                            str_i = str(i)
                            if str_i in sub_dict:
                                sub_dict[sk] = sub_dict.pop(str_i)
                        row_dict[main_k] = sub_dict
                    else:
                        raise ValueError(f"Expected tuple/list or dict for {main_k} at line {self.peek().line}")
                else:
                    row_dict[header] = self.parse_value()
                    
            while self.peek().type not in ('NEWLINE', 'EOF', 'DEDENT'):
                key_tok = self.peek()
                if key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                    raise ValueError(f"Expected dynamic property key, got {key_tok.type} at line {key_tok.line}")
                self.consume()
                key = str(key_tok.value)
                
                self._skip_key_annotation()
                
                if self.peek().type == '=':
                    self.consume('=')
                    row_dict[key] = self.parse_value()
                else:
                    raise ValueError(f"Expected '=' after dynamic property '{key}' at line {key_tok.line}")
                    
            if is_keyed_tabular:
                res[dict_key] = row_dict
            else:
                res.append(row_dict)
            
        self.consume('DEDENT')
        if is_keyed_tabular:
            return res
        return res if array_depth > 0 else res[0]

    def parse_root_tabular(self):
        """Parse a root-level tabular array introduced by the [] marker.

        Syntax::

            []
              col1 col2
              val1 val2
              val3 val4
        """
        self.consume('[')  # consume '['
        self.consume(']')  # consume ']'
        self._skip_newlines()

        if self.peek().type == 'EOF':
            return []

        if self.peek().type == 'INDENT':
            self.consume('INDENT')

        # Read header
        headers = []
        while self.peek().type not in ('NEWLINE', 'EOF', 'DEDENT'):
            key_tok = self.peek()
            if key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                raise ValueError(
                    f"Expected header key, got {key_tok.type} at line {key_tok.line}"
                )
            self.consume()
            col_key = str(key_tok.value)

            self._skip_key_annotation()

            while self.peek().type == '[':
                if (self.pos + 1 < len(self.tokens)
                        and self.tokens[self.pos + 1].type == ']'):
                    self.consume('['); self.consume(']')
                else:
                    break

            while self.peek().type == '(':
                if (self.pos + 1 < len(self.tokens)
                        and self.tokens[self.pos + 1].type == ')'):
                    self.consume('('); self.consume(')')
                else:
                    break

            if self.peek().type == '(':
                self.consume('(')
                sub_keys = []
                while self.peek().type not in (')', 'NEWLINE', 'EOF'):
                    sub_key_tok = self.peek()
                    if sub_key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                        raise ValueError(
                            f"Expected sub header key, got {sub_key_tok.type}"
                        )
                    self.consume()
                    sub_key_str = str(sub_key_tok.value)
                    self._skip_key_annotation()
                    sub_keys.append(sub_key_str)
                self.consume(')')
                headers.append((col_key, sub_keys))
            else:
                headers.append(col_key)

        if self.peek().type == 'NEWLINE':
            self.consume('NEWLINE')

        res = []
        while self.peek().type not in ('DEDENT', 'EOF'):
            self._skip_newlines()
            if self.peek().type in ('DEDENT', 'EOF'):
                break

            row_dict = {}
            for header in headers:
                if isinstance(header, tuple):
                    main_k, sub_k = header
                    val = self.parse_value()
                    if isinstance(val, (tuple, list)):
                        row_dict[main_k] = dict(zip(sub_k, val))
                    elif isinstance(val, dict):
                        sub_dict = val.copy()
                        for i, sk in enumerate(sub_k):
                            str_i = str(i)
                            if str_i in sub_dict:
                                sub_dict[sk] = sub_dict.pop(str_i)
                        row_dict[main_k] = sub_dict
                    else:
                        raise ValueError(
                            f"Expected tuple/list or dict for {main_k} at line {self.peek().line}"
                        )
                else:
                    row_dict[header] = self.parse_value()

            # Inline dynamic properties at the end of the row
            while self.peek().type not in ('NEWLINE', 'EOF', 'DEDENT'):
                key_tok = self.peek()
                if key_tok.type not in ('IDENTIFIER', 'NUMBER', 'STRING'):
                    raise ValueError(
                        f"Expected dynamic property key, got {key_tok.type} at line {key_tok.line}"
                    )
                self.consume()
                key = str(key_tok.value)
                self._skip_key_annotation()
                if self.peek().type == '=':
                    self.consume('=')
                    row_dict[key] = self.parse_value()
                else:
                    raise ValueError(
                        f"Expected '=' after dynamic property '{key}' at line {key_tok.line}"
                    )

            res.append(row_dict)

        if self.peek().type == 'DEDENT':
            self.consume('DEDENT')

        return res

    def parse_list(self):
        self.consume('[')
        res = []
        while self.peek().type != ']':
            while self.peek().type in ('NEWLINE', 'INDENT', 'DEDENT'):
                self.consume()
            if self.peek().type == ']':
                break
            res.append(self.parse_value())
        self.consume(']')
        return res

    def parse_tuple_row(self):
        row = []
        while self.peek().type not in ('NEWLINE', 'EOF', 'DEDENT'):
            row.append(self.parse_value())
            if self.peek().type == ',':
                self.consume(',')
        return row

    def parse_inline_group(self):
        self.consume('(')
        res = {}
        pos_idx = 0
        has_kwargs = False
        
        while self.peek().type != ')':
            while self.peek().type in ('NEWLINE', 'INDENT', 'DEDENT'):
                self.consume()
            if self.peek().type == ')':
                break
                
            temp = self.pos
            tok = self.tokens[temp]
            is_kwarg = False
            
            if tok.type in ('IDENTIFIER', 'NUMBER', 'STRING'):
                temp += 1
                while temp < len(self.tokens) and self.tokens[temp].type == '[':
                    temp += 1
                    if temp < len(self.tokens) and self.tokens[temp].type == ']':
                        temp += 1
                    else:
                        break
                if temp < len(self.tokens) and self.tokens[temp].type == '=':
                    is_kwarg = True
                    
            if is_kwarg:
                has_kwargs = True
                key_tok = self.peek()
                self.consume()
                key = str(key_tok.value)
                self._skip_key_annotation()
                self.consume('=')
                res[key] = self.parse_value()
            else:
                val = self.parse_value()
                res[str(pos_idx)] = val
                pos_idx += 1
                
        self.consume(')')
        
        if not has_kwargs:
            return tuple(res[str(i)] for i in range(pos_idx))
            
        return res

    def parse_value(self):
        tok = self.peek()
        if tok.type == '[':
            return self.parse_list()
        if tok.type == '(':
            return self.parse_inline_group()
        if tok.type in ('STRING', 'NUMBER', 'BOOLEAN', 'NONE', 'IDENTIFIER'):
            self.consume()
            return tok.value
        raise ValueError(f"Unexpected token {tok.type} in parse_value at line {tok.line}")

def loads(text: str):
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

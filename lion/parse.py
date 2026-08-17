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
            if c in '()[]=':
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
                
            match = re.match(r'[^\s()\[\]=]+', line[pos:])
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
            return self.parse_list()
        return self.parse_dict()

    def parse_dict(self, end_tokens=('EOF', 'DEDENT', ')', ']')):
        res = {}
        while self.peek().type not in end_tokens:
            self._skip_newlines()
            if self.peek().type in end_tokens:
                break
            key_tok = self.consume('IDENTIFIER')
            key = key_tok.value
            
            array_depth = 0
            while True:
                if self.peek().type == '[':
                    if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == ']':
                        self.consume('[')
                        self.consume(']')
                        array_depth += 1
                    else:
                        break
                else:
                    break

            if self.peek().type == 'NEWLINE':
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos+1].type == 'INDENT':
                    res[key] = self.parse_tabular_block(array_depth)
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

    def parse_tabular_block(self, array_depth):
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        if array_depth >= 2:
            res = []
            while self.peek().type not in ('DEDENT', 'EOF'):
                self._skip_newlines()
                if self.peek().type == 'DEDENT':
                    break
                row = self.parse_tuple_row()
                res.append(row)
            self.consume('DEDENT')
            return res
            
        headers = []
        while self.peek().type not in ('NEWLINE', 'EOF'):
            col_key = self.consume('IDENTIFIER').value
            if self.peek().type == '(':
                self.consume('(')
                sub_keys = []
                while self.peek().type not in (')', 'NEWLINE', 'EOF'):
                    sub_keys.append(self.consume('IDENTIFIER').value)
                self.consume(')')
                headers.append((col_key, sub_keys))
            else:
                headers.append(col_key)
                
        self.consume('NEWLINE')
        
        res = []
        while self.peek().type not in ('DEDENT', 'EOF'):
            self._skip_newlines()
            if self.peek().type == 'DEDENT':
                break
            
            row_dict = {}
            for header in headers:
                if isinstance(header, tuple):
                    main_k, sub_k = header
                    val = self.parse_value()
                    if isinstance(val, (tuple, list)):
                        row_dict[main_k] = dict(zip(sub_k, val))
                    else:
                        raise ValueError(f"Expected tuple/list for {main_k}")
                else:
                    row_dict[header] = self.parse_value()
                    
            res.append(row_dict)
            
        self.consume('DEDENT')
        return res if array_depth > 0 else res[0]

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
        is_dict = False
        temp = self.pos
        while temp < len(self.tokens) and self.tokens[temp].type != ')':
            if self.tokens[temp].type == '=':
                is_dict = True
                break
            temp += 1
            
        if is_dict:
            res = self.parse_dict(end_tokens=(')', 'NEWLINE', 'EOF'))
            self.consume(')')
        else:
            res = []
            while self.peek().type != ')':
                res.append(self.parse_value())
            self.consume(')')
            res = tuple(res)
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

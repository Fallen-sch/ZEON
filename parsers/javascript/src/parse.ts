export class Token {
    constructor(
        public type: string,
        public value: any,
        public line: number,
        public col: number
    ) {}
}

export class Lexer {
    private tokens: Token[] = [];
    private line: number = 1;
    private indentStack: number[] = [0];

    constructor(private text: string) {}

    public tokenize(): Token[] {
        const lines = this.text.split('\n');
        for (let i = 0; i < lines.length; i++) {
            this.line = i + 1;
            let lineStr = lines[i].replace(/\r$/, '');

            if (lineStr.includes('#')) {
                lineStr = lineStr.split('#')[0];
            }

            const stripped = lineStr.trimStart();
            if (!stripped) {
                this.tokens.push(new Token('NEWLINE', '\n', this.line, 0));
                continue;
            }

            const indent = lineStr.length - stripped.length;

            if (indent > this.indentStack[this.indentStack.length - 1]) {
                this.indentStack.push(indent);
                this.tokens.push(new Token('INDENT', indent, this.line, 0));
            } else if (indent < this.indentStack[this.indentStack.length - 1]) {
                while (this.indentStack[this.indentStack.length - 1] > indent) {
                    this.indentStack.pop();
                    this.tokens.push(new Token('DEDENT', this.indentStack[this.indentStack.length - 1], this.line, 0));
                }
            }

            this._tokenizeLine(stripped);
            this.tokens.push(new Token('NEWLINE', '\n', this.line, lineStr.length));
        }

        while (this.indentStack.length > 1) {
            this.indentStack.pop();
            this.tokens.push(new Token('DEDENT', 0, this.line, 0));
        }

        this.tokens.push(new Token('EOF', null, this.line, 0));
        return this.tokens;
    }

    private _tokenizeLine(lineStr: string) {
        let pos = 0;
        while (pos < lineStr.length) {
            const c = lineStr[pos];
            const startCol = pos;

            if (/\s/.test(c)) {
                pos++;
                continue;
            }

            if ('()[]={}'.includes(c)) {
                this.tokens.push(new Token(c, c, this.line, startCol));
                pos++;
                continue;
            }

            if (c === '"') {
                let end = pos + 1;
                while (end < lineStr.length && !(lineStr[end] === '"' && lineStr[end - 1] !== '\\')) {
                    end++;
                }
                const val = lineStr.substring(pos + 1, end).replace(/\\"/g, '"');
                this.tokens.push(new Token('STRING', val, this.line, startCol + pos));
                pos = end + 1;
                continue;
            }

            const match = lineStr.substring(pos).match(/^[^\s()[\]={}\"]+/);
            if (match) {
                const val = match[0];
                if (val === 'True' || val === 'true') {
                    this.tokens.push(new Token('BOOLEAN', true, this.line, startCol + pos));
                } else if (val === 'False' || val === 'false') {
                    this.tokens.push(new Token('BOOLEAN', false, this.line, startCol + pos));
                } else if (val === 'None' || val === 'null') {
                    this.tokens.push(new Token('NONE', null, this.line, startCol + pos));
                } else {
                    const num = Number(val);
                    if (!isNaN(num) && val.trim() !== '') {
                        this.tokens.push(new Token('NUMBER', num, this.line, startCol + pos));
                    } else {
                        this.tokens.push(new Token('IDENTIFIER', val, this.line, startCol + pos));
                    }
                }
                pos += val.length;
            } else {
                throw new Error(`Unexpected character '${c}' at line ${this.line}`);
            }
        }
    }
}

export class Parser {
    private pos: number = 0;

    constructor(private tokens: Token[]) {}

    private peek(): Token {
        if (this.pos < this.tokens.length) {
            return this.tokens[this.pos];
        }
        return this.tokens[this.tokens.length - 1];
    }

    private consume(expectedType?: string): Token {
        const tok = this.peek();
        if (expectedType && tok.type !== expectedType) {
            throw new Error(`Expected ${expectedType}, got ${tok.type} at line ${tok.line}`);
        }
        this.pos++;
        return tok;
    }

    private _skipNewlines() {
        while (this.peek().type === 'NEWLINE') {
            this.consume('NEWLINE');
        }
    }

    public parse(): any {
        this._skipNewlines();
        const tok1 = this.peek();
        if (tok1.type === '[') {
            return this.parseList();
        }
        return this.parseDict();
    }

    private _skipKeyAnnotation() {
        if (this.peek().type === '[') {
            if (this.pos + 1 < this.tokens.length) {
                const nextTok = this.tokens[this.pos + 1];
                if (nextTok.type === ']') return;
                if (nextTok.type === 'NUMBER') {
                    if (this.pos + 2 < this.tokens.length && this.tokens[this.pos + 2].type === ']') {
                        return;
                    }
                }
                
                this.consume('[');
                while (![']', 'NEWLINE', 'EOF'].includes(this.peek().type)) {
                    this.consume();
                }
                if (this.peek().type === ']') {
                    this.consume(']');
                }
            }
        }
    }

    private parseDict(endTokens: string[] = ['EOF', 'DEDENT', ')', ']']): any {
        const res: any = {};
        while (!endTokens.includes(this.peek().type)) {
            this._skipNewlines();
            if (endTokens.includes(this.peek().type)) break;

            const keyTok = this.peek();
            if (!['IDENTIFIER', 'NUMBER', 'STRING'].includes(keyTok.type)) {
                throw new Error(`Expected IDENTIFIER, NUMBER or STRING as dict key, got ${keyTok.type} at line ${keyTok.line}`);
            }
            this.consume();
            const key = String(keyTok.value);

            this._skipKeyAnnotation();

            let arrayDepth = 0;
            let isKeyedTabular = false;
            while (true) {
                if (this.peek().type === '[') {
                    if (this.pos + 1 < this.tokens.length && this.tokens[this.pos + 1].type === ']') {
                        this.consume('[');
                        this.consume(']');
                        arrayDepth++;
                    } else if (this.pos + 1 < this.tokens.length && this.tokens[this.pos + 1].type === 'NUMBER') {
                        if (this.pos + 2 < this.tokens.length && this.tokens[this.pos + 2].type === ']') {
                            this.consume('[');
                            const num = Number(this.consume('NUMBER').value);
                            this.consume(']');
                            arrayDepth += num;
                        } else {
                            break;
                        }
                    } else {
                        break;
                    }
                } else if (this.peek().type === '{') {
                    if (this.pos + 1 < this.tokens.length && this.tokens[this.pos + 1].type === '}') {
                        this.consume('{');
                        this.consume('}');
                        isKeyedTabular = true;
                    } else if (this.pos + 1 < this.tokens.length && this.tokens[this.pos + 1].type === '[') {
                        if (this.pos + 2 < this.tokens.length && this.tokens[this.pos + 2].type === ']') {
                            if (this.pos + 3 < this.tokens.length && this.tokens[this.pos + 3].type === '}') {
                                this.consume('{');
                                this.consume('[');
                                this.consume(']');
                                this.consume('}');
                                isKeyedTabular = true;
                                arrayDepth++;
                            } else break;
                        } else break;
                    } else break;
                } else {
                    break;
                }
            }

            if (this.peek().type === 'NEWLINE') {
                if (this.pos + 1 < this.tokens.length && this.tokens[this.pos + 1].type === 'INDENT') {
                    res[key] = this.parseTabularBlock(arrayDepth, isKeyedTabular);
                    continue;
                } else {
                    if (arrayDepth > 0) {
                        res[key] = [];
                    } else {
                        res[key] = {};
                    }
                    continue;
                }
            }

            if (this.peek().type === '=') {
                this.consume('=');
                res[key] = this.parseValue();
            } else if (this.peek().type === '[') {
                res[key] = this.parseList();
            } else if (this.peek().type === '(') {
                res[key] = this.parseInlineGroup();
            } else {
                res[key] = this.parseValue();
            }
        }
        return res;
    }

    private parseTabularBlock(arrayDepth: number, isKeyedTabular: boolean = false): any {
        this.consume('NEWLINE');
        this.consume('INDENT');

        if (arrayDepth >= 2 || (isKeyedTabular && arrayDepth >= 1)) {
            const res: any = isKeyedTabular ? {} : [];
            let currentSlice: any[] = [];
            
            let newlineCount = 0;
            while (this.peek().type === 'NEWLINE') {
                this.consume('NEWLINE');
                newlineCount++;
            }
            
            while (!['DEDENT', 'EOF'].includes(this.peek().type)) {
                if (this.peek().type === 'DEDENT') break;
                
                if (arrayDepth >= 3 && newlineCount >= 2 && currentSlice.length > 0) {
                    if (!isKeyedTabular) {
                        res.push(currentSlice);
                    }
                    currentSlice = [];
                }
                
                let dictKey: string | null = null;
                if (isKeyedTabular) {
                    const keyTok = this.peek();
                    if (!['IDENTIFIER', 'NUMBER', 'STRING'].includes(keyTok.type)) {
                        throw new Error(`Expected dict key for keyed matrix row, got ${keyTok.type} at line ${keyTok.line}`);
                    }
                    this.consume();
                    dictKey = String(keyTok.value);
                }
                
                const row = this.parseTupleRow();
                
                if (arrayDepth >= 3) {
                    currentSlice.push(row);
                } else {
                    if (isKeyedTabular) {
                        res[dictKey!] = row;
                    } else {
                        res.push(row);
                    }
                }
                
                newlineCount = 0;
                while (this.peek().type === 'NEWLINE') {
                    this.consume('NEWLINE');
                    newlineCount++;
                }
            }
            
            if (arrayDepth >= 3 && currentSlice.length > 0) {
                res.push(currentSlice);
            }
            
            this.consume('DEDENT');
            return res;
        }

        const headers: any[] = [];
        while (!['NEWLINE', 'EOF'].includes(this.peek().type)) {
            const keyTok = this.peek();
            if (!['IDENTIFIER', 'NUMBER', 'STRING'].includes(keyTok.type)) {
                throw new Error(`Expected header key, got ${keyTok.type} at line ${keyTok.line}`);
            }
            this.consume();
            const colKey = String(keyTok.value);

            this._skipKeyAnnotation();

            while (this.peek().type === '[') {
                if (this.pos + 1 < this.tokens.length && this.tokens[this.pos + 1].type === ']') {
                    this.consume('[');
                    this.consume(']');
                } else break;
            }

            while (this.peek().type === '(') {
                if (this.pos + + 1 < this.tokens.length && this.tokens[this.pos + 1].type === ')') {
                    this.consume('(');
                    this.consume(')');
                } else break;
            }

            if (this.peek().type === '(') {
                this.consume('(');
                const subKeys: string[] = [];
                while (![')', 'NEWLINE', 'EOF'].includes(this.peek().type)) {
                    const subKeyTok = this.peek();
                    if (!['IDENTIFIER', 'NUMBER', 'STRING'].includes(subKeyTok.type)) {
                        throw new Error(`Expected sub header key, got ${subKeyTok.type}`);
                    }
                    this.consume();
                    subKeys.push(String(subKeyTok.value));
                    this._skipKeyAnnotation();
                }
                this.consume(')');
                headers.push([colKey, subKeys]);
            } else {
                headers.push(colKey);
            }
        }

        this.consume('NEWLINE');

        const res: any = isKeyedTabular ? {} : [];
        while (!['DEDENT', 'EOF'].includes(this.peek().type)) {
            this._skipNewlines();
            if (this.peek().type === 'DEDENT') break;

            let dictKey: string | null = null;
            if (isKeyedTabular) {
                const keyTok = this.peek();
                if (!['IDENTIFIER', 'NUMBER', 'STRING'].includes(keyTok.type)) {
                    throw new Error(`Expected dict key for keyed tabular row, got ${keyTok.type} at line ${keyTok.line}`);
                }
                this.consume();
                dictKey = String(keyTok.value);
            }

            const rowDict: any = {};
            for (const header of headers) {
                if (Array.isArray(header)) {
                    const mainK = header[0];
                    const subK = header[1];
                    const val = this.parseValue();
                    if (Array.isArray(val)) {
                        const subDict: any = {};
                        for (let i = 0; i < subK.length; i++) {
                            subDict[subK[i]] = val[i];
                        }
                        rowDict[mainK] = subDict;
                    } else if (typeof val === 'object' && val !== null) {
                        const subDict: any = { ...val };
                        for (let i = 0; i < subK.length; i++) {
                            const strI = String(i);
                            if (strI in subDict) {
                                subDict[subK[i]] = subDict[strI];
                                delete subDict[strI];
                            }
                        }
                        rowDict[mainK] = subDict;
                    } else {
                        throw new Error(`Expected array or dict for ${mainK} at line ${this.peek().line}`);
                    }
                } else {
                    rowDict[header] = this.parseValue();
                }
            }

            while (!['NEWLINE', 'EOF', 'DEDENT'].includes(this.peek().type)) {
                const keyTok = this.peek();
                if (!['IDENTIFIER', 'NUMBER', 'STRING'].includes(keyTok.type)) {
                    throw new Error(`Expected dynamic property key, got ${keyTok.type} at line ${keyTok.line}`);
                }
                this.consume();
                const key = String(keyTok.value);

                this._skipKeyAnnotation();

                if (this.peek().type === '=') {
                    this.consume('=');
                    rowDict[key] = this.parseValue();
                } else {
                    throw new Error(`Expected '=' after dynamic property '${key}' at line ${keyTok.line}`);
                }
            }

            if (isKeyedTabular) {
                res[dictKey!] = rowDict;
            } else {
                res.push(rowDict);
            }
        }

        this.consume('DEDENT');
        if (isKeyedTabular) return res;
        return arrayDepth > 0 ? res : res[0];
    }

    private parseList(): any[] {
        this.consume('[');
        const res: any[] = [];
        while (this.peek().type !== ']') {
            while (['NEWLINE', 'INDENT', 'DEDENT'].includes(this.peek().type)) {
                this.consume();
            }
            if (this.peek().type === ']') break;
            res.push(this.parseValue());
        }
        this.consume(']');
        return res;
    }

    private parseTupleRow(): any[] {
        const row: any[] = [];
        while (!['NEWLINE', 'EOF', 'DEDENT'].includes(this.peek().type)) {
            row.push(this.parseValue());
            if (this.peek().type === ',') {
                this.consume(',');
            }
        }
        return row;
    }

    private parseInlineGroup(): any {
        this.consume('(');
        const res: any = {};
        let posIdx = 0;
        let hasKwargs = false;

        while (this.peek().type !== ')') {
            while (['NEWLINE', 'INDENT', 'DEDENT'].includes(this.peek().type)) {
                this.consume();
            }
            if (this.peek().type === ')') break;

            let temp = this.pos;
            const tok = this.tokens[temp];
            let isKwarg = false;

            if (['IDENTIFIER', 'NUMBER', 'STRING'].includes(tok.type)) {
                temp++;
                while (temp < this.tokens.length && this.tokens[temp].type === '[') {
                    temp++;
                    if (temp < this.tokens.length && this.tokens[temp].type === ']') {
                        temp++;
                    } else {
                        break;
                    }
                }
                if (temp < this.tokens.length && this.tokens[temp].type === '=') {
                    isKwarg = true;
                }
            }

            if (isKwarg) {
                hasKwargs = true;
                const keyTok = this.peek();
                this.consume();
                const key = String(keyTok.value);
                this._skipKeyAnnotation();
                this.consume('=');
                res[key] = this.parseValue();
            } else {
                const val = this.parseValue();
                res[String(posIdx)] = val;
                posIdx++;
            }
        }
        this.consume(')');

        if (!hasKwargs) {
            const arr = [];
            for (let i = 0; i < posIdx; i++) arr.push(res[String(i)]);
            return arr;
        }

        return res;
    }

    private parseValue(): any {
        const tok = this.peek();
        if (tok.type === '[') return this.parseList();
        if (tok.type === '(') return this.parseInlineGroup();
        if (['STRING', 'NUMBER', 'BOOLEAN', 'NONE', 'IDENTIFIER'].includes(tok.type)) {
            this.consume();
            return tok.value;
        }
        throw new Error(`Unexpected token ${tok.type} in parseValue at line ${tok.line}`);
    }
}

export function parse(text: string): any {
    const lexer = new Lexer(text);
    const tokens = lexer.tokenize();
    const parser = new Parser(tokens);
    return parser.parse();
}

function isObject(v: any): boolean {
    return typeof v === 'object' && v !== null && !Array.isArray(v);
}

function _needsQuotes(s: any): boolean {
    if (typeof s !== 'string') return false;
    if (!s) return true;
    if (/[\s,"'\(\)\[\]=\{\}\:]/.test(s)) return true;
    const lower = s.toLowerCase();
    if (['true', 'false', 'null', 'none'].includes(lower)) return true;
    if (!isNaN(Number(s))) return true;
    return false;
}

function _dumpPrimitive(val: any): string {
    if (val === null || val === undefined) {
        return "None";
    } else if (typeof val === 'boolean') {
        return val ? "True" : "False";
    } else if (typeof val === 'number') {
        return String(val);
    } else if (typeof val === 'string') {
        if (_needsQuotes(val)) {
            return '"' + val.replace(/"/g, '\\"') + '"';
        }
        return val;
    } else {
        return `"${String(val)}"`;
    }
}

function _isFlatEnoughForHeaders(v: any): boolean {
    if (!isObject(v)) return true;
    for (const val of Object.values(v)) {
        if (isObject(val) || Array.isArray(val)) {
            return false;
        }
    }
    return true;
}

function _getHybridHeaders(lst: any[]): any[] {
    if (!lst || lst.length === 0 || !isObject(lst[0])) return [];
    
    let commonKeys = new Set(Object.keys(lst[0]));
    for (let i = 1; i < lst.length; i++) {
        const item = lst[i];
        if (!isObject(item)) return [];
        const itemKeys = new Set(Object.keys(item));
        commonKeys = new Set([...commonKeys].filter(x => itemKeys.has(x)));
    }
    
    if (commonKeys.size === 0) return [];
    
    const headers: any[] = [];
    for (const k of Object.keys(lst[0])) {
        if (commonKeys.has(k)) {
            const v1 = lst[0][k];
            if (isObject(v1) && _isFlatEnoughForHeaders(v1)) {
                let subKeys = new Set(Object.keys(v1));
                let valid = true;
                for (let i = 1; i < lst.length; i++) {
                    const v2 = lst[i][k];
                    if (!isObject(v2)) {
                        valid = false;
                        break;
                    }
                    const v2Keys = new Set(Object.keys(v2));
                    subKeys = new Set([...subKeys].filter(x => v2Keys.has(x)));
                }
                
                if (valid && subKeys.size > 0) {
                    const orderedSubKeys = Object.keys(v1).filter(sk => subKeys.has(sk));
                    headers.push([k, orderedSubKeys]);
                } else {
                    headers.push(k);
                }
            } else {
                headers.push(k);
            }
        }
    }
    return headers;
}

function _getKeyedTabularHeaders(d: any): any[] {
    if (!d || !isObject(d)) return [];
    return _getHybridHeaders(Object.values(d));
}

function _isMatrix2d(lst: any[]): boolean {
    if (!lst || lst.length === 0 || !Array.isArray(lst[0])) return false;
    for (const item of lst) {
        if (!Array.isArray(item)) return false;
        for (const v of item) {
            if (isObject(v) || Array.isArray(v)) return false;
        }
    }
    return true;
}

function _isMatrix3d(lst: any[]): boolean {
    if (!lst || lst.length === 0 || !Array.isArray(lst[0])) return false;
    for (const item of lst) {
        if (!_isMatrix2d(item)) return false;
    }
    return true;
}

function _isDictOfArrays(d: any): boolean {
    if (!d || !isObject(d)) return false;
    for (const v of Object.values(d)) {
        if (!Array.isArray(v)) return false;
        for (const x of v) {
            if (isObject(x) || Array.isArray(x)) return false;
        }
    }
    return true;
}

function _isFlatDict(d: any): boolean {
    for (const v of Object.values(d)) {
        if (isObject(v)) return false;
        if (Array.isArray(v)) {
            for (const x of v) {
                if (isObject(x) || Array.isArray(x)) return false;
            }
        }
    }
    return true;
}

function _formatHeaderTuple(header: any): string {
    if (Array.isArray(header) && header.length === 2) {
        return `${header[0]}(${header[1].join(' ')})`;
    }
    return header;
}

function _formatValueForHeader(item: any, header: any): string {
    if (Array.isArray(header) && header.length === 2) {
        const main_k = header[0];
        const sub_k = header[1];
        const val_dict = item[main_k] || {};
        const vals = sub_k.map((sk: string) => _dumpPrimitive(val_dict[sk]));
        
        const subKSet = new Set(sub_k);
        const extraKeys = Object.keys(val_dict).filter(ek => !subKSet.has(ek));
        if (extraKeys.length > 0) {
            const extraDict: any = {};
            for (const ek of extraKeys) {
                extraDict[ek] = val_dict[ek];
            }
            vals.push(_dumpsInline(extraDict));
        }
        
        return `(${vals.join(' ')})`;
    } else {
        const v = item[header];
        if (isObject(v)) {
            return `(${_dumpsInline(v)})`;
        } else if (Array.isArray(v)) {
            return _dumpsInline(v);
        }
        return _dumpPrimitive(v);
    }
}

function _dumpsInline(obj: any): string {
    if (isObject(obj)) {
        const parts: string[] = [];
        for (const [k, v] of Object.entries(obj)) {
            if (isObject(v)) {
                parts.push(`${k}=(${_dumpsInline(v)})`);
            } else if (Array.isArray(v)) {
                parts.push(`${k}=${_dumpsInline(v)}`);
            } else {
                parts.push(`${k}=${_dumpsInline(v)}`);
            }
        }
        return parts.join(" ");
    } else if (Array.isArray(obj)) {
        const parts: string[] = [];
        for (const v of obj) {
            if (isObject(v)) {
                parts.push(`(${_dumpsInline(v)})`);
            } else {
                parts.push(_dumpsInline(v));
            }
        }
        return "[" + parts.join(" ") + "]";
    } else {
        return _dumpPrimitive(obj);
    }
}

function _dumps(obj: any, indentLevel: number = 0): string {
    const indentStr = "  ".repeat(indentLevel);
    
    if (isObject(obj)) {
        const values = Object.values(obj);
        const hasTabular = values.some(v => Array.isArray(v) && (_getHybridHeaders(v as any[]).length > 0 || _isMatrix2d(v as any[]) || _isMatrix3d(v as any[])));
        const hasKeyedTabular = values.some(v => isObject(v) && (_getKeyedTabularHeaders(v).length > 0 || _isDictOfArrays(v)));
        
        if (!hasTabular && !hasKeyedTabular && indentLevel > 0) {
            return `${indentStr}(${_dumpsInline(obj)})`;
        }
            
        const lines: string[] = [];
        for (const [k, v] of Object.entries(obj)) {
            if (Array.isArray(v) && _isMatrix3d(v)) {
                lines.push(`${indentStr}${k}[3]`);
                for (let sliceIdx = 0; sliceIdx < v.length; sliceIdx++) {
                    if (sliceIdx > 0) lines.push("");
                    const slice2d = v[sliceIdx];
                    for (const row of slice2d) {
                        const valsStr = row.map((x: any) => _dumpPrimitive(x)).join(" ");
                        lines.push(`${indentStr}  ${valsStr}`);
                    }
                }
            } else if (Array.isArray(v) && _isMatrix2d(v)) {
                lines.push(`${indentStr}${k}[2]`);
                for (const row of v) {
                    const valsStr = row.map((x: any) => _dumpPrimitive(x)).join(" ");
                    lines.push(`${indentStr}  ${valsStr}`);
                }
            } else if (Array.isArray(v) && _getHybridHeaders(v).length > 0) {
                const headers = _getHybridHeaders(v);
                
                const headerStrs: string[] = [];
                for (const h of headers) {
                    if (Array.isArray(h) && h.length === 2) {
                        headerStrs.push(_formatHeaderTuple(h));
                    } else {
                        const firstVal = v[0][h];
                        if (isObject(firstVal)) {
                            headerStrs.push(`${h}()`);
                        } else if (Array.isArray(firstVal)) {
                            headerStrs.push(`${h}[]`);
                        } else {
                            headerStrs.push(String(h));
                        }
                    }
                }
                
                const headerStr = headerStrs.join(" ");
                lines.push(`${indentStr}${k}[]`);
                lines.push(`${indentStr}  ${headerStr}`);
                
                for (const item of v) {
                    let valsStr = headers.map(h => _formatValueForHeader(item, h)).join(" ");
                    const headerKeysSet = new Set(headers.map(h => Array.isArray(h) && h.length === 2 ? h[0] : h));
                    
                    const extraKeys = Object.keys(item).filter(ek => !headerKeysSet.has(ek));
                    if (extraKeys.length > 0) {
                        const extraDict: any = {};
                        for (const ek of extraKeys) {
                            extraDict[ek] = item[ek];
                        }
                        valsStr += ` ${_dumpsInline(extraDict)}`;
                    }
                    lines.push(`${indentStr}  ${valsStr}`);
                }
            } else if (Array.isArray(v) && v.length > 0 && isObject(v[0])) {
                const parts = v.map((item: any) => `(${_dumpsInline(item)})`);
                lines.push(`${indentStr}${k}=[\n${indentStr}  ` + parts.join(`\n${indentStr}  `) + `\n${indentStr}]`);
            } else if (isObject(v) && _getKeyedTabularHeaders(v).length > 0) {
                const headers = _getKeyedTabularHeaders(v);
                const headerStrs: string[] = [];
                for (const h of headers) {
                    if (Array.isArray(h) && h.length === 2) {
                        headerStrs.push(_formatHeaderTuple(h));
                    } else {
                        const firstVal = Object.values(v as any)[0] as any;
                        if (firstVal && isObject(firstVal[h])) {
                            headerStrs.push(`${h}()`);
                        } else if (firstVal && Array.isArray(firstVal[h])) {
                            headerStrs.push(`${h}[]`);
                        } else {
                            headerStrs.push(String(h));
                        }
                    }
                }
                const headerStr = headerStrs.join(" ");
                lines.push(`${indentStr}${k}{}`);
                lines.push(`${indentStr}  ${headerStr}`);
                
                for (const [dictKey, item] of Object.entries(v as any)) {
                    let valsStr = `${_dumpPrimitive(dictKey)} ` + headers.map(h => _formatValueForHeader(item, h)).join(" ");
                    const headerKeysSet = new Set(headers.map(h => Array.isArray(h) && h.length === 2 ? h[0] : h));
                    
                    const extraKeys = Object.keys(item as object).filter(ek => !headerKeysSet.has(ek));
                    if (extraKeys.length > 0) {
                        const extraDict: any = {};
                        for (const ek of extraKeys) {
                            extraDict[ek] = (item as any)[ek];
                        }
                        valsStr += ` ${_dumpsInline(extraDict)}`;
                    }
                    lines.push(`${indentStr}  ${valsStr}`);
                }
            } else if (isObject(v) && _isDictOfArrays(v)) {
                lines.push(`${indentStr}${k}{[]}`);
                for (const [dictKey, arr] of Object.entries(v as any)) {
                    const valsStr = `${_dumpPrimitive(dictKey)} ` + (arr as any[]).map((x: any) => _dumpPrimitive(x)).join(" ");
                    lines.push(`${indentStr}  ${valsStr}`);
                }
            } else if (isObject(v)) {
                if (_isFlatDict(v)) {
                    const headers = Object.keys(v as any);
                    const headerStr = headers.join(" ");
                    const valsStr = headers.map(hk => {
                        const val = (v as any)[hk];
                        if (Array.isArray(val)) {
                            return "[" + val.map(x => _dumpPrimitive(x)).join(" ") + "]";
                        }
                        return _dumpPrimitive(val);
                    }).join(" ");
                    lines.push(`${indentStr}${k}`);
                    lines.push(`${indentStr}  ${headerStr}`);
                    lines.push(`${indentStr}  ${valsStr}`);
                } else {
                    lines.push(`${indentStr}${k}=(${_dumpsInline(v)})`);
                }
            } else if (Array.isArray(v)) {
                lines.push(`${indentStr}${k}=${_dumpsInline(v)}`);
            } else {
                lines.push(`${indentStr}${k}=${_dumpsInline(v)}`);
            }
        }
        return lines.join("\n");
        
    } else if (Array.isArray(obj)) {
        if (obj.length > 0 && _getHybridHeaders(obj).length > 0) {
            const headers = _getHybridHeaders(obj);
            const headerStrs: string[] = [];
            for (const h of headers) {
                if (Array.isArray(h) && h.length === 2) {
                    headerStrs.push(_formatHeaderTuple(h));
                } else {
                    const firstVal = obj[0][h];
                    if (isObject(firstVal)) {
                        headerStrs.push(`${h}()`);
                    } else if (Array.isArray(firstVal)) {
                        headerStrs.push(`${h}[]`);
                    } else {
                        headerStrs.push(String(h));
                    }
                }
            }
            const lines = ["[]", "  " + headerStrs.join(" ")];
            for (const item of obj) {
                let valsStr = headers.map(h => _formatValueForHeader(item, h)).join(" ");
                const headerKeysSet = new Set(headers.map(h => Array.isArray(h) && h.length === 2 ? h[0] : h));
                const extraKeys = Object.keys(item).filter(ek => !headerKeysSet.has(ek));
                if (extraKeys.length > 0) {
                    const extraDict: any = {};
                    for (const ek of extraKeys) {
                        extraDict[ek] = item[ek];
                    }
                    valsStr += ` ${_dumpsInline(extraDict)}`;
                }
                lines.push("  " + valsStr);
            }
            return lines.join("\n");
        }
        return indentStr + _dumpsInline(obj);
    } else {
        return indentStr + _dumpPrimitive(obj);
    }
}

export function dumps(obj: any): string {
    return _dumps(obj, 0);
}

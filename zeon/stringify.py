import re

def _needs_quotes(s: str) -> bool:
    if not isinstance(s, str):
        return False
    if not s:
        return True
    if re.search(r'[\s,"\'\(\)\[\]=\{\}\:]', s):
        return True
    if s.lower() in ('true', 'false', 'null', 'none'):
        return True
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False

def _dump_primitive(val) -> str:
    if val is None:
        return "None"
    elif isinstance(val, bool):
        return "True" if val else "False"
    elif isinstance(val, (int, float)):
        return str(val)
    elif isinstance(val, str):
        if _needs_quotes(val):
            return '"' + val.replace('"', '\\"') + '"'
        return val
    else:
        return f'"{str(val)}"'

def _is_flat_enough_for_headers(v) -> bool:
    if not isinstance(v, dict):
        return True
    for val in v.values():
        if isinstance(val, (dict, list)):
            return False
    return True

def _get_hybrid_headers(lst: list) -> list:
    if not lst or not isinstance(lst[0], dict):
        return []
    common_keys = set(lst[0].keys())
    for item in lst[1:]:
        if not isinstance(item, dict):
            return []
        common_keys.intersection_update(item.keys())
    if not common_keys:
        return []
    headers = []
    for k in lst[0].keys():
        if k in common_keys:
            v1 = lst[0][k]
            if isinstance(v1, dict) and _is_flat_enough_for_headers(v1):
                sub_keys = set(v1.keys())
                valid = True
                for item in lst[1:]:
                    v2 = item[k]
                    if not isinstance(v2, dict) or set(v2.keys()) != sub_keys:
                        valid = False
                        break
                if valid:
                    headers.append((k, list(v1.keys())))
                else:
                    headers.append(k)
            else:
                headers.append(k)
    return headers

def _get_keyed_tabular_headers(d: dict) -> list:
    if not d or not isinstance(d, dict):
        return []
    return _get_hybrid_headers(list(d.values()))

def _is_matrix_2d(lst: list) -> bool:
    if not lst or not isinstance(lst[0], list):
        return False
    for item in lst:
        if not isinstance(item, list):
            return False
        for v in item:
            if isinstance(v, dict) or isinstance(v, list):
                return False
    return True

def _is_flat_dict(d: dict) -> bool:
    for v in d.values():
        if isinstance(v, dict):
            return False
        # allow 1D arrays of primitives in flat dict
        if isinstance(v, list):
            for x in v:
                if isinstance(x, (dict, list)):
                    return False
    return True


def _format_header_tuple(header) -> str:
    if isinstance(header, tuple):
        return f"{header[0]}({' '.join(header[1])})"
    return header

def _format_value_for_header(item, header) -> str:
    if isinstance(header, tuple):
        main_k, sub_k = header
        val_dict = item.get(main_k, {})
        vals = [_dump_primitive(val_dict.get(sk)) for sk in sub_k]
        return f"({' '.join(vals)})"
    else:
        v = item.get(header)
        if isinstance(v, dict):
            return f"({_dumps_inline(v)})"
        elif isinstance(v, list):
            return _dumps_inline(v)
        return _dump_primitive(v)

def _dumps_inline(obj) -> str:
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            if isinstance(v, dict):
                parts.append(f"{k}=({_dumps_inline(v)})")
            elif isinstance(v, list):
                parts.append(f"{k}={_dumps_inline(v)}")
            else:
                parts.append(f"{k}={_dumps_inline(v)}")
        return " ".join(parts)
    elif isinstance(obj, list):
        parts = []
        for v in obj:
            if isinstance(v, dict):
                parts.append(f"({_dumps_inline(v)})")
            else:
                parts.append(_dumps_inline(v))
        return "[" + " ".join(parts) + "]"
    else:
        return _dump_primitive(obj)

def _dumps(obj, indent_level=0) -> str:
    indent_str = "  " * indent_level
    
    if isinstance(obj, dict):
        has_tabular = any(isinstance(v, list) and (len(_get_hybrid_headers(v)) > 0 or _is_matrix_2d(v)) for v in obj.values())
        has_keyed_tabular = any(isinstance(v, dict) and len(_get_keyed_tabular_headers(v)) > 0 for v in obj.values())
        if not has_tabular and not has_keyed_tabular and indent_level > 0:
            return indent_str + "(" + _dumps_inline(obj) + ")"
            
        lines = []
        for k, v in obj.items():
            if isinstance(v, list) and _is_matrix_2d(v):
                lines.append(f"{indent_str}{k}[][]")
                for row in v:
                    vals_str = " ".join([_dump_primitive(x) for x in row])
                    lines.append(f"{indent_str}  {vals_str}")
            elif isinstance(v, list) and len(_get_hybrid_headers(v)) > 0:
                headers = _get_hybrid_headers(v)
                
                header_strs = []
                for h in headers:
                    if isinstance(h, tuple):
                        header_strs.append(_format_header_tuple(h))
                    else:
                        first_val = v[0].get(h)
                        if isinstance(first_val, dict):
                            header_strs.append(f"{h}()")
                        elif isinstance(first_val, list):
                            header_strs.append(f"{h}[]")
                        else:
                            header_strs.append(str(h))
                            
                header_str = " ".join(header_strs)
                
                lines.append(f"{indent_str}{k}[]")
                lines.append(f"{indent_str}  {header_str}")
                for item in v:
                    vals_str = " ".join([_format_value_for_header(item, h) for h in headers])
                    
                    header_keys_set = set(h[0] if isinstance(h, tuple) else h for h in headers)
                    extra_keys = [ek for ek in item.keys() if ek not in header_keys_set]
                    if extra_keys:
                        extra_dict = {ek: item[ek] for ek in extra_keys}
                        vals_str += f" {_dumps_inline(extra_dict)}"
                        
                    lines.append(f"{indent_str}  {vals_str}")
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                parts = [f"({_dumps_inline(item)})" for item in v]
                lines.append(f"{indent_str}{k}=[\n{indent_str}  " + f"\n{indent_str}  ".join(parts) + f"\n{indent_str}]")
            elif isinstance(v, dict) and len(_get_keyed_tabular_headers(v)) > 0:
                headers = _get_keyed_tabular_headers(v)
                header_strs = []
                for h in headers:
                    if isinstance(h, tuple):
                        header_strs.append(_format_header_tuple(h))
                    else:
                        first_val = list(v.values())[0].get(h)
                        if isinstance(first_val, dict):
                            header_strs.append(f"{h}()")
                        elif isinstance(first_val, list):
                            header_strs.append(f"{h}[]")
                        else:
                            header_strs.append(str(h))
                header_str = " ".join(header_strs)
                
                lines.append(f"{indent_str}{k}{{}}")
                lines.append(f"{indent_str}  {header_str}")
                for dict_key, item in v.items():
                    vals_str = f"{_dump_primitive(dict_key)} " + " ".join([_format_value_for_header(item, h) for h in headers])
                    header_keys_set = set(h[0] if isinstance(h, tuple) else h for h in headers)
                    extra_keys = [ek for ek in item.keys() if ek not in header_keys_set]
                    if extra_keys:
                        extra_dict = {ek: item[ek] for ek in extra_keys}
                        vals_str += f" {_dumps_inline(extra_dict)}"
                    lines.append(f"{indent_str}  {vals_str}")
            elif isinstance(v, dict):
                if _is_flat_dict(v):
                    headers = list(v.keys())
                    header_str = " ".join(headers)
                    vals_str = " ".join([_dump_primitive(v[hk]) if not isinstance(v[hk], list) else "[" + " ".join([_dump_primitive(x) for x in v[hk]]) + "]" for hk in headers])
                    lines.append(f"{indent_str}{k}")
                    lines.append(f"{indent_str}  {header_str}")
                    lines.append(f"{indent_str}  {vals_str}")
                else:
                    lines.append(f"{indent_str}{k}=({_dumps_inline(v)})")
            elif isinstance(v, list):
                lines.append(f"{indent_str}{k}={_dumps_inline(v)}")
            else:
                lines.append(f"{indent_str}{k}={_dumps_inline(v)}")
        return "\n".join(lines)
        
    elif isinstance(obj, list):
        return indent_str + _dumps_inline(obj)
    else:
        return indent_str + _dump_primitive(obj)

def dumps(obj) -> str:
    return _dumps(obj, 0)

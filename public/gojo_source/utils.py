# utils.py
import re
from state import memory
from stdlib import builtins

# --- İFADE TEMİZLEYİCİ ---
def clean_expr(expr):
    if not isinstance(expr, str): return expr
    
    placeholders = {}
    def mask_string(match):
        key = f"___STR{len(placeholders)}___"
        placeholders[key] = match.group(0)
        return key
    masked_expr = re.sub(r'("[^"]*")', mask_string, expr)

    # Mantık Dönüşümleri
    masked_expr = masked_expr.replace('!=', '___NEQ___')
    masked_expr = masked_expr.replace(' isnt ', ' ___NEQ___ ')
    masked_expr = masked_expr.replace('&&', ' and ')
    masked_expr = masked_expr.replace('||', ' or ')
    masked_expr = masked_expr.replace('!', ' not ') 
    masked_expr = masked_expr.replace('___NEQ___', '!=')
    
    for key, val in placeholders.items(): masked_expr = masked_expr.replace(key, val)
    return masked_expr

# --- TİP KONTROL VE PARSE ---
def parse_value(hedef_tip, ifade):
    temiz_ifade = clean_expr(ifade)
    try: 
        deger = eval(temiz_ifade, builtins, memory)
    except: deger = ifade

    if '[]' in hedef_tip:
        if not isinstance(deger, list): raise ValueError(f"Dizi hatasi: '{deger}'")
        ana_tip = hedef_tip.replace('[]', '') 
        yeni_liste = []
        for item in deger:
            yeni_liste.append(parse_value(ana_tip, str(item)))
        return yeni_liste

    if hedef_tip == 'int':
        try: return int(deger)
        except: raise ValueError(f"Int hatasi: '{deger}'")
    elif hedef_tip == 'double':
        try: return float(deger)
        except: raise ValueError(f"Double hatasi: '{deger}'")
    elif hedef_tip == 'string':
        try: return str(deger)
        except: raise ValueError(f"String hatasi: '{deger}'")
    elif hedef_tip == 'bool':
        val = str(deger).lower()
        if val not in ['true', 'false']: raise ValueError(f"Bool hatasi: '{deger}'")
        return val == 'true'
    elif hedef_tip == 'char':
        text = str(deger)
        if len(text) > 1 or len(text) == 0: raise ValueError(f"Char hatasi: '{text}'")
        return text
    return deger

# --- FORMATLAMA ---
def format_text(text):
    if not isinstance(text, str): return text
    bulunan = re.findall(r'\{([^}]+)\}', text)
    for ifade in bulunan:
        try:
            val = eval(clean_expr(ifade), builtins, memory)
            text = text.replace("{" + ifade + "}", str(val))
        except Exception as e: raise ValueError(f"Metin ici ifade hatasi: '{{{ifade}}}' -> {e}")
    text = text.replace(r'\n', '\n').replace(r'\t', '\t').replace(r'\"', '"')
    return text
# core.py
import os
import re
from state import memory, var_types, functions, call_stack  # functions ve call_stack eklendi
from stdlib import builtins
from utils import clean_expr, parse_value, format_text

def run_gojo(filename):
    if not os.path.exists(filename):
        print(f"HATA: '{filename}' bulunamadı.")
        return

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    print(f"Gojo v7.0 Çalışıyor: {filename}\n")
    print("-" * 30)
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Yorum temizleme
        in_string = False
        comment_pos = -1
        for idx, ch in enumerate(line):
            if ch == '"' and (idx == 0 or line[idx-1] != '\\'):
                in_string = not in_string
            elif ch == '#' and not in_string:
                comment_pos = idx
                break
        if comment_pos != -1:
            line = line[:comment_pos].strip()
        if not line:
            i += 1
            continue

        first_word = line.split()[0]

        # Önce şu anki kelimenin "Parantezden önceki kısmını" alalım
        # Örn: "topla(10,"  -> "topla" olur.
        func_candidate = first_word.split('(')[0]

        # --- YENİ: FUNCTION CALL (GENEL, SATIR İÇİ DEĞER DÖNÜŞÜ DE DESTEKLİ) ---
        # Satırın ilk görünen fonksiyon çağrısını yakala (gömülü veya tek başına)
        m = re.search(r'(\w+)\s*\((.*?)\)', line)
        if m and m.group(1) in functions:
            func_name = m.group(1)
            func_data = functions[func_name]
            args_str = m.group(2).strip()
            if args_str:
                call_args = [arg.strip() for arg in args_str.split(',')]
            else:
                call_args = []

            # Parametre sayısı kontrolü
            if len(call_args) != len(func_data['args']):
                print(f"HATA: '{func_name}' fonksiyonu {len(func_data['args'])} parametre bekliyor, {len(call_args)} verildi.")
                i += 1
                continue

            try:
                # temiz return alanı
                memory['__last_ret__'] = None

                # Map params
                for idx, param_name in enumerate(func_data['args']):
                    val = eval(clean_expr(call_args[idx]), builtins, memory)
                    memory[param_name] = val
                    if isinstance(val, int): var_types[param_name] = 'int'
                    elif isinstance(val, float): var_types[param_name] = 'double'
                    elif isinstance(val, str): var_types[param_name] = 'string'

                # Determine if call is embedded (e.g., "x = fn(...)" or "print(fn(...))")
                call_span_start, call_span_end = m.start(0), m.end(0)
                embedded = not line.strip() == line[call_span_start:call_span_end].strip()

                # Push a tuple: (return_line_index, reprocess_flag, original_line, call_span_start, call_span_end)
                call_stack.append((i, embedded, lines[i], call_span_start, call_span_end))

                # Jump into function body
                i = func_data['start_line']
                continue
            except Exception as e:
                print(f"Fonksiyon cagirma hatasi: {e}")
                return

        # --- YENİ: FUN (Fonksiyon Tanımlama) ---
        # Örn: fun topla(a, b)
        elif first_word == 'fun':
            try:
                # Regex ile isim ve parametreleri al
                match = re.search(r'fun\s+(\w+)\s*\((.*)\)', line)
                if match:
                    f_name = match.group(1)
                    f_args_str = match.group(2).strip()
                    if f_args_str:
                        f_args = [arg.strip() for arg in f_args_str.split(',')]
                    else:
                        f_args = []
                    
                    # Fonksiyonu kaydet
                    functions[f_name] = {
                        'args': f_args,
                        'start_line': i + 1  # Başlangıç satırı: fonksiyon gövdesinin ilk satırı
                    }
                    
                    # ÖNEMLİ: Fonksiyonun içini şimdi çalıştırma! 'cursed' bulana kadar atla.
                    nested_fun = 0
                    temp_i = i + 1
                    found_end = False
                    while temp_i < len(lines):
                        chk_line = lines[temp_i].strip().split()
                        if not chk_line: 
                            temp_i += 1
                            continue
                        
                        if chk_line[0] == 'fun': nested_fun += 1
                        elif chk_line[0] == 'cursed':
                            if nested_fun == 0:
                                i = temp_i # Ana döngüyü 'cursed' satırına taşı (atla)
                                found_end = True
                                break
                            nested_fun -= 1
                        temp_i += 1
                    
                    if not found_end:
                        print(f"HATA: '{f_name}' fonksiyonu kapatilmamis (cursed eksik).")
                        return
                else:
                    print(f"HATA: Hatali fonksiyon tanimi. Ornek: fun isim(a, b)")
                    return
            except Exception as e:
                print(f"Fonksiyon tanimlama hatasi: {e}")
                return

        # --- YENİ: CURSED (Fonksiyon Sonu / Return) ---
        elif first_word == 'cursed':
            # Eğer bir fonksiyon çağrısından geldiysek, geri dön
            if len(call_stack) > 0:
                ret_entry = call_stack.pop()
                # ret_entry: (return_line_index, embedded_flag, original_line, start, end)
                if isinstance(ret_entry, tuple):
                    return_line, embedded, orig_line, cs, ce = ret_entry
                    if embedded:
                        # Replace the function call in the original line with the returned value literal
                        repl = repr(memory.get('__last_ret__'))
                        new_line = orig_line[:cs] + repl + orig_line[ce:]
                        # preserve newline if existed
                        if lines[return_line].endswith("\n"):
                            lines[return_line] = new_line.rstrip("\n") + "\n"
                        else:
                            lines[return_line] = new_line
                        # Re-run the same line after return: set i = return_line - 1 so i +=1 processes it
                        i = return_line - 1
                    else:
                        i = return_line
                else:
                    # backward compatibility: integer entry
                    i = ret_entry
            else:
                pass

        # --- YENİ: RETURN (Fonksiyon İçinden Değer Döndürme) ---
        elif first_word == 'return':
            expr = line[len('return'):].strip()
            try:
                if expr:
                    val = eval(clean_expr(expr), builtins, memory)
                else:
                    val = None
                memory['__last_ret__'] = val
                if len(call_stack) > 0:
                    ret_entry = call_stack.pop()
                    if isinstance(ret_entry, tuple):
                        return_line, embedded, orig_line, cs, ce = ret_entry
                        if embedded:
                            repl = repr(memory.get('__last_ret__'))
                            new_line = orig_line[:cs] + repl + orig_line[ce:]
                            if lines[return_line].endswith("\n"):
                                lines[return_line] = new_line.rstrip("\n") + "\n"
                            else:
                                lines[return_line] = new_line
                            i = return_line - 1
                        else:
                            i = return_line
                    else:
                        i = ret_entry
                else:
                    pass
            except Exception as e:
                print(f"Return hatasi: {e}")
                return

        # 1. TANIMLAMA
        base_types = ['int', 'string', 'double', 'bool', 'char']
        if (first_word in base_types) or first_word.endswith('[]') or first_word == 'array[]':
            tip = first_word
            if ',' in line and '=' not in line:
                vars_part = line[len(tip):].strip()
                var_list = [v.strip() for v in vars_part.split(',')]
                for var_name in var_list:
                    if tip.endswith('[]') or tip == 'array[]': memory[var_name] = []
                    elif tip == 'int': memory[var_name] = 0
                    elif tip == 'string': memory[var_name] = ""
                    elif tip == 'double': memory[var_name] = 0.0
                    elif tip == 'bool': memory[var_name] = False
                    elif tip == 'char': memory[var_name] = ''
                    var_types[var_name] = tip
            elif '=' in line:
                parts = line.split('=', 1)
                sol = parts[0].strip().split()
                sag = parts[1].strip()
                tip, isim = sol[0], sol[1]
                try:
                    if sag.startswith('input'):
                        soru = sag[5:].strip().strip('"') if len(sag) > 5 else ""
                        val = input(soru + " ")
                        memory[isim] = parse_value(tip, f'"{val}"')
                    else:
                        memory[isim] = parse_value(tip, sag)
                    var_types[isim] = tip
                except Exception as e:
                    print(f"HATA (Satır {i+1}): {e}")
                    return
            else:
                parts = line.split()
                if len(parts) > 1:
                    var = parts[1]
                    if tip.endswith('[]') or tip == 'array[]': memory[var] = []
                    elif tip == 'int': memory[var] = 0
                    elif tip == 'string': memory[var] = ""
                    elif tip == 'double': memory[var] = 0.0
                    elif tip == 'bool': memory[var] = False
                    elif tip == 'char': memory[var] = ''
                    var_types[var] = tip

        # 1.b ADD (yeni söz dizimi: add((var) <değer>) — parantezli değişken adı kabul edilir)
        elif first_word == 'add':
            parts = line.split(None, 2)
            if len(parts) < 3:
                print(f"HATA: add kullanım: add((degisken) <değer>)")
            else:
                raw = parts[1].strip()
                # Require parantezli değişken adı: e.g. add((myList)
                if not (raw.startswith('(') and raw.endswith(')')):
                    print(f"HATA: add kullanım: add((degisken) <değer>) — parantezli değişken adı zorunludur")
                    i += 1
                    continue
                varname = raw.lstrip('(').rstrip(')')
                expr = parts[2]
                if varname in memory and isinstance(memory[varname], list):
                    vtip = var_types.get(varname, None)
                    try:
                        if vtip and vtip.endswith('[]') and vtip != 'array[]':
                            val = parse_value(vtip.replace('[]',''), expr)
                        else:
                            val = eval(clean_expr(expr), builtins, memory)
                        memory[varname].append(val)
                    except Exception as e:
                        print(f"Add hatasi: {e}")

        # 1.c APPEND (+=)
        elif '+=' in line and first_word not in ['if', 'while', 'for', 'print', 'println', 'con']:
            try:
                parts = line.split('+=',1)
                varname = parts[0].strip()
                expr = parts[1].strip()
                if varname in memory:
                    if isinstance(memory[varname], list):
                         val = eval(clean_expr(expr), builtins, memory)
                         if isinstance(val, list): memory[varname].extend(val)
                         else: memory[varname].append(val)
                    else:
                         val = eval(clean_expr(expr), builtins, memory)
                         memory[varname] += val
            except Exception as e: print(f"Atama hatasi: {e}")

        # 2. GÜNCELLEME (=)
        elif '=' in line and first_word not in ['if', 'while', 'for', 'print', 'println', 'con', 'add'] + base_types:
            parts = line.split('=', 1)
            var_expr, expr = parts[0].strip(), parts[1].strip()
            try:
                if '[' in var_expr and ']' in var_expr: 
                    base_name = var_expr.split('[')[0]
                    if base_name in memory:
                        val = eval(clean_expr(expr), builtins, memory)
                        mevcut = eval(var_expr, builtins, memory)
                        if isinstance(mevcut, int) and not isinstance(mevcut, bool): val = int(val)
                        elif isinstance(mevcut, float): val = float(val)
                        # val yerine repr(val) kullanıyoruz ki stringlerin tırnakları korunsun
                        exec(f"memory['{base_name}']{var_expr[len(base_name):]} = {repr(val)}")
                elif var_expr in memory:
                    if expr.startswith('input'):
                        soru = expr[5:].strip().strip('"') if len(expr) > 5 else ""
                        val = input(soru + " ")
                    else:
                        val = eval(clean_expr(expr), builtins, memory)
                    
                    eski = memory[var_expr]
                    if isinstance(eski, bool): val = str(val).lower() == 'true'
                    elif isinstance(eski, int): val = int(val)
                    elif isinstance(eski, float): val = float(val)
                    elif isinstance(eski, str): val = str(val)
                    memory[var_expr] = val
            except Exception as e: print(f"Atama hatasi: {e}")

        # 3. PRINT / PRINTLN
        elif first_word == 'print':
            try:
                res = eval(clean_expr(line[5:].strip()), builtins, memory)
                print(f"{format_text(str(res))}", end='', flush=True)
            except Exception as e: print(f"HATA: {e}")
        elif first_word == 'println':
            if len(line.strip()) == 7: print()
            else:
                try:
                    res = eval(clean_expr(line[7:].strip()), builtins, memory)
                    print(f"{format_text(str(res))}")
                except: print(f"HATA: Yazdirma hatasi")

        # 4. FOR
        elif first_word == 'for':
            try:
                match = re.search(r'for\s+(\w+)\s*=\s*(.+?)\s+to\s+(.+?)(?:\s+but\s+(.+))?$', line)
                if match:
                    var_name = match.group(1)
                    start = int(eval(match.group(2), builtins, memory))
                    end = int(eval(match.group(3), builtins, memory))
                    step = 1
                    if match.group(4): step = int(eval(match.group(4), builtins, memory))
                    memory[var_name] = start
                    
                    skip = False
                    if step > 0 and start > end: skip = True
                    elif step < 0 and start < end: skip = True
                    
                    if skip:
                        nested = 0
                        while i < len(lines):
                            i += 1
                            if i >= len(lines): break
                            curr = lines[i].strip().split()[0]
                            if curr == 'for': nested += 1
                            elif curr == 'con':
                                if nested == 0: break
                                nested -= 1
            except: pass

        # 5. CON
        elif first_word == 'con':
            nested = 0
            temp_i = i - 1
            while temp_i >= 0:
                s_line = lines[temp_i].strip()
                if not s_line: 
                    temp_i -= 1
                    continue
                s_word = s_line.split()[0]
                if s_word == 'con': nested += 1
                elif s_word == 'for':
                    if nested == 0:
                        match = re.search(r'for\s+(\w+)\s*=\s*(.+?)\s+to\s+(.+?)(?:\s+but\s+(.+))?$', s_line)
                        if match:
                            var = match.group(1)
                            end = int(eval(match.group(3), builtins, memory))
                            step = 1
                            if match.group(4): step = int(eval(match.group(4), builtins, memory))
                            
                            memory[var] += step
                            curr = memory[var]
                            cont = False
                            if step > 0 and curr <= end: cont = True
                            elif step < 0 and curr >= end: cont = True
                            
                            if cont: i = temp_i
                            break
                    else: nested -= 1
                temp_i -= 1

        # 6. IF
        elif first_word == 'if':
             try:
                cond = eval(clean_expr(line[2:].strip()), builtins, memory)
                if not cond:
                    nested = 0
                    while i < len(lines):
                        i += 1
                        if i >= len(lines): break
                        # --- DÜZELTME BAŞLANGICI ---
                        s_line = lines[i].strip()
                        if not s_line: continue  # Boş satırsa atla
                        curr = s_line.split()[0]
                        # --- DÜZELTME BİTİŞİ ---
                        
                        if curr == 'if': nested += 1
                        elif curr == 'finn':
                            if nested == 0: break
                            nested -= 1
                        elif curr == 'else':
                            if nested == 0: break
             except Exception as e:
                 print(f"IF HATASI (Satır {i+1}): {e}")
                 return

        # 7. ELSE
        elif first_word == 'else':
             nested = 0
             while i < len(lines):
                i += 1
                if i >= len(lines): break
                # --- DÜZELTME BAŞLANGICI ---
                s_line = lines[i].strip()
                if not s_line: continue  # Boş satırsa atla
                curr = s_line.split()[0]
                # --- DÜZELTME BİTİŞİ ---
                
                if curr == 'if': nested += 1
                elif curr == 'finn':
                    if nested == 0: break
                    nested -= 1

        # 8. WHILE
        elif first_word == 'while':
             try:
                 if not eval(clean_expr(line[5:].strip()), builtins, memory):
                     nested = 0
                     while i < len(lines):
                         i += 1
                         if i >= len(lines): break
                         # --- DÜZELTME BAŞLANGICI ---
                         s_line = lines[i].strip()
                         if not s_line: continue
                         curr = s_line.split()[0]
                         # --- DÜZELTME BİTİŞİ ---
                         
                         if curr == 'while': nested += 1
                         elif curr == 'end':
                             if nested == 0: break
                             nested -= 1
             except Exception as e:
                     print(f"WHILE HATASI (Satır {i+1}): {e}")
                     return

        elif first_word == 'finn': pass
        elif first_word == 'end':
            temp_i = i - 1
            while temp_i >= 0:
                s = lines[temp_i].strip()
                if not s: 
                    temp_i -= 1
                    continue
                if s.startswith('while') and 'end' not in lines[temp_i:i]:
                    if eval(clean_expr(s[5:].strip()), builtins, memory): i = temp_i
                    break
                temp_i -= 1
        # Eğer yukarıdaki hiçbir if/elif bloğuna girmediyse, bu komut geçersizdir.
        else:
            # Sadece boş satır değilse hata ver (Gerçi başta boş satır kontrolü var ama garanti olsun)
            if line.strip():
                print(f"HATA (Satir {i+1}): Bilinmeyen komut veya yazim hatasi -> '{first_word}'")
                return # Programı burada kes
        i += 1
    print("\n" + "-" * 30)
# core.py
import os
import re
from state import memory, var_types, functions, call_stack
from stdlib import builtins
from utils import clean_expr, parse_value, format_text

def run_gojo(filename):
    if not os.path.exists(filename):
        print(f"HATA: '{filename}' bulunamadı.")
        return

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    print(f"Gojo v7.2 (Fix: Indentation Offset) Çalışıyor: {filename}\n")
    print("-" * 30)
    
    # Değiştirilen satırların orjinal halini tutan hafıza
    modified_lines = {} 

    i = 0
    while i < len(lines):
        # --- ZAMAN GERİ ALMA (Restoration) ---
        # Eğer bir satırı değiştirdiysek ve o satırdan çıktıysak, eski haline getir.
        to_remove = []
        for mod_i, orig_line in modified_lines.items():
            if mod_i != i: 
                lines[mod_i] = orig_line
                to_remove.append(mod_i)
        for mod_i in to_remove:
            del modified_lines[mod_i]
        # -------------------------------------

        # Orjinal satırı al (girintileriyle beraber)
        original_line_content = lines[i]
        line = original_line_content.strip()
        
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

        # --- KRİTİK DÜZELTME: Girinti (Indentation) Hesaplama ---
        # Regex araması 'line' (temizlenmiş) üzerinde yapılırken,
        # Değişiklik 'original_line_content' (boşluklu) üzerinde yapılacak.
        # Bu yüzden aradaki farkı (offset) bulmamız lazım.
        indent_offset = 0
        if line:
            # Satırın orjinalinde, temiz halinin başladığı yeri bul
            found_idx = original_line_content.find(line)
            if found_idx >= 0:
                indent_offset = found_idx
        # -------------------------------------------------------

        # 1. FUNCTION CALL (Fonksiyon Çağrısı)
        # Satırın içindeki fonksiyon çağrısını bul (Örn: kareAl(5))
        m = re.search(r'(\w+)\s*\((.*?)\)', line)
        if m and m.group(1) in functions:
            func_name = m.group(1)
            func_data = functions[func_name]
            args_str = m.group(2).strip()
            
            # Parametreleri ayır
            call_args = []
            if args_str:
                current_arg = ""
                paren_count = 0
                bracket_count = 0
                in_str = False
                for char in args_str:
                    if char == '"': in_str = not in_str
                    if not in_str:
                        if char == '(': paren_count += 1
                        elif char == ')': paren_count -= 1
                        elif char == '[': bracket_count += 1
                        elif char == ']': bracket_count -= 1
                    
                    if char == ',' and paren_count == 0 and bracket_count == 0 and not in_str:
                        call_args.append(current_arg.strip())
                        current_arg = ""
                    else:
                        current_arg += char
                if current_arg: call_args.append(current_arg.strip())

            if len(call_args) != len(func_data['args']):
                print(f"HATA: '{func_name}' {len(func_data['args'])} parametre bekliyor.")
                i += 1
                continue

            try:
                memory['__last_ret__'] = None
                for idx, param_name in enumerate(func_data['args']):
                    val = eval(clean_expr(call_args[idx]), builtins, memory)
                    memory[param_name] = val
                    if isinstance(val, int): var_types[param_name] = 'int'
                    elif isinstance(val, float): var_types[param_name] = 'double'
                    elif isinstance(val, str): var_types[param_name] = 'string'

                # --- KRİTİK DÜZELTME UYGULANIYOR ---
                # Regex konumu (stripped) + Indentation Offset = Gerçek Konum
                call_span_start = m.start(0) + indent_offset
                call_span_end = m.end(0) + indent_offset
                
                # Embedded kontrolü (Tam satır mı, yoksa println içinde mi?)
                embedded = not line.strip() == m.group(0)

                # Stack'e kaydet
                call_stack.append((i, embedded, lines[i], call_span_start, call_span_end)) 
                
                # Fonksiyona zıpla
                i = func_data['start_line']
                continue
            except Exception as e:
                print(f"Fonksiyon cagirma hatasi: {e}")
                return

        # 2. FUN (Fonksiyon Tanımlama)
        elif first_word == 'fun':
            match = re.search(r'fun\s+(\w+)\s*\((.*)\)', line)
            if match:
                f_name = match.group(1)
                f_args_str = match.group(2).strip()
                f_args = [arg.strip() for arg in f_args_str.split(',')] if f_args_str else []
                
                functions[f_name] = {'args': f_args, 'start_line': i + 1}
                
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
                            i = temp_i + 1
                            found_end = True
                            break
                        nested_fun -= 1
                    temp_i += 1
                
                if not found_end: 
                    print(f"HATA: '{f_name}' fonksiyonu kapatilmamis (cursed eksik).")
                    return
                continue
            else: 
                print(f"HATA: Hatali fonksiyon tanimi.")
                return

        # 3. CURSED (Return / End)
        elif first_word == 'cursed':
            if len(call_stack) > 0:
                ret_entry = call_stack.pop()
                if isinstance(ret_entry, tuple):
                    return_line, embedded, orig_line, cs, ce = ret_entry
                    
                    if embedded:
                        # Orjinal satırı sakla (Zamanı geri almak için)
                        if return_line not in modified_lines:
                            modified_lines[return_line] = lines[return_line]

                        # Değeri yerine koy
                        repl = repr(memory.get('__last_ret__'))
                        
                        # --- DÜZELTME: Offset kullanıldığı için artık kesme işlemi doğru ---
                        new_line = orig_line[:cs] + repl + orig_line[ce:]
                        
                        if lines[return_line].endswith("\n"):
                            lines[return_line] = new_line.rstrip("\n") + "\n"
                        else:
                            lines[return_line] = new_line
                        
                        i = return_line # O satırı tekrar işle
                    else:
                        i = return_line + 1
                else:
                    i = ret_entry
            else:
                i += 1
            continue

        # 4. RETURN
        elif first_word == 'return':
            expr = line[len('return'):].strip()
            try:
                val = eval(clean_expr(expr), builtins, memory) if expr else None
                memory['__last_ret__'] = val
                
                if len(call_stack) > 0:
                    ret_entry = call_stack.pop()
                    if isinstance(ret_entry, tuple):
                        return_line, embedded, orig_line, cs, ce = ret_entry
                        
                        if embedded:
                            if return_line not in modified_lines:
                                modified_lines[return_line] = lines[return_line]

                            repl = repr(memory.get('__last_ret__'))
                            new_line = orig_line[:cs] + repl + orig_line[ce:]
                            
                            if lines[return_line].endswith("\n"):
                                lines[return_line] = new_line.rstrip("\n") + "\n"
                            else:
                                lines[return_line] = new_line
                            
                            i = return_line
                        else:
                            i = return_line + 1
                    else:
                        i = ret_entry
                else:
                    i += 1
                continue
            except Exception as e: 
                print(f"Return hatasi: {e}")
                return

        # 5. TANIMLAMA (int, string vs.)
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

        # 6. ADD
        elif first_word == 'add':
            parts = line.split(None, 2)
            if len(parts) < 3:
                print(f"HATA: add kullanım: add((degisken) <değer>)")
            else:
                raw = parts[1].strip()
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

        # 7. APPEND (+=)
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

        # 8. GÜNCELLEME (=)
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

        # 9. PRINT / PRINTLN
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

        # 10. FOR
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

        # 11. CON
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

        # 12. IF
        elif first_word == 'if':
             try:
                cond = eval(clean_expr(line[2:].strip()), builtins, memory)
                if not cond:
                    nested = 0
                    while i < len(lines):
                        i += 1
                        if i >= len(lines): break
                        s_line = lines[i].strip()
                        if not s_line: continue
                        curr = s_line.split()[0]
                        if curr == 'if': nested += 1
                        elif curr == 'finn':
                            if nested == 0: break
                            nested -= 1
                        elif curr == 'else':
                            if nested == 0: break
             except Exception as e:
                 print(f"IF HATASI (Satır {i+1}): {e}")
                 return

        # 13. ELSE
        elif first_word == 'else':
             nested = 0
             while i < len(lines):
                i += 1
                if i >= len(lines): break
                s_line = lines[i].strip()
                if not s_line: continue
                curr = s_line.split()[0]
                if curr == 'if': nested += 1
                elif curr == 'finn':
                    if nested == 0: break
                    nested -= 1

        # 14. WHILE
        elif first_word == 'while':
             try:
                 if not eval(clean_expr(line[5:].strip()), builtins, memory):
                     nested = 0
                     while i < len(lines):
                         i += 1
                         if i >= len(lines): break
                         s_line = lines[i].strip()
                         if not s_line: continue
                         curr = s_line.split()[0]
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
        
        # HATA YAKALAMA
        else:
            if line.strip():
                print(f"HATA (Satir {i+1}): Bilinmeyen komut veya yazim hatasi -> '{first_word}'")
                return 
        i += 1
    print("\n" + "-" * 30)
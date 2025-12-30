# src/state.py

# Değişkenlerin değerleri (x = 5)
memory = {}

# Değişkenlerin tipleri (x: int)
var_types = {}

# YENİ: Fonksiyon Hafızası
# Yapı: {'topla': {'start_line': 5, 'args': ['a', 'b']}}
functions = {}

# YENİ: Çağrı Yığını (Nereye döneceğim?)
call_stack = []
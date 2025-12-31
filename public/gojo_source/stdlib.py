# stdlib.py
import random
import math

# GojoLang içinden çağrılabilen fonksiyonlar
builtins = {
    # Matematik
    'random': random.randint,
    'sqrt': math.sqrt,
    'floor': math.floor,
    'ceil': math.ceil,
    'pow': math.pow,
    'abs': abs,
    
    # Dönüşüm ve Tip İşlemleri
    'str': str,
    'int': int,
    'float': float, # Gojo'da double diyoruz ama Python'da float
    'len': len,
    
    # Sabitler
    'true': True,
    'false': False
}
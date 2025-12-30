# stdlib.py
import random
import math

# GojoLang içinden çağrılabilen fonksiyonlar
builtins = {
    'random': random.randint,
    'len': len,
    'sqrt': math.sqrt,
    'floor': math.floor,
    'ceil': math.ceil,
    'pow': math.pow,
    'abs': abs,
    'true': True,   # Artık küçük harf 'true' tanınıyor
    'false': False  # Artık küçük harf 'false' tanınıyor
}
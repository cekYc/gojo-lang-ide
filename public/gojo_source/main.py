# main.py
import sys
from core import run_gojo

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_gojo(sys.argv[1])
    else:
        print("Kullanim: python main.py <dosya.gj>")
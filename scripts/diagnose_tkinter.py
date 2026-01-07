#!/usr/bin/env python3
"""
Diagnóstico del error de tkinter en BodegaApp
"""
import sys
from pathlib import Path

def check_tkinter_error():
    """Revisar el error específico de tkinter"""
    print("🔍 DIAGNÓSTICO ERROR TKINTER")
    print("="*50)
    
    # Buscar src/app.py
    SCRIPT_DIR = Path(__file__).parent
    PROJECT_ROOT = SCRIPT_DIR.parent
    app_py = PROJECT_ROOT / "src" / "app.py"
    
    if not app_py.exists():
        print(f"❌ No se encuentra: {app_py}")
        return
    
    print(f"📄 Analizando: {app_py}")
    
    try:
        with open(app_py, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar línea 52 (el error indica línea 52)
        if len(lines) >= 52:
            line_52 = lines[51].rstrip()
            print(f"\n📌 Línea 52 de app.py:")
            print(f"   '{line_52}'")
            
            # Buscar patrones comunes
            if '.ar' in line_52:
                print(f"\n⚠️  POSIBLE ERROR: Atributo '.ar' encontrado")
                print("   Buscando alternativas cercanas...")
                
                # Buscar atributos similares en líneas cercanas
                for i in range(max(0, 45), min(len(lines), 60)):
                    line = lines[i].rstrip()
                    if any(attr in line for attr in ['arr', 'array', 'arc', 'art', 'arb']):
                        print(f"   Línea {i+1}: {line}")
            
            # Buscar en todo el archivo referencias a 'ar'
            print(f"\n🔍 Buscando todas las referencias a 'ar' en app.py:")
            for i, line in enumerate(lines):
                if '.ar' in line and not line.strip().startswith('#'):
                    print(f"   Línea {i+1}: {line.rstrip()[:80]}")
        
        print(f"\n💡 SUGERENCIA:")
        print("   El error 'AttributeError: no attribute ar' sugiere:")
        print("   1. Variable mal escrita (ej: 'arr' escrito como 'ar')")
        print("   2. Atributo no inicializado en __init__")
        print("   3. Error en acceso a widget de tkinter")
        print("\n   Revisa la línea 52 y busca atributos similares como:")
        print("   - self.arr (¿array?)")
        print("   - self.arc (¿archivo?)")
        print("   - self.art (¿artículo?)")
        
    except Exception as e:
        print(f"❌ Error analizando archivo: {e}")

if __name__ == "__main__":
    check_tkinter_error()
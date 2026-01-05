#!/usr/bin/env python3
"""
BODEGA REGISTER APP - Punto de entrada principal
Versión: 1.0.0
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    required_packages = ['customtkinter', 'pandas', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Faltan dependencias necesarias:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstalar con:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_environment():
    """Configura el entorno de la aplicación"""
    # Crear directorios necesarios
    directories = ['data', 'data/exports', 'data/backups', 'logs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ Entorno configurado correctamente")

def main():
    """Función principal"""
    print("=" * 50)
    print("BODEGA REGISTER APP - Iniciando...")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    # Configurar entorno
    setup_environment()
    
    try:
        from src.main import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Verifica la estructura del proyecto")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()
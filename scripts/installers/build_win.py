#!/usr/bin/env python3
"""
build_win.py - Genera .exe para Windows desde Linux
Sin Docker - Usa Wine directamente
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_wine():
    """Verifica que Wine esté instalado"""
    print("🔍 Verificando Wine...")
    try:
        result = subprocess.run(["wine", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Wine instalado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Wine no funciona correctamente")
            return False
    except FileNotFoundError:
        print("❌ Wine no está instalado")
        print("\nInstalar con:")
        print("  sudo dnf install wine wine-core wine-desktop")
        return False

def install_wine_python():
    """Instala Python para Windows en Wine"""
    print("\n🐍 Instalando Python para Windows en Wine...")
    
    # Descargar Python
    python_url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    python_exe = Path.home() / "python_installer.exe"
    
    if not python_exe.exists():
        print(f"  Descargando {python_url}...")
        subprocess.run(["wget", "-q", "-O", str(python_exe), python_url])
    
    # Instalar
    print("  Instalando (esto puede tardar 2-3 minutos)...")
    cmd = [
        "wine", str(python_exe),
        "/quiet",
        "InstallAllUsers=1",
        "PrependPath=1",
        "Shortcuts=0",
        "Include_test=0"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ Python instalado en Wine")
        return True
    else:
        print(f"  ❌ Error: {result.stderr[:200]}")
        return False

def install_dependencies():
    """Instala PyInstaller y dependencias en Wine Python"""
    print("\n📦 Instalando dependencias en Wine Python...")
    
    packages = [
        "pyinstaller==6.17.0",
        "customtkinter==5.2.2",
        "pandas==2.3.3",
        "openpyxl==3.1.5",
        "Pillow==12.0.0"
    ]
    
    for package in packages:
        print(f"  Instalando {package}...")
        cmd = ["wine", "pip", "install", package]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"    ✅ {package.split('==')[0]}")
        else:
            print(f"    ⚠️  Error con {package}")
            # Intentar con python -m pip
            cmd = ["wine", "python", "-m", "pip", "install", package]
            subprocess.run(cmd, capture_output=True)

def fix_unicode_files():
    """Corrige caracteres Unicode en archivos fuente"""
    print("\n🔧 Corrigiendo caracteres Unicode...")
    
    files_to_fix = ["run.py", "src/database.py"]
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Reemplazar emojis por texto
            content = content.replace('✅', '[OK]')
            content = content.replace('❌', '[ERROR]')
            content = content.replace('✓', '[OK]')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ {filepath}")

def build_exe():
    """Genera el .exe con PyInstaller"""
    print("\n🔨 Generando .exe con PyInstaller...")
    
    # Comando PyInstaller optimizado
    cmd = [
        "wine", "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", "BodegaApp",
        "--distpath", "dist_windows",
        "--workpath", "build_windows",
        
        # Añadir datos
        "--add-data", "config;config",
        "--add-data", "views;views",
        "--add-data", "models;models",
        "--add-data", "assets;assets",
        "--add-data", "data;data",
        
        # Imports ocultos
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "pandas",
        "--hidden-import", "openpyxl",
        
        # Opciones
        "--clean",
        "--noconfirm",
        
        # Archivo principal
        "run.py"
    ]
    
    print(f"  Comando: {' '.join(cmd[:5])}...")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Mostrar output
    if result.stdout:
        for line in result.stdout.strip().split('\n')[-20:]:
            if line.strip():
                print(f"    {line}")
    
    if result.returncode == 0:
        print("\n  ✅ PyInstaller terminó exitosamente")
        return True
    else:
        print(f"\n  ❌ Error en PyInstaller:")
        if result.stderr:
            for line in result.stderr.strip().split('\n')[-10:]:
                if 'error' in line.lower() or 'fail' in line.lower():
                    print(f"    {line}")
        return False

def verify_exe():
    """Verifica que el .exe se creó correctamente"""
    print("\n🔍 Verificando .exe...")
    
    exe_path = Path("dist_windows") / "BodegaApp.exe"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ .EXE CREADO: {exe_path}")
        print(f"  📦 Tamaño: {size_mb:.1f} MB")
        
        # Verificar tipo
        result = subprocess.run(["file", str(exe_path)], 
                              capture_output=True, text=True)
        
        if "PE32" in result.stdout or "Windows" in result.stdout:
            print("  🎯 ¡Es un .exe REAL para Windows!")
        else:
            print(f"  ⚠️  Tipo: {result.stdout}")
        
        return True
    else:
        print("  ❌ No se encontró el .exe")
        return False

def create_portable_package():
    """Crea un paquete portable con todo lo necesario"""
    print("\n📁 Creando paquete portable...")
    
    portable_dir = Path("BodegaApp_Portable_Windows")
    
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # Copiar .exe
    exe_src = Path("dist_windows") / "BodegaApp.exe"
    exe_dst = portable_dir / "BodegaApp.exe"
    shutil.copy2(exe_src, exe_dst)
    
    # Copiar carpetas necesarias
    folders = ["config", "views", "models", "assets"]
    for folder in folders:
        src = Path(folder)
        dst = portable_dir / folder
        if src.exists():
            shutil.copytree(src, dst)
            print(f"  ✅ {folder}/")
    
    # Crear estructura de datos
    (portable_dir / "data").mkdir()
    (portable_dir / "data" / "exports").mkdir()
    (portable_dir / "data" / "backups").mkdir()
    
    # Crear README
    readme = portable_dir / "LEEME.txt"
    readme.write_text("""BODEGA APP - Versión Windows
==============================

Para ejecutar:
1. Asegúrate de tener todas las carpetas en el mismo directorio:
   - BodegaApp.exe
   - config/
   - views/
   - models/
   - assets/
   - data/

2. Ejecuta BodegaApp.exe

Los datos se guardarán en la carpeta data/
""")
    
    print(f"  📦 Paquete creado: {portable_dir}")
    return portable_dir

def main():
    print("="*60)
    print("  CONSTRUCTOR .EXE WINDOWS (Sin Docker)")
    print("="*60)
    
    # Paso 1: Verificar Wine
    if not check_wine():
        sys.exit(1)
    
    # Paso 2: Corregir Unicode
    fix_unicode_files()
    
    # Paso 3: Instalar Python en Wine
    if not install_wine_python():
        print("\n⚠️  Intentando continuar sin reinstalar Python...")
    
    # Paso 4: Instalar dependencias
    install_dependencies()
    
    # Paso 5: Generar .exe
    if not build_exe():
        print("\n❌ Falló la generación del .exe")
        sys.exit(1)
    
    # Paso 6: Verificar
    if verify_exe():
        # Paso 7: Crear paquete portable
        portable_dir = create_portable_package()
        
        print("\n" + "="*60)
        print("  ✅ ¡CONSTRUCCIÓN COMPLETADA!")
        print("="*60)
        print(f"\n📂 Paquete portable: {portable_dir}")
        print("\n🚀 Para probar:")
        print(f"  wine {portable_dir}/BodegaApp.exe")
        print("\n📦 Para distribuir:")
        print(f"  tar -czf BodegaApp_Windows.tar.gz {portable_dir}/")
        print(f"  zip -r BodegaApp_Windows.zip {portable_dir}/")
    else:
        print("\n❌ La construcción falló")

if __name__ == "__main__":
    main()
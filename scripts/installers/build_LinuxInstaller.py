#!/usr/bin/env python3
"""
build_final.py - Constructor de ejecutable con verificación CORREGIDA
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """Verificación CORREGIDA - maneja correctamente PyInstaller"""
    print("🔍 Verificando dependencias...")
    
    all_ok = True
    
    # Verificar PyInstaller (puede ser importado como 'PyInstaller' o 'pyinstaller')
    print("  Verificando PyInstaller...")
    pyinstaller_ok = False
    
    # Intentar varias formas de importar
    try:
        import PyInstaller
        pyinstaller_ok = True
    except ImportError:
        try:
            import PyInstaller
            pyinstaller_ok = True
        except ImportError:
            pass
    
    if pyinstaller_ok:
        print("  ✅ PyInstaller instalado")
    else:
        print("  ❌ PyInstaller NO instalado")
        all_ok = False
    
    # Verificar Pillow (se importa como PIL)
    print("  Verificando Pillow...")
    try:
        import PIL
        print("  ✅ Pillow instalado")
    except ImportError:
        print("  ❌ Pillow NO instalado")
        all_ok = False
    
    if not all_ok:
        print(f"\n⚠️  Faltan dependencias.")
        print("Asegúrate de ejecutar estos comandos primero:")
        print("  pip install pyinstaller pillow")
        print("\nSi ya están instalados, prueba:")
        print("  python -c 'import PyInstaller; print(\"PyInstaller OK\")'")
        print("  python -c 'import PIL; print(\"Pillow OK\")'")
        return False
    
    return True

def clean_previous_builds():
    """Limpia builds y archivos temporales anteriores"""
    print("\n🧹 Limpiando builds anteriores...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  ✓ Eliminado: {dir_name}/")
            except Exception as e:
                print(f"  ⚠️  Error eliminando {dir_name}: {e}")
    
    # Eliminar archivos .spec
    for spec_file in Path('.').glob('*.spec'):
        try:
            spec_file.unlink()
            print(f"  ✓ Eliminado: {spec_file}")
        except Exception as e:
            print(f"  ⚠️  Error eliminando {spec_file}: {e}")

def create_icon():
    """Crea un icono simple para la aplicación"""
    icon_path = Path('assets/icons/app_icon.ico')
    
    if icon_path.exists():
        print(f"\n🎨 Icono ya existe: {icon_path}")
        return True
    
    print("\n🎨 Creando icono para la aplicación...")
    
    try:
        from PIL import Image, ImageDraw
        
        # Crear imagen 256x256
        img = Image.new('RGBA', (256, 256), (46, 134, 193, 255))  # #2E86C1
        
        draw = ImageDraw.Draw(img)
        
        # Dibujar círculo
        draw.ellipse([30, 30, 226, 226], outline='white', width=15)
        
        # Dibujar letra B
        try:
            # Intentar usar fuente por defecto
            from PIL import ImageFont
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 120)
            except:
                font = ImageFont.load_default(size=120)
        except:
            font = None
        
        # Dibujar texto
        if font:
            draw.text((128, 128), "B", fill='white', font=font, anchor='mm')
        else:
            # Texto simple si no hay fuente
            draw.text((100, 100), "B", fill='white')
        
        # Crear directorio si no existe
        icon_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar como .ico
        img.save(icon_path, format='ICO')
        print(f"  ✅ Icono creado: {icon_path}")
        return True
        
    except ImportError:
        print("  ⚠️  Pillow no disponible. Saltando creación de icono.")
        return False
    except Exception as e:
        print(f"  ⚠️  Error creando icono: {e}")
        return False

def build_executable():
    """Construye el ejecutable usando PyInstaller"""
    print("\n🚀 Construyendo ejecutable con PyInstaller...")
    
    # Configuración básica
    app_name = "BodegaApp"
    
    # Argumentos para PyInstaller
    args = [
        'run.py',                    # Archivo principal
        f'--name={app_name}',        # Nombre del ejecutable
        '--windowed',                # Sin consola (modo ventana)
        '--onefile',                 # Un solo archivo .exe
        '--clean',                   # Limpiar cache
        '--noconfirm',               # No pedir confirmación
        
        # Imports ocultos necesarios
        '--hidden-import=customtkinter',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=tkinter',
        '--hidden-import=sqlite3',
        
        # Datos a incluir
        '--add-data=config:config',
        '--add-data=data:data',
        '--add-data=assets:assets',
    ]
    
    # Añadir icono si existe
    icon_path = Path('assets/icons/app_icon.ico')
    if icon_path.exists() and icon_path.stat().st_size > 0:
        args.append(f'--icon={icon_path}')
        print(f"  ✓ Usando icono: {icon_path}")
    
    print(f"\n📋 Comando PyInstaller a ejecutar:")
    print(f"pyinstaller {' '.join(args)}")
    print("\n⏳ Esto puede tomar varios minutos...")
    
    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run(args)
        
        # Verificar resultado
        exe_path = Path('dist') / app_name
        if sys.platform == 'win32':
            exe_path = Path('dist') / f'{app_name}.exe'
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ ¡ÉXITO! Ejecutable creado:")
            print(f"   📍 Ubicación: {exe_path}")
            print(f"   📏 Tamaño: {size_mb:.1f} MB")
            
            # Mostrar información adicional
            print(f"   📁 Incluye: config/, data/, assets/")
            return True
        else:
            print(f"\n❌ Error: No se encontró el ejecutable en {exe_path}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error durante la construcción:")
        print(f"   {e}")
        print("\n💡 Solución de problemas:")
        print("   1. Asegúrate de que todas las dependencias están instaladas")
        print("   2. Verifica que run.py funciona correctamente")
        print("   3. Intenta ejecutar PyInstaller manualmente:")
        print(f"      pyinstaller {' '.join(args)}")
        return False

def create_windows_files():
    """Crea archivos auxiliares para Windows"""
    print("\n📝 Creando archivos para distribución Windows...")
    
    # Script de instalación simple
    install_script = '''@echo off
echo ========================================
echo   INSTALACIÓN BODEGA APP - WINDOWS
echo ========================================
echo.

echo 1. Creando directorio de instalación...
mkdir "C:\\BodegaApp" 2>nul

echo 2. Copiando ejecutable...
copy "BodegaApp.exe" "C:\\BodegaApp\\" >nul

echo 3. Creando acceso directo en escritorio...
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\\shortcut.vbs"
echo Set shortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") ^& "\\Bodega App.lnk") >> "%TEMP%\\shortcut.vbs"
echo shortcut.TargetPath = "C:\\BodegaApp\\BodegaApp.exe" >> "%TEMP%\\shortcut.vbs"
echo shortcut.WorkingDirectory = "C:\\BodegaApp" >> "%TEMP%\\shortcut.vbs"
echo shortcut.Save >> "%TEMP%\\shortcut.vbs"
cscript //nologo "%TEMP%\\shortcut.vbs" >nul
del "%TEMP%\\shortcut.vbs" 2>nul

echo.
echo ========================================
echo   ✅ INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo La aplicación ha sido instalada en:
echo   C:\\BodegaApp\\
echo.
echo Se creó un acceso directo en el escritorio.
echo.
echo Presione cualquier tecla para salir...
pause >nul
'''
    
    # Script de desinstalación
    uninstall_script = '''@echo off
echo ========================================
echo   DESINSTALACIÓN BODEGA APP
echo ========================================
echo.

set /p CONFIRM="¿Seguro que desea desinstalar? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Desinstalación cancelada.
    pause
    exit /b 0
)

echo.
echo Eliminando archivos...
rmdir /s /q "C:\\BodegaApp" 2>nul
del "%USERPROFILE%\\Desktop\\Bodega App.lnk" 2>nul

echo.
echo ========================================
echo   ✅ DESINSTALACIÓN COMPLETADA
echo ========================================
echo.
echo Presione cualquier tecla para salir...
pause >nul
'''
    
    # README para Windows
    readme_content = """# BODEGA APP - PARA WINDOWS

## 🚀 INSTRUCCIONES DE INSTALACIÓN

### Opción 1: Instalación automática (recomendada)
1. Ejecute `install_windows.bat`
2. Siga las instrucciones en pantalla
3. La aplicación se instalará en `C:\\BodegaApp`

### Opción 2: Uso portátil
1. Copie `BodegaApp.exe` a cualquier carpeta
2. Ejecútelo directamente (no requiere instalación)

## 📋 REQUISITOS DEL SISTEMA

- Windows 10 o superior
- 4 GB de RAM
- 200 MB de espacio libre
- Resolución 1366x768 o superior

## 🛠️ SOLUCIÓN DE PROBLEMAS

### "Falta MSVCP140.dll"
Instale Microsoft Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### "La aplicación no inicia"
1. Asegúrese de tener permisos de administrador si es necesario
2. Verifique que el antivirus no esté bloqueando la aplicación

### "Error al guardar datos"
1. Ejecute la aplicación como administrador
2. Asegúrese de tener permisos de escritura en la carpeta de instalación

## 📞 SOPORTE

Para reportar problemas:
1. Revise los logs en la carpeta de la aplicación
2. Contacte al desarrollador

## ⚖️ LICENCIA

Software gratuito para uso personal y comercial.
"""

    # Guardar archivos
    files_to_create = {
        'install_windows.bat': install_script,
        'uninstall_windows.bat': uninstall_script,
        'README_WINDOWS.txt': readme_content,
    }
    
    for filename, content in files_to_create.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Creado: {filename}")

def main():
    """Función principal"""
    print("=" * 60)
    print("CONSTRUCTOR DE EJECUTABLE - BODEGA APP")
    print("Versión definitiva con verificación corregida")
    print("=" * 60)
    
    # Paso 1: Verificar dependencias (CORREGIDO)
    if not check_dependencies():
        print("\n❌ No se puede continuar sin las dependencias.")
        print("   Ejecuta: pip install pyinstaller pillow")
        sys.exit(1)
    
    # Paso 2: Limpiar builds anteriores
    clean_previous_builds()
    
    # Paso 3: Crear icono
    create_icon()
    
    # Paso 4: Construir ejecutable
    if not build_executable():
        print("\n❌ La construcción del ejecutable falló.")
        sys.exit(1)
    
    # Paso 5: Crear archivos para Windows
    create_windows_files()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("🎉 ¡CONSTRUCCIÓN COMPLETADA CON ÉXITO!")
    print("=" * 60)
    print("\n📁 ARCHIVOS GENERADOS:")
    print("  📦 dist/BodegaApp       - Ejecutable principal")
    print("  📜 install_windows.bat  - Instalador para Windows")
    print("  📜 uninstall_windows.bat - Desinstalador")
    print("  📄 README_WINDOWS.txt   - Instrucciones")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("  1. Copia la carpeta 'dist/' completa a una PC con Windows")
    print("  2. Ejecuta 'install_windows.bat' para instalar")
    print("  3. O ejecuta 'BodegaApp.exe' directamente para uso portátil")
    
    print("\n⚠️  NOTA IMPORTANTE:")
    print("  Este ejecutable fue construido en Linux.")
    print("  Para máxima compatibilidad con Windows,")
    print("  considera construir en una máquina Windows.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
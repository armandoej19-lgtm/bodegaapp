#!/usr/bin/env python3
"""
Build Windows .exe with installer for Program Files
Located in: scripts/installers/build.py
"""
import subprocess
import os
import sys
import shutil
import zipfile
from pathlib import Path

# Get the project root directory (go up two levels from this script)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
print(f"📁 Directorio del proyecto: {PROJECT_ROOT}")

def create_nsis_installer():
    """Create NSIS installer script"""
    nsis_script = """# NSIS Installer Script for BodegaApp
!include "MUI2.nsh"

# Basic configuration
Name "Bodega Register App"
OutFile "dist\\BodegaApp_Setup.exe"
InstallDir "$PROGRAMFILES32\\BodegaApp"
RequestExecutionLevel admin

# Interface configuration
!define MUI_ICON "assets\\icons\\app_icon.ico"
!define MUI_UNICON "assets\\icons\\app_icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\\installer_welcome.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "assets\\installer_welcome.bmp"

# Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

# Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Spanish"

Section "Main Application"
    SetOutPath "$INSTDIR"
    
    # Copy main executable
    File "dist\\BodegaApp.exe"
    
    # Copy data folders
    File /r "assets"
    File /r "config"
    File /r "views"
    
    # Create data directory
    CreateDirectory "$LOCALAPPDATA\\BodegaApp\\data"
    CreateDirectory "$LOCALAPPDATA\\BodegaApp\\logs"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    # Create shortcuts
    CreateDirectory "$SMPROGRAMS\\BodegaApp"
    CreateShortcut "$SMPROGRAMS\\BodegaApp\\BodegaApp.lnk" "$INSTDIR\\BodegaApp.exe"
    CreateShortcut "$SMPROGRAMS\\BodegaApp\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    CreateShortcut "$DESKTOP\\BodegaApp.lnk" "$INSTDIR\\BodegaApp.exe"
    
    # Write registry for uninstall
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BodegaApp" \
        "DisplayName" "Bodega Register App"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BodegaApp" \
        "UninstallString" '"$INSTDIR\\Uninstall.exe"'
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BodegaApp" \
        "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BodegaApp" \
        "Publisher" "Tu Empresa"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BodegaApp" \
        "DisplayVersion" "1.0.0"
SectionEnd

Section "Uninstall"
    # Remove shortcuts
    Delete "$SMPROGRAMS\\BodegaApp\\BodegaApp.lnk"
    Delete "$SMPROGRAMS\\BodegaApp\\Uninstall.lnk"
    Delete "$DESKTOP\\BodegaApp.lnk"
    RMDir "$SMPROGRAMS\\BodegaApp"
    
    # Remove application files
    RMDir /r "$INSTDIR"
    
    # Remove data (optional - ask user?)
    # RMDir /r "$LOCALAPPDATA\\BodegaApp"
    
    # Remove registry
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\BodegaApp"
SectionEnd
"""
    
    # Save NSIS script in project root
    nsis_path = PROJECT_ROOT / "installer.nsi"
    with open(nsis_path, "w", encoding="utf-8") as f:
        f.write(nsis_script)
    
    print("📝 Script NSIS creado: installer.nsi")
    
    # Create installer bitmap (optional)
    bmp_path = PROJECT_ROOT / "assets" / "installer_welcome.bmp"
    if not bmp_path.exists():
        print("⚠️  Crea assets/installer_welcome.bmp (164x314) para mejor apariencia")
    
    return str(nsis_path)

def build_for_windows_with_installer():
    print("="*60)
    print("🏗️  CONSTRUYENDO .EXE E INSTALADOR PARA WINDOWS")
    print("="*60)
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    print(f"📂 Trabajando en: {os.getcwd()}")
    
    # 1. First build the .exe
    print("\n1️⃣  Construyendo ejecutable principal...")
    cmd_build = [
        "wine", "python", "-m", "PyInstaller",
        "run.py",
        "--name=BodegaApp",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--hidden-import=pandas",
        "--hidden-import=customtkinter", 
        "--hidden-import=openpyxl",
        "--hidden-import=tkinter",
        "--hidden-import=PIL",
        "--add-data=assets:assets",
        "--add-data=views:views",
        "--add-data=config:config"
    ]
    
    icon_path = PROJECT_ROOT / "assets" / "icons" / "app_icon.ico"
    if icon_path.exists():
        cmd_build.append(f"--icon={icon_path}")
        print(f"🎨 Usando ícono: {icon_path}")
    else:
        print("⚠️  No se encontró ícono, creando uno básico...")
        create_basic_icon()
        if icon_path.exists():
            cmd_build.append(f"--icon={icon_path}")
    
    print("🔨 Ejecutando PyInstaller...")
    result = subprocess.run(cmd_build, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Error construyendo .exe:")
        print(result.stderr[:500])  # Show first 500 chars
        return False
    
    exe_path = PROJECT_ROOT / "dist" / "windows_installer" / "BodegaApp.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Ejecutable creado: {exe_path} ({size_mb:.2f} MB)")
    else:
        print("❌ Ejecutable no encontrado en dist/")
        return False
    
    # 2. Create NSIS installer script
    print("\n2️⃣  Creando script de instalación...")
    nsis_script = create_nsis_installer()
    
    # 3. Compile installer (need NSIS installed on Linux)
    print("\n3️⃣  Compilando instalador...")
    
    # Check if NSIS is available
    if shutil.which("makensis"):
        cmd_nsis = ["makensis", nsis_script]
        result = subprocess.run(cmd_nsis, capture_output=True, text=True)
        
        if result.returncode == 0:
            setup_path = PROJECT_ROOT / "dist" / "windows_installer" / "BodegaApp_Setup.exe"
            if setup_path.exists():
                size_mb = setup_path.stat().st_size / (1024 * 1024)
                print(f"✅ Instalador creado: {setup_path} ({size_mb:.2f} MB)")
                print("\n📋 Instalador incluye:")
                print("   ✓ Instalación en Program Files (x86)")
                print("   ✓ Acceso directo en Menú Inicio y Escritorio")
                print("   ✓ Desinstalador completo")
                print("   ✓ Entradas en Panel de Control")
            else:
                print("⚠️  Instalador no creado, verificando NSIS...")
                create_simple_installer()
        else:
            print("⚠️  NSIS no pudo compilar:")
            print(result.stderr[:200])
            create_simple_installer()
    else:
        print("⚠️  NSIS no instalado, creando instalador simple...")
        print("   Para NSIS: sudo dnf install nsis")
        create_simple_installer()
    
    # 4. Create portable version too
    create_portable_version()
    
    print("\n" + "="*60)
    print("🎉 ¡CONSTRUCCIÓN COMPLETADA!")
    print("="*60)
    print("\n📁 ARCHIVOS GENERADOS:")
    print(f"   {PROJECT_ROOT}/dist/windows_installer/BodegaApp.exe           - Versión portable")
    print(f"   {PROJECT_ROOT}/dist/windows_installer/BodegaApp_Setup.exe     - Instalador (recomendado)")
    print(f"   {PROJECT_ROOT}/dist/windows_installer/BodegaApp_Portable.zip  - Paquete portable")
    print(f"   {PROJECT_ROOT}/dist/windows_installer/install_windows.bat     - Instalador simple")
    print(f"   {PROJECT_ROOT}/dist/windows_installer/uninstall_windows.bat   - Desinstalador simple")
    print("\n🚀 Para usuarios:")
    print("   1. Ejecuta BodegaApp_Setup.exe para instalación completa")
    print("   2. Se instalará en: C:\\Program Files (x86)\\BodegaApp")
    print("="*60)
    
    return True

def create_basic_icon():
    """Create a basic icon if none exists"""
    icon_dir = PROJECT_ROOT / "assets" / "icons"
    icon_dir.mkdir(parents=True, exist_ok=True)
    icon_path = icon_dir / "app_icon.ico"
    
    # Create a simple icon using ImageMagick if available
    if shutil.which("convert"):
        try:
            cmd = [
                "convert", "-size", "256x256", "xc:#4A90E2",
                "-fill", "white", "-draw", "circle 128,128 128,64",
                "-define", "icon:auto-resize=256,128,64,48,32,16",
                str(icon_path)
            ]
            subprocess.run(cmd, capture_output=True)
            print("✅ Ícono básico creado")
        except:
            # Create empty icon file as placeholder
            with open(icon_path, "wb") as f:
                f.write(b"")  # Empty file
            print("⚠️  Ícono placeholder creado (vacío)")
    else:
        print("⚠️  ImageMagick no instalado para crear ícono")
        print("   sudo dnf install ImageMagick")

def create_simple_installer():
    """Create a simple batch installer"""
    dist_dir = PROJECT_ROOT / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    batch_content = """@echo off
REM Simple Installer for BodegaApp
echo ========================================
echo    BODEGA APP - INSTALADOR
echo ========================================
echo.

REM Check for administrator privileges
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Necesitas ejecutar como Administrador
    echo Haz clic derecho -> Ejecutar como administrador
    pause
    exit /b 1
)

echo Instalando en: C:\\Program Files (x86)\\BodegaApp

REM Create installation directory
mkdir "C:\\Program Files (x86)\\BodegaApp" 2>nul
if errorlevel 1 (
    echo Error al crear directorio
    pause
    exit /b 1
)

REM Copy files
echo Copiando archivos...
copy "%~dp0BodegaApp.exe" "C:\\Program Files (x86)\\BodegaApp\\" >nul
xcopy "%~dp0assets" "C:\\Program Files (x86)\\BodegaApp\\assets\\" /E /I /Y >nul
xcopy "%~dp0config" "C:\\Program Files (x86)\\BodegaApp\\config\\" /E /I /Y >nul
xcopy "%~dp0views" "C:\\Program Files (x86)\\BodegaApp\\views\\" /E /I /Y >nul

REM Create data directory
mkdir "%LOCALAPPDATA%\\BodegaApp\\data" 2>nul
mkdir "%LOCALAPPDATA%\\BodegaApp\\logs" 2>nul

REM Create desktop shortcut
echo Creando accesos directos...
set SCRIPT="%TEMP%\\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = "%USERPROFILE%\\Desktop\\BodegaApp.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "C:\\Program Files (x86)\\BodegaApp\\BodegaApp.exe" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

REM Create Start Menu shortcut
mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\BodegaApp" 2>nul
set SCRIPT="%TEMP%\\create_startmenu.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\BodegaApp\\BodegaApp.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "C:\\Program Files (x86)\\BodegaApp\\BodegaApp.exe" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo.
echo ========================================
echo    INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo La aplicación se ha instalado en:
echo   C:\\Program Files (x86)\\BodegaApp
echo.
echo Accesos directos creados en:
echo   - Escritorio
echo   - Menu Inicio -> BodegaApp
echo.
echo Para desinstalar, borra la carpeta:
echo   C:\\Program Files (x86)\\BodegaApp
echo.
pause
"""
    
    installer_path = dist_dir / "install_windows.bat"
    with open(installer_path, "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    # Create uninstaller
    uninstall_content = """@echo off
echo ========================================
echo    BODEGA APP - DESINSTALADOR
echo ========================================
echo.
echo Esto eliminará BodegaApp de tu sistema.
echo.
set /p confirm="¿Continuar? (S/N): "
if /i "%confirm%" NEQ "S" (
    echo Desinstalación cancelada.
    pause
    exit /b 0
)

echo Eliminando archivos...
rmdir /S /Q "C:\\Program Files (x86)\\BodegaApp" 2>nul
del "%USERPROFILE%\\Desktop\\BodegaApp.lnk" 2>nul
rmdir /S /Q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\BodegaApp" 2>nul

echo.
echo ========================================
echo    DESINSTALACIÓN COMPLETADA
echo ========================================
echo.
pause
"""
    
    uninstaller_path = dist_dir / "uninstall_windows.bat"
    with open(uninstaller_path, "w", encoding="utf-8") as f:
        f.write(uninstall_content)
    
    print("✅ Instalador simple creado: dist/install_windows.bat")

def create_portable_version():
    """Create portable zip package"""
    print("\n4️⃣  Creando versión portable...")
    
    dist_dir = PROJECT_ROOT / "dist" / "windows_installer"
    portable_dir = dist_dir / "portable" / "BodegaApp"
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    files_to_copy = [
        (dist_dir / "BodegaApp.exe", portable_dir / "BodegaApp.exe"),
        (PROJECT_ROOT / "assets", portable_dir / "assets"),
        (PROJECT_ROOT / "config", portable_dir / "config"),
        (PROJECT_ROOT / "views", portable_dir / "views")
    ]
    
    for src, dst in files_to_copy:
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        else:
            print(f"⚠️  No encontrado: {src}")
    
    # Create portable config file
    portable_config = """[Portable]
data_dir = ./data
logs_dir = ./logs
"""
    
    config_path = portable_dir / "portable.ini"
    with open(config_path, "w") as f:
        f.write(portable_config)
    
    # Create README
    readme_content = """BODEGA APP - VERSIÓN PORTABLE
================================

Esta es la versión portable de BodegaApp.

PARA USAR:
1. Extrae esta carpeta en cualquier lugar
2. Ejecuta BodegaApp.exe
3. Los datos se guardarán en la subcarpeta ./data

CARACTERÍSTICAS:
- No requiere instalación
- No escribe en el registro de Windows
- Los datos viajan con la aplicación
- Ideal para USB o uso temporal

NOTA: Para instalación permanente, usa el instalador.
"""
    
    readme_path = portable_dir / "README_PORTABLE.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create zip
    zip_path = dist_dir / "BodegaApp_Portable.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir / "portable")
                zipf.write(file_path, arcname)
    
    # Cleanup
    shutil.rmtree(dist_dir / "portable")
    
    if zip_path.exists():
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"✅ Versión portable: {zip_path} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    # Change to project root directory
    os.chdir(PROJECT_ROOT)
    print(f"📍 Directorio de trabajo: {PROJECT_ROOT}")
    
    # Check if wine is available
    if not shutil.which("wine"):
        print("❌ Wine no está instalado. Instálalo primero:")
        print("   sudo dnf install wine")
        sys.exit(1)
    
    build_for_windows_with_installer()
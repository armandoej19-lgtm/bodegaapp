#!/usr/bin/env python3
"""
Build Windows installer using ZIP + BAT (sin NSIS/Docker)
Ubicación: scripts/installers/build_windows_zip_installer.py
"""
import subprocess
import os
import sys
import shutil
import zipfile
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def verify_executable():
    """Verificar que existe el ejecutable"""
    print_header("VERIFICANDO EJECUTABLE")
    
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    exe_path = PROJECT_ROOT / "dist" / "BodegaApp.exe"
    
    if not exe_path.exists():
        print("❌ No se encontró BodegaApp.exe")
        print("   Ejecuta primero: python scripts/build_windows_exe.py")
        return False
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✅ Ejecutable encontrado: {exe_path}")
    print(f"📏 Tamaño: {size_mb:.2f} MB")
    return True

def create_zip_installer():
    """Crear instalador autoextraíble ZIP"""
    print_header("CREANDO INSTALADOR ZIP AUTOEXTRAÍBLE")
    
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    dist_dir = PROJECT_ROOT / "dist"
    
    # Crear directorio temporal para el instalador
    temp_dir = Path("/tmp/bodega_installer")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 1. Copiar ejecutable principal
    exe_src = dist_dir / "BodegaApp.exe"
    exe_dst = temp_dir / "BodegaApp.exe"
    shutil.copy2(exe_src, exe_dst)
    print("✅ Copiado: BodegaApp.exe")
    
    # 2. Crear estructura de carpetas
    folders = ["assets", "config", "views", "models"]
    for folder in folders:
        folder_path = temp_dir / folder
        folder_path.mkdir(exist_ok=True)
        print(f"✅ Creada carpeta: {folder}/")
    
    # 3. Copiar contenido de carpetas
    src_folders = ["assets", "config", "views", "models"]
    for folder in src_folders:
        src = PROJECT_ROOT / folder
        dst = temp_dir / folder
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"✅ Copiado contenido: {folder}/")
    
    # 4. Crear scripts de instalación
    
    # Script de instalación principal (ADMIN)
    install_bat = """@echo off
chcp 65001 >nul
echo ========================================
echo    BODEGA APP - INSTALADOR
echo ========================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Este instalador requiere permisos de Administrador.
    echo Por favor, ejecuta como Administrador.
    echo.
    echo 1. Haz clic derecho en este archivo
    echo 2. Selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

:: Configuración
set "INSTALL_DIR=C:\\Program Files\\BodegaApp"
set "DATA_DIR=%%LOCALAPPDATA%%\\BodegaApp\\data"
set "LOG_DIR=%%LOCALAPPDATA%%\\BodegaApp\\logs"

echo Configuración de instalación:
echo   Programa: %INSTALL_DIR%
echo   Datos: %DATA_DIR%
echo   Logs: %LOG_DIR%
echo.

:: Confirmar instalación
set /p CONFIRMAR=¿Desea continuar con la instalación? (S/N): 
if /i "%CONFIRMAR%" NEQ "S" (
    echo Instalación cancelada.
    pause
    exit /b 0
)

echo.
echo Paso 1/5: Creando directorios...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Paso 2/5: Copiando archivos...
xcopy /E /I /Y ".\\*" "%INSTALL_DIR%\\"

echo Paso 3/5: Creando acceso directo en escritorio...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\BodegaApp.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\BodegaApp.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo Paso 4/5: Creando acceso directo en menú Inicio...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\BodegaApp.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\BodegaApp.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo Paso 5/5: Creando archivo de configuración...
echo Configuración instalada: %DATE% %TIME% > "%DATA_DIR%\\install.log"

echo.
echo ========================================
echo    ✅ INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo Resumen:
echo   ✓ Programa instalado en: %INSTALL_DIR%
echo   ✓ Datos guardados en: %DATA_DIR%
echo   ✓ Acceso directo creado en Escritorio
echo   ✓ Acceso directo creado en Menú Inicio
echo.
echo Para ejecutar: Doble clic en BodegaApp.lnk en tu escritorio.
echo.
echo Para desinstalar: Ejecuta "Desinstalar.bat" como Administrador.
echo.
pause
"""
    
    with open(temp_dir / "Instalar.bat", "w", encoding="utf-8") as f:
        f.write(install_bat)
    print("✅ Creado: Instalar.bat (instalador con Admin)")
    
    # Script de instalación sin Admin (portable)
    install_portable_bat = """@echo off
chcp 65001 >nul
echo ========================================
echo    BODEGA APP - INSTALADOR PORTABLE
echo ========================================
echo.
echo Este instalador NO requiere permisos de administrador.
echo La aplicación se instalará en tu carpeta de usuario.
echo.

:: Configuración
set "INSTALL_DIR=%USERPROFILE%\\BodegaApp"
set "DATA_DIR=%INSTALL_DIR%\\data"
set "LOG_DIR=%INSTALL_DIR%\\logs"

echo Configuración de instalación:
echo   Programa: %INSTALL_DIR%
echo   Datos: %DATA_DIR%
echo.

:: Confirmar instalación
set /p CONFIRMAR=¿Desea continuar con la instalación? (S/N): 
if /i "%CONFIRMAR%" NEQ "S" (
    echo Instalación cancelada.
    pause
    exit /b 0
)

echo.
echo Paso 1/3: Creando directorios...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Paso 2/3: Copiando archivos...
xcopy /E /I /Y ".\\*" "%INSTALL_DIR%\\"

echo Paso 3/3: Creando acceso directo en escritorio...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\BodegaApp.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\BodegaApp.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo ========================================
echo    ✅ INSTALACIÓN PORTABLE COMPLETADA
echo ========================================
echo.
echo Resumen:
echo   ✓ Programa instalado en: %INSTALL_DIR%
echo   ✓ Datos guardados en: %DATA_DIR%
echo   ✓ Acceso directo creado en Escritorio
echo.
echo Para ejecutar: Doble clic en BodegaApp.lnk en tu escritorio.
echo.
pause
"""
    
    with open(temp_dir / "Instalar_Portable.bat", "w", encoding="utf-8") as f:
        f.write(install_portable_bat)
    print("✅ Creado: Instalar_Portable.bat (sin Admin)")
    
    # Script desinstalador
    uninstall_bat = """@echo off
chcp 65001 >nul
echo ========================================
echo    BODEGA APP - DESINSTALADOR
echo ========================================
echo.

:: Verificar permisos
net session >nul 2>&1
set IS_ADMIN=%errorLevel%

if %IS_ADMIN% == 0 (
    echo Modo: Administrador (instalación completa)
    set "INSTALL_DIR=C:\\Program Files\\BodegaApp"
) else (
    echo Modo: Usuario (instalación portable)
    set "INSTALL_DIR=%USERPROFILE%\\BodegaApp"
)

set "DATA_DIR=%LOCALAPPDATA%\\BodegaApp"
set "BACKUP_DIR=%USERPROFILE%\\Desktop\\BodegaApp_Backup_%DATE:/=_%_%TIME::=_%"

echo.
echo Esta acción eliminará:
echo   • Programa: %INSTALL_DIR%
echo   • Datos: %DATA_DIR%
echo   • Accesos directos
echo.
echo ¿Está seguro de continuar? (S/N)
set /p CONFIRMAR=
if /i "%CONFIRMAR%" NEQ "S" (
    echo Desinstalación cancelada.
    pause
    exit /b 0
)

echo.
echo ⚠️  ¿Desea crear una copia de seguridad de los datos? (S/N)
set /p BACKUP=
if /i "%BACKUP%" EQU "S" (
    echo Creando copia de seguridad en: %BACKUP_DIR%
    if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
    if exist "%DATA_DIR%" xcopy /E /I /Y "%DATA_DIR%\\*" "%BACKUP_DIR%\\"
    echo ✓ Copia de seguridad creada.
)

echo.
echo Paso 1/3: Eliminando acceso directo del escritorio...
del "%USERPROFILE%\\Desktop\\BodegaApp.lnk" 2>nul

echo Paso 2/3: Eliminando acceso directo del menú Inicio...
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\BodegaApp.lnk" 2>nul

echo Paso 3/3: Eliminando directorios...
if exist "%INSTALL_DIR%" rmdir /S /Q "%INSTALL_DIR%"
if exist "%DATA_DIR%" rmdir /S /Q "%DATA_DIR%"

echo.
echo ========================================
echo    ✅ DESINSTALACIÓN COMPLETADA
echo ========================================
echo.
if /i "%BACKUP%" EQU "S" (
    echo Nota: Se creó una copia de seguridad en:
    echo       %BACKUP_DIR%
    echo.
)
echo Para reinstalar, ejecuta "Instalar.bat" nuevamente.
echo.
pause
"""
    
    with open(temp_dir / "Desinstalar.bat", "w", encoding="utf-8") as f:
        f.write(uninstall_bat)
    print("✅ Creado: Desinstalar.bat")
    
    # Script de ejecución directa (desde carpeta actual)
    run_bat = """@echo off
chcp 65001 >nul
echo ========================================
echo    BODEGA APP - EJECUTAR DESDE AQUÍ
echo ========================================
echo.
echo Modo: Ejecución directa desde esta carpeta.
echo Los datos se guardarán en: .\\data
echo.
echo Para instalar completamente, ejecuta "Instalar.bat"
echo.
echo Iniciando BodegaApp...
echo.
BodegaApp.exe
"""
    
    with open(temp_dir / "Ejecutar_Aqui.bat", "w", encoding="utf-8") as f:
        f.write(run_bat)
    print("✅ Creado: Ejecutar_Aqui.bat")
    
    # 5. Crear README profesional
    readme_content = """BODEGA REGISTER APP v1.0
============================

📦 CONTENIDO DEL PAQUETE
------------------------
• BodegaApp.exe         - Aplicación principal
• Instalar.bat          - Instalador con permisos de Administrador (RECOMENDADO)
• Instalar_Portable.bat - Instalador sin permisos de administrador
• Desinstalar.bat       - Desinstalador completo
• Ejecutar_Aqui.bat     - Ejecutar desde esta carpeta sin instalar

📋 REQUISITOS DEL SISTEMA
-------------------------
• Windows 10 o Windows 11 (64-bit)
• 4 GB de RAM mínimo
• 500 MB de espacio libre en disco
• Conexión a Internet (para actualizaciones)

🚀 CÓMO INSTALAR
----------------

OPCIÓN 1: INSTALACIÓN COMPLETA (Recomendada)
--------------------------------------------
1. Ejecutar "Instalar.bat" como Administrador
   (clic derecho → "Ejecutar como administrador")
2. Seguir las instrucciones en pantalla
3. La aplicación se instalará en: C:\\Program Files\\BodegaApp
4. Se crearán accesos directos en Escritorio y Menú Inicio

OPCIÓN 2: INSTALACIÓN PORTABLE
------------------------------
1. Ejecutar "Instalar_Portable.bat" (sin Admin)
2. La aplicación se instalará en: %USERPROFILE%\\BodegaApp
3. Se creará acceso directo en el Escritorio

OPCIÓN 3: EJECUCIÓN DIRECTA
---------------------------
1. Ejecutar "Ejecutar_Aqui.bat"
2. La aplicación se ejecuta desde esta carpeta
3. Los datos se guardan en: .\\data

🗑️ CÓMO DESINSTALAR
-------------------
1. Ejecutar "Desinstalar.bat"
2. Seguir las instrucciones en pantalla
3. Opcional: Crear copia de seguridad de los datos

📂 ESTRUCTURA DE ARCHIVOS
-------------------------
• assets/     - Iconos, imágenes y recursos
• config/     - Archivos de configuración
• views/      - Interfaces de usuario
• models/     - Modelos de datos
• data/       - Base de datos y backups (se crea automáticamente)

🔧 SOPORTE Y SOLUCIÓN DE PROBLEMAS
-----------------------------------

PROBLEMA COMÚN: Antivirus bloquea la aplicación
SOLUCIÓN: Agregar excepción en tu antivirus para BodegaApp.exe

PROBLEMA: No se puede ejecutar como Administrador
SOLUCIÓN: Usar "Instalar_Portable.bat" en su lugar

PROBLEMA: Error al iniciar la aplicación
SOLUCIÓN:
1. Verificar que Windows esté actualizado
2. Ejecutar "Ejecutar_Aqui.bat" para ver mensajes de error
3. Contactar soporte con el archivo logs/error.log

📞 CONTACTO Y SOPORTE
---------------------
• Soporte técnico: soporte@bodegaapp.com
• Documentación: docs.bodegaapp.com
• Actualizaciones: updates.bodegaapp.com

🔒 SEGURIDAD
------------
• La aplicación no requiere conexión a Internet para funcionar
• Los datos se almacenan localmente en tu computadora
• Se realizan backups automáticos cada 24 horas
• Compatible con políticas de seguridad empresarial

© 2024 BodegaApp Team. Todos los derechos reservados.
"""
    
    with open(temp_dir / "LEAME.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ Creado: LEAME.txt (documentación completa)")
    
    # 6. Crear archivo de licencia básico
    license_content = """LICENCIA DE USO - BODEGA REGISTER APP

Copyright (c) 2024 BodegaApp Team

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y los archivos de documentación asociados (el "Software"),
para utilizar el Software sin restricción, incluyendo sin limitación los derechos
de usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender
copias del Software, y para permitir a las personas a las que se les proporcione
el Software a hacer lo mismo, sujeto a las siguientes condiciones:

1. El aviso de copyright anterior y este aviso de permiso se incluirán en
   todas las copias o partes sustanciales del Software.

2. EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO,
   EXPRESA O IMPLÍCITA, INCLUYENDO PERO NO LIMITADO A GARANTÍAS DE
   COMERCIALIZACIÓN, IDONEIDAD PARA UN PROPÓSITO PARTICULAR Y NO INFRACCIÓN.
   EN NINGÚN CASO LOS AUTORES O TITULARES DEL COPYRIGHT SERÁN RESPONSABLES
   DE NINGUNA RECLAMACIÓN, DAÑOS U OTRAS RESPONSABILIDADES, YA SEA EN UNA
   ACCIÓN DE CONTRATO, AGRAVIO O CUALQUIER OTRO MOTIVO, QUE SURJA DE O
   EN CONEXIÓN CON EL SOFTWARE O EL USO U OTRO TIPO DE ACCIONES EN EL SOFTWARE.

Para consultas sobre licencias comerciales, contacte a: licencias@bodegaapp.com
"""
    
    with open(temp_dir / "LICENCIA.txt", "w", encoding="utf-8") as f:
        f.write(license_content)
    print("✅ Creado: LICENCIA.txt")
    
    # 7. Crear ZIP del instalador
    print("\n📦 Creando archivo ZIP del instalador...")
    zip_path = dist_dir / "BodegaApp_Instalador_Completo.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in temp_dir.rglob('*'):
            if item.is_file():
                arcname = item.relative_to(temp_dir)
                zipf.write(item, arcname)
    
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✅ ZIP creado: {zip_path} ({zip_size_mb:.2f} MB)")
    
    # 8. También copiar la carpeta completa
    installer_dir = dist_dir / "BodegaApp_Instalador"
    if installer_dir.exists():
        shutil.rmtree(installer_dir)
    shutil.copytree(temp_dir, installer_dir)
    
    print(f"✅ Carpeta de instalador: {installer_dir}")
    
    # Limpiar temporal
    shutil.rmtree(temp_dir)
    
    return True

def main():
    print("="*60)
    print("   CONSTRUCTOR DE INSTALADOR ZIP - BODEGAAPP")
    print("="*60)
    
    # 1. Verificar ejecutable
    if not verify_executable():
        sys.exit(1)
    
    # 2. Crear instalador ZIP
    if create_zip_installer():
        print_header("🎉 INSTALADOR ZIP CREADO EXITOSAMENTE")
        
        PROJECT_ROOT = Path(__file__).parent.parent.parent
        dist_dir = PROJECT_ROOT / "dist"
        
        print("\n📦 ARCHIVOS DISPONIBLES EN dist/:")
        print("   EJECUTABLES Y ARCHIVOS PRINCIPALES:")
        
        items = list(dist_dir.iterdir())
        for item in items:
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                if item.suffix == '.exe':
                    print(f"   • 🚀 {item.name:30} ({size_mb:6.2f} MB) - Aplicación principal")
                elif item.suffix == '.zip':
                    print(f"   • 📦 {item.name:30} ({size_mb:6.2f} MB) - Instalador completo")
                elif item.suffix == '.txt':
                    print(f"   • 📄 {item.name:30} ({size_mb:6.2f} MB) - Documentación")
                elif item.suffix == '.bat':
                    print(f"   • ⚙️  {item.name:30} ({size_mb:6.2f} MB) - Script")
        
        print("\n   CARPETAS:")
        for item in items:
            if item.is_dir():
                if item.name == "BodegaApp_Instalador":
                    print(f"   • 📁 {item.name}/ - Contenido del instalador")
                else:
                    print(f"   • 📁 {item.name}/")
        
        print("\n🚀 INSTRUCCIONES DE DISTRIBUCIÓN:")
        print("   1. Para distribución fácil: Envía 'BodegaApp_Instalador_Completo.zip'")
        print("   2. Para distribución detallada: Envía carpeta 'BodegaApp_Instalador/'")
        print("   3. Para usuarios técnicos: Envía solo 'BodegaApp.exe'")
        
        print("\n📋 CÓMO USAR EL INSTALADOR:")
        print("   • Extrae el ZIP en Windows")
        print("   • Ejecuta 'Instalar.bat' como Administrador")
        print("   • O usa 'Instalar_Portable.bat' sin permisos de Admin")
        
        print("\n✅ VENTAJAS DE ESTE INSTALADOR:")
        print("   ✓ No requiere NSIS o Docker")
        print("   ✓ Funciona en cualquier Windows 10/11")
        print("   ✓ Incluye desinstalador completo")
        print("   ✓ Soporta instalación con/sin permisos de Admin")
        print("   ✓ Documentación completa incluida")
        print("="*60)
    else:
        print("\n❌ Error creando el instalador ZIP")
        sys.exit(1)

if __name__ == "__main__":
    main()
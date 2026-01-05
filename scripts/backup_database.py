"""
Script para realizar backup de la base de datos
"""
import sqlite3
import shutil
from datetime import datetime
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DATABASE_PATH, DATA_DIR, BACKUP_DIR


def backup_database(verbose=True):
    """Crea una copia de seguridad de la base de datos"""
    try:
        if verbose:
            print("=" * 50)
            print("📦 INICIANDO BACKUP DE BASE DE DATOS")
            print("=" * 50)
        
        # Verificar si la base de datos existe
        if not os.path.exists(DATABASE_PATH):
            error_msg = f"❌ Error: Base de datos no encontrada en:\n{DATABASE_PATH}"
            if verbose:
                print(error_msg)
                print("   Verifique que la base de datos exista y la ruta sea correcta.")
            return False, error_msg
        
        if verbose:
            db_size = os.path.getsize(DATABASE_PATH)
            print(f"✅ Base de datos encontrada: {DATABASE_PATH}")
            print(f"📊 Tamaño: {db_size:,} bytes")
        
        # Usar el directorio de backups definido en settings
        backup_dir = BACKUP_DIR
        
        # Crear directorio de backups si no existe
        os.makedirs(backup_dir, exist_ok=True)
        
        if verbose:
            print(f"📁 Directorio de backups: {backup_dir}")
        
        # Verificar permisos de escritura
        try:
            # Intentar crear un archivo temporal para verificar permisos
            test_file = os.path.join(backup_dir, ".write_test.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            if verbose:
                print(f"✅ Permisos de escritura verificados")
        except PermissionError:
            error_msg = f"❌ Error: Sin permisos de escritura en: {backup_dir}"
            if verbose:
                print(error_msg)
            return False, error_msg
        
        # Nombre del backup con fecha y hora
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"bodega_backup_{timestamp}.db"
        backup_file = os.path.join(backup_dir, backup_filename)
        
        if verbose:
            print("🔄 Creando backup...")
        
        # Método 1: Usar shutil.copy2 (más simple y rápido)
        shutil.copy2(DATABASE_PATH, backup_file)
        
        # Verificar que el backup se creó correctamente
        if not os.path.exists(backup_file):
            error_msg = f"❌ Error: No se pudo crear el archivo de backup"
            if verbose:
                print(error_msg)
            return False, error_msg
        
        # Verificar integridad del backup
        backup_size = os.path.getsize(backup_file)
        original_size = os.path.getsize(DATABASE_PATH)
        
        if backup_size == 0:
            error_msg = f"❌ Error: Backup creado pero está vacío"
            if verbose:
                print(error_msg)
            os.remove(backup_file)  # Eliminar backup corrupto
            return False, error_msg
        
        # Verificar que el tamaño sea similar (puede variar un poco por overhead de SQLite)
        size_diff = abs(backup_size - original_size)
        if size_diff > 1024:  # Más de 1KB de diferencia
            if verbose:
                print(f"⚠️  Advertencia: Diferencia de tamaño: {size_diff:,} bytes")
        
        if verbose:
            print(f"✅ Backup creado exitosamente!")
            print(f"   📄 Archivo: {backup_filename}")
            print(f"   📊 Tamaño: {backup_size:,} bytes")
            print(f"   📍 Ubicación: {backup_dir}")
        
        # Limpiar backups antiguos (mantener solo los últimos 10)
        cleanup_old_backups(backup_dir, max_backups=10, verbose=verbose)
        
        return True, backup_file
        
    except PermissionError as e:
        error_msg = f"❌ Error de permisos: {str(e)}"
        if verbose:
            print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error inesperado al crear backup: {str(e)}"
        if verbose:
            print(error_msg)
        import traceback
        if verbose:
            traceback.print_exc()
        return False, error_msg


def cleanup_old_backups(backup_dir, max_backups=10, verbose=True):
    """Elimina backups antiguos, manteniendo solo los más recientes"""
    try:
        # Obtener todos los archivos de backup
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("bodega_backup_") and filename.endswith(".db"):
                filepath = os.path.join(backup_dir, filename)
                if os.path.isfile(filepath):
                    backup_files.append((filepath, os.path.getmtime(filepath)))
        
        # Ordenar por fecha de modificación (más antiguos primero)
        backup_files.sort(key=lambda x: x[1])
        
        # Eliminar los más antiguos si hay más de max_backups
        if len(backup_files) > max_backups:
            files_to_delete = backup_files[:len(backup_files) - max_backups]
            deleted_count = 0
            freed_space = 0
            
            for filepath, _ in files_to_delete:
                try:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    deleted_count += 1
                    freed_space += file_size
                    if verbose:
                        print(f"🗑️  Eliminado backup antiguo: {os.path.basename(filepath)}")
                except Exception as e:
                    if verbose:
                        print(f"⚠️  No se pudo eliminar {filepath}: {str(e)}")
            
            if verbose and deleted_count > 0:
                print(f"🧹 Limpieza completada: {deleted_count} backups antiguos eliminados")
                print(f"💾 Espacio liberado: {freed_space:,} bytes")
                
    except Exception as e:
        if verbose:
            print(f"⚠️  Error al limpiar backups antiguos: {str(e)}")


def list_backups(backup_dir=None):
    """Lista todos los backups disponibles"""
    if backup_dir is None:
        backup_dir = BACKUP_DIR
    
    if not os.path.exists(backup_dir):
        print(f"❌ Directorio de backups no encontrado: {backup_dir}")
        return []
    
    print(f"\n📋 BACKUPS DISPONIBLES en {backup_dir}:")
    print("=" * 60)
    
    backups = []
    for filename in sorted(os.listdir(backup_dir)):
        if filename.startswith("bodega_backup_") and filename.endswith(".db"):
            filepath = os.path.join(backup_dir, filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                backups.append((filename, size, mod_time))
    
    if not backups:
        print("No se encontraron backups")
        return []
    
    for i, (filename, size, mod_time) in enumerate(backups, 1):
        print(f"{i:2d}. {filename}")
        print(f"    Tamaño: {size:,} bytes")
        print(f"    Fecha:  {mod_time.strftime('%d/%m/%Y %H:%M:%S')}")
        print()
    
    return backups


def restore_backup(backup_file, verbose=True):
    """Restaura la base de datos desde un backup"""
    try:
        if verbose:
            print("=" * 50)
            print("🔄 INICIANDO RESTAURACIÓN DE BACKUP")
            print("=" * 50)
        
        # Verificar que el backup existe
        if not os.path.exists(backup_file):
            error_msg = f"❌ Error: Archivo de backup no encontrado: {backup_file}"
            if verbose:
                print(error_msg)
            return False, error_msg
        
        # Verificar que el backup no esté vacío
        backup_size = os.path.getsize(backup_file)
        if backup_size == 0:
            error_msg = f"❌ Error: El archivo de backup está vacío"
            if verbose:
                print(error_msg)
            return False, error_msg
        
        # Crear backup de la base de datos actual antes de restaurar
        if os.path.exists(DATABASE_PATH):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = os.path.join(BACKUP_DIR, f"pre_restore_{timestamp}.db")
            shutil.copy2(DATABASE_PATH, pre_restore_backup)
            if verbose:
                print(f"✅ Backup pre-restauración creado: {pre_restore_backup}")
        
        # Restaurar el backup
        if verbose:
            print(f"🔄 Restaurando desde: {backup_file}")
            print(f"📊 Tamaño del backup: {backup_size:,} bytes")
        
        shutil.copy2(backup_file, DATABASE_PATH)
        
        # Verificar que la restauración fue exitosa
        if not os.path.exists(DATABASE_PATH):
            error_msg = "❌ Error: No se pudo restaurar la base de datos"
            if verbose:
                print(error_msg)
            return False, error_msg
        
        restored_size = os.path.getsize(DATABASE_PATH)
        if restored_size == 0:
            error_msg = "❌ Error: Base de datos restaurada pero está vacía"
            if verbose:
                print(error_msg)
            return False, error_msg
        
        if verbose:
            print(f"✅ Restauración completada exitosamente!")
            print(f"📊 Base de datos restaurada: {DATABASE_PATH}")
            print(f"📈 Tamaño restaurado: {restored_size:,} bytes")
        
        return True, DATABASE_PATH
        
    except Exception as e:
        error_msg = f"❌ Error al restaurar backup: {str(e)}"
        if verbose:
            print(error_msg)
        return False, error_msg


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Herramienta de backup/restauración de base de datos")
    parser.add_argument("--backup", action="store_true", help="Crear backup")
    parser.add_argument("--restore", type=str, help="Restaurar desde archivo específico")
    parser.add_argument("--list", action="store_true", help="Listar backups disponibles")
    parser.add_argument("--cleanup", action="store_true", help="Limpiar backups antiguos")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso")
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    if args.backup:
        success, result = backup_database(verbose=verbose)
        if success:
            if verbose:
                print("\n" + "=" * 50)
                print("✅ BACKUP COMPLETADO EXITOSAMENTE")
                print("=" * 50)
            sys.exit(0)
        else:
            if verbose:
                print("\n" + "=" * 50)
                print(f"❌ ERROR EN BACKUP: {result}")
                print("=" * 50)
            sys.exit(1)
    
    elif args.restore:
        success, result = restore_backup(args.restore, verbose=verbose)
        if success:
            if verbose:
                print("\n" + "=" * 50)
                print("✅ RESTAURACIÓN COMPLETADA EXITOSAMENTE")
                print("=" * 50)
            sys.exit(0)
        else:
            if verbose:
                print("\n" + "=" * 50)
                print(f"❌ ERROR EN RESTAURACIÓN: {result}")
                print("=" * 50)
            sys.exit(1)
    
    elif args.list:
        list_backups()
        sys.exit(0)
    
    elif args.cleanup:
        cleanup_old_backups(BACKUP_DIR, verbose=verbose)
        sys.exit(0)
    
    else:
        # Por defecto, mostrar ayuda
        parser.print_help()
        sys.exit(0)
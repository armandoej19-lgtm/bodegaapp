# src/app.py
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import tkinter as tk
import pandas as pd
import os

# Importaciones internas
from src.database import Database
from config import settings
from config.device_config import *
from views.register_view import RegisterView
from views.search_view import SearchView
from views.info_view import InfoView
from scripts.backup_database import backup_database


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Inicializar base de datos
        self.db = Database()
        
        self.title('Bodega Register App')
        self.geometry('1080x600')
        
        # Variables para almacenar resultados de búsqueda
        self.current_results = []
        self.current_search_term = ""
        self.current_search_by = ""
        
        # Configurar variables de dispositivo
        self.device_models = DEVICE_MODELS
        self.device_types = DEVICE_TYPES
        self.failure_types = FAILURE_TYPES

        # Variables para control de backup
        self.last_backup_check = None
        
        # Iniciar verificación de backup si está configurado
        if settings.BACKUP_ENABLED and settings.AUTO_BACKUP_ON_START:
            self.after(2000, self.check_auto_backup) # Esperar 2 segundos después de iniciar

        # Configurar sistema de backup automático
        self.setup_backup_system()

        # Configurar interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # tabs viewing...
        self.tabview = ctk.CTkTabview(master=self, width=1366, height=768)
        self.tabview.pack(padx=10, pady=10)
        
        # Pestaña de registro
        self.registertab = self.tabview.add('Registro')
        self.setup_register_tab()
        
        # Pestaña de búsqueda
        self.searchtab = self.tabview.add('Búsqueda')
        self.setup_search_tab()

        # Pestaña de información
        self.infotab = self.tabview.add('Información')
        self.setup_info_tab()
    
    def setup_register_tab(self):
        """Configura la pestaña de registro usando RegisterView"""
        # Botón para nueva entrada
        self.addbutton = ctk.CTkButton(
            master=self.registertab,
            width=800,
            height=30,
            anchor='center',
            text='(+) Añade un nuevo dispositivo',
            font=ctk.CTkFont(size=16, weight='bold'),
            command=self.show_register_view
        )
        self.addbutton.pack(padx=10, pady=10)
    
    def show_register_view(self):
        """Muestra la vista de registro"""
        self.addbutton.pack_forget()
        
        self.register_view = RegisterView(
            self.registertab,
            self.db,
            on_save_callback=self.on_device_saved,
            on_cancel_callback=self.hide_register_view
        )
        self.register_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    def hide_register_view(self):
        """Oculta la vista de registro"""
        if hasattr(self, 'register_view'):
            self.register_view.destroy()
        self.addbutton.pack(padx=10, pady=10)
    
    def on_device_saved(self, device_id, serialno):
        """Callback cuando se guarda un dispositivo"""
        print(f"Dispositivo guardado: {serialno} (ID: {device_id})")
        messagebox.showinfo("Éxito", f"Dispositivo {serialno} guardado correctamente")
    
    def setup_search_tab(self):
        """Configura la pestaña de búsqueda usando SearchView"""
        self.search_view = SearchView(
            self.searchtab,
            self.db,
            on_export_callback=self.on_export_requested,
            on_delete_callback=self.on_delete_requested
        )
        self.search_view.pack(fill="both", expand=True)
    
    def on_export_requested(self, data, search_by):
        """Callback para exportación"""
        try:
            if not data:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            # Crear directorio de exportaciones si no existe
            export_dir = os.path.join('data', 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Generar nombre de archivo con fecha y hora
            fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"bodega_export_{fecha_hora}.xlsx"
            
            # Abrir diálogo en el directorio exports
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                initialdir=export_dir,
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Procesar datos - SOLO código de planta (no nombre)
            processed_data = []
            
            for row in data:
                # Asegurar que la fila tenga al menos 8 elementos
                if len(row) >= 8:
                    # Obtener código de planta (ya está en la base de datos)
                    plant_code = row[1] if row[1] else ""
                    
                    # Formatear fecha para mejor legibilidad
                    fecha = row[7] if len(row) > 7 and row[7] else ""
                    if fecha:
                        try:
                            dt = datetime.strptime(str(fecha), '%Y-%m-%d %H:%M:%S')
                            fecha = dt.strftime('%d/%m/%Y %H:%M')
                        except:
                            # Si falla, mantener el formato original
                            pass
                    
                    # Crear fila procesada - SOLO código de planta
                    processed_row = (
                        row[0] if len(row) > 0 and row[0] else "",      # ID
                        plant_code,                                      # Código Planta (ej: "UP02")
                        row[2] if len(row) > 2 and row[2] else "",      # Serial
                        row[3] if len(row) > 3 and row[3] else "",      # Tipo
                        row[4] if len(row) > 4 and row[4] else "",      # Modelo
                        row[5] if len(row) > 5 and row[5] else "",      # Falla
                        row[6] if len(row) > 6 and row[6] else "",      # Observaciones
                        fecha                                           # Fecha
                    )
                    processed_data.append(processed_row)
            
            # Definir columnas (ahora 8 columnas - sin "Nombre Planta")
            columns = [
                "ID", 
                "Código Planta",
                "Serial", 
                "Tipo", 
                "Modelo", 
                "Falla", 
                "Fecha", 
                "Observaciones"
            ]
            
            # Convertir a DataFrame
            df = pd.DataFrame(processed_data, columns=columns)
            
            # Exportar a Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            # Preguntar si quiere abrir la carpeta
            open_folder = messagebox.askyesno(
                "[OK] Exportación Completada",
                f"Archivo guardado en:\n{file_path}\n\n"
                f"¿Abrir carpeta contenedora?"
            )
            
            if open_folder:
                self.open_file_explorer(file_path)
            
        except Exception as e:
            messagebox.showerror("[ERROR] Error", f"Error al exportar: {str(e)}")
        
    def open_file_explorer(self, file_path):
        """Abre el explorador de archivos en la ubicación del archivo"""
        try:
            import subprocess
            import platform
            
            # Obtener el directorio del archivo
            directory = os.path.dirname(file_path)
            
            # Abrir según el sistema operativo
            system = platform.system()
            
            if system == "Windows":
                os.startfile(directory)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", directory])
            else:  # Linux y otros Unix
                subprocess.run(["xdg-open", directory])
                
        except Exception as e:
            # Si falla, mostrar mensaje con la ruta
            messagebox.showinfo(
                "Ubicación del archivo",
                f"Directorio: {directory}\n"
                f"Puede abrirlo manualmente desde su explorador de archivos."
            )

    def on_delete_requested(self, identifier, is_single=True, search_by=None):
        """Callback para eliminación CON VALIDACIONES"""
        try:
            if is_single:
                # Eliminar registro individual (sin restricciones)
                confirm = messagebox.askyesno(
                    "Confirmar eliminación",
                    f"¿Está seguro de eliminar el registro con ID {identifier}?"
                )
                
                if confirm:
                    # Buscar el serial del dispositivo
                    self.db.cur.execute("SELECT serialno FROM DeviceReg WHERE id = ?", (identifier,))
                    result = self.db.cur.fetchone()
                    
                    if result:
                        serialno = result[0]
                        deleted = self.db.del_SData(serialno, "serialno", exact_match=True)
                        
                        if deleted > 0:
                            messagebox.showinfo("Éxito", f"Registro {identifier} eliminado")
                            if hasattr(self, 'search_view'):
                                self.search_view.refresh_results()
            else:
                # VALIDACIÓN: No permitir eliminar por "Todos" o "Por Tipo"
                if search_by in ["Todos", "Por Tipo"]:
                    messagebox.showerror(
                        "Operación no permitida",
                        f"No está permitido eliminar dispositivos usando '{search_by}'.\n"
                        "Use una búsqueda más específica."
                    )
                    return
                
                # Mapear search_by a parámetro de base de datos
                search_map = {
                    "Por Serial": "serialno",
                    "Por Modelo": "model",
                    "Fecha": "entry_date"
                }
                
                db_search_by = search_map.get(search_by, "serialno")
                deleted = self.db.del_SData(identifier, db_search_by)
                
                if deleted > 0:
                    messagebox.showinfo("Éxito", f"{deleted} registros eliminados")
                    if hasattr(self, 'search_view'):
                        self.search_view.refresh_results()
                        
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def setup_info_tab(self):
        '''Información adicional y Documentación de la Aplicación'''
        # Crear instancia de InfoView
        self.info_view = InfoView(self.infotab)
        self.info_view.pack(fill="both", expand=True, padx=10, pady=10)

    def get_last_backup_file(self):
            """Obtiene el archivo de backup más reciente"""
            try:
                from config.settings import BACKUP_DIR
                
                if not os.path.exists(BACKUP_DIR):
                    return None
                
                backup_files = []
                for filename in os.listdir(BACKUP_DIR):
                    if filename.startswith("bodega_backup_") and filename.endswith(".db"):
                        filepath = os.path.join(BACKUP_DIR, filename)
                        if os.path.isfile(filepath):
                            backup_files.append((filepath, os.path.getmtime(filepath)))
                
                if not backup_files:
                    return None
                
                # Ordenar por fecha (más reciente primero)
                backup_files.sort(key=lambda x: x[1], reverse=True)
                return backup_files[0][0]
                
            except Exception as e:
                print(f"[WARNING!] Error obteniendo último backup: {e}")
                return None

    def setup_backup_system(self):
        """Configura el sistema de backup automático"""
        if not settings.BACKUP_ENABLED:
            print("[i]  Sistema de backup deshabilitado en configuración")
            return
        
        print(f"[i] Sistema de backup configurado:")
        print(f"   • Intervalo: cada {settings.BACKUP_INTERVAL_HOURS} horas")  
        print(f"   • Máximo backups: {settings.MAX_BACKUP_FILES}")
        print(f"   • Backup al iniciar: {'Sí' if settings.AUTO_BACKUP_ON_START else 'No'}")
        print(f"   • Backup al cerrar: {'Sí' if settings.AUTO_BACKUP_ON_EXIT else 'No'}")
        
        # Programar verificación periódica (cada hora)
        self.after(3600000, self.periodic_backup_check)

    def periodic_backup_check(self):  # <-- MÉTODO FALTANTE
        """Verificación periódica de backup"""
        if settings.BACKUP_ENABLED:
            self.check_auto_backup()
            # Programar siguiente verificación (cada hora)
            self.after(3600000, self.periodic_backup_check)

    def check_auto_backup(self):
        last_backup_file = self.get_last_backup_file()
        
        # Determinar si se necesita crear backup
        if self.should_create_backup(last_backup_file):
            print("C. Creando backup automatico...")
            self.create_auto_backup()
        else:
            if last_backup_file:
                last_time = os.path.getmtime(last_backup_file)
                last_date = datetime.fromtimestamp(last_time)
                next_backup = last_date + timedelta(hours=settings.BACKUP_INTERVAL_HOURS)
                print(f"C. Próximo backup programado: {next_backup.strftime('%d/%m/%Y %H:%M')}")

    def check_min_db_size(self):
        """Verifica que la BD tenga el tamaño mínimo configurado"""
        try:
            from config.settings import DATABASE_PATH, BACKUP_MIN_DB_SIZE
            
            if not os.path.exists(DATABASE_PATH):
                return False
                
            db_size = os.path.getsize(DATABASE_PATH)
            return db_size >= BACKUP_MIN_DB_SIZE
            
        except Exception as e:
            print(f"[WARNING!] Error verificando tamaño de BD: {e}")
            return False

    def should_create_backup(self, last_backup_file):
        """Determina si se debe crear backup basado en configuración"""
        try:
            # Si nunca se ha creado backup
            if last_backup_file is None:
                return True
            
            # Verificar intervalo configurado
            last_backup_time = os.path.getmtime(last_backup_file)
            last_backup_date = datetime.fromtimestamp(last_backup_time)
            current_date = datetime.now()
            
            # Calcular diferencia en horas
            time_diff = current_date - last_backup_date
            hours_diff = time_diff.total_seconds() / 3600
            
            return hours_diff >= settings.BACKUP_INTERVAL_HOURS
            
        except Exception as e:
            print(f"[WARNING!] Error verificando necesidad de backup: {e}")
            return True  # En caso de error, mejor crear backup

    def create_auto_backup(self):
        """Crea backup automático usando configuración"""
        try:
            from config.settings import MAX_BACKUP_FILES
            
            success, result = backup_database(verbose=False)
            
            if success:
                print(f"[OK] Backup automático creado: {os.path.basename(result)}")
                
                # Limpiar backups antiguos según configuración
                self.cleanup_old_backups(MAX_BACKUP_FILES)
                
                # Registrar hora del último backup
                self.last_backup_check = datetime.now()
                
            else:
                print(f"[WARNING!] No se pudo crear backup automático: {result}")
                
        except Exception as e:
            print(f"[ERROR] Error en backup automático: {e}")

    def cleanup_old_backups(self, max_files):
        """Limpia backups antiguos según configuración"""
        try:
            from config.settings import BACKUP_DIR
            
            if not os.path.exists(BACKUP_DIR):
                return
                
            # Obtener todos los backups
            backup_files = []
            for filename in os.listdir(BACKUP_DIR):
                if filename.startswith("bodega_backup_") and filename.endswith(".db"):
                    filepath = os.path.join(BACKUP_DIR, filename)
                    if os.path.isfile(filepath):
                        backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # Ordenar por fecha (más antiguos primero)
            backup_files.sort(key=lambda x: x[1])
            
            # Eliminar excedentes
            if len(backup_files) > max_files:
                files_to_delete = backup_files[:len(backup_files) - max_files]
                for filepath, _ in files_to_delete:
                    try:
                        os.remove(filepath)
                        print(f"[i]  Eliminado backup antiguo: {os.path.basename(filepath)}")
                    except Exception as e:
                        print(f"[WARNING!]  No se pudo eliminar backup: {e}")
                        
        except Exception as e:
            print(f"[WARNING!] Error limpiando backups antiguos: {e}")

    def on_closing(self):
        """Cierra la aplicación con backup si está configurado"""
        try:
            # Backup antes de cerrar si está configurado
            if settings.BACKUP_ENABLED and settings.AUTO_BACKUP_ON_EXIT:
                self.create_exit_backup()
            
        except Exception as e:
            print(f"[WARNING!] Error en proceso de cierre: {e}")
        finally:
            # Cerrar base de datos y aplicación
            self.db.close()
            self.destroy()

    def create_exit_backup(self):
        """Crea backup al cerrar la aplicación si es necesario"""
        try:
            # Verificar si se necesita backup
            last_backup_file = self.get_last_backup_file()
            
            if last_backup_file is None or self.should_create_exit_backup(last_backup_file):
                print("[i] Creando backup antes de cerrar...")
                success, result = backup_database(verbose=False)
                if success:
                    print(f"[OK] Backup de cierre creado: {os.path.basename(result)}")
                    
        except Exception as e:
            print(f"[WARNING!] Error en backup de cierre: {e}")

    def should_create_exit_backup(self, last_backup_file):
        """Determina si se debe crear backup al cerrar"""
        try:
            # Si el último backup fue hace más de 6 horas, crear uno nuevo
            last_backup_time = os.path.getmtime(last_backup_file)
            last_backup_date = datetime.fromtimestamp(last_backup_time)
            current_date = datetime.now()
            
            time_diff = current_date - last_backup_date
            return time_diff.total_seconds() > 6 * 3600  # 6 horas
            
        except Exception as e:
            print(f"[WARNING!] Error verificando backup de cierre: {e}")
            return False

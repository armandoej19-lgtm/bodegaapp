"""
Vista para búsqueda y gestión de dispositivos
CON PROTECCIONES CONTRA ELIMINACIONES MASIVAS
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime


class SearchView(ctk.CTkFrame):
    """Vista para buscar y gestionar dispositivos"""
    
    def __init__(self, master, db, on_export_callback=None, on_delete_callback=None):
        super().__init__(master)
        
        self.db = db
        self.on_export_callback = on_export_callback
        self.on_delete_callback = on_delete_callback
        
        # Variables de estado
        self.current_results = []
        self.current_search_term = ""
        self.current_search_by = ""
        self.selected_device_id = None
        
        # Configurar interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Crear controles de búsqueda
        self.create_search_controls()
        
        # Crear tabla de resultados
        self.create_results_table()
        
        # Crear controles de acción
        self.create_action_controls()
    
    def create_search_controls(self):
        """Crea los controles de búsqueda"""
        # Frame para controles
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Etiqueta
        ctk.CTkLabel(search_frame, text="🔍 Buscar:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=(10, 5), pady=10, sticky="w"
        )
        
        # Campo de búsqueda
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Ingrese término de búsqueda...",
            width=250
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        
        # Opciones de búsqueda
        self.search_option = ctk.CTkOptionMenu(
            search_frame,
            values=["Por Serial", "Por Tipo", "Por Modelo", "Por Fecha", "Todos"],
            width=120
        )
        self.search_option.set("Por Serial")
        self.search_option.grid(row=0, column=2, padx=5, pady=10)
        
        # Botón de búsqueda
        self.search_btn = ctk.CTkButton(
            search_frame,
            text="Buscar",
            command=self.perform_search,
            width=80
        )
        self.search_btn.grid(row=0, column=3, padx=5, pady=10)
        
        # Botón de limpiar
        self.clear_btn = ctk.CTkButton(
            search_frame,
            text="Limpiar",
            command=self.clear_search,
            width=80,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_btn.grid(row=0, column=4, padx=(5, 10), pady=10)
    
    def create_results_table(self):
        """Crea la tabla de resultados"""
        # Frame para la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar Treeview
        columns = ("ID", "Planta", "Serial", "Tipo", "Modelo", "Falla", "Fecha", "Observaciones")
        
        # Crear Treeview con estilo
        style = ttk.Style()
        style.configure("Treeview", 
                       background="#2a2d2e",
                       foreground="white",
                       rowheight=25,
                       fieldbackground="#2a2d2e")
        style.map('Treeview', background=[('selected', '#22559b')])
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
            style="Treeview"
        )
        
        # Configurar columnas
        column_widths = {
        "ID": 50,
        "Planta": 80,
        "Serial": 150,
        "Tipo": 120,
        "Modelo": 150,
        "Falla": 120,
        "Fecha": 120,
        "Observaciones": 200
        }   
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar vertical
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Scrollbar horizontal
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Evento de selección
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)
    
    def create_action_controls(self):
        """Crea los controles de acción"""
        # Frame para botones de acción
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        # Botón: Exportar
        self.export_btn = ctk.CTkButton(
            action_frame,
            text="📤 Exportar a Excel",
            command=self.on_export,
            width=140,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.export_btn.pack(side="left", padx=(0, 10))
        
        # Botón: Editar seleccionado
        self.edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Editar",
            command=self.on_edit,
            width=100,
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=(0, 10))
        
        # Botón: Eliminar seleccionado
        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Eliminar",
            command=self.on_delete_selected,
            width=100,
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=(0, 10))
        
        # Botón: Eliminar filtrados (CON TEXTO DINÁMICO)
        self.delete_filtered_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Eliminar Filtrados",
            command=self.on_delete_filtered,
            width=140,
            fg_color="#ff6b6b",
            hover_color="#ff5252"
        )
        self.delete_filtered_btn.pack(side="left")
        
        # Etiqueta de resultados
        self.results_label = ctk.CTkLabel(
            action_frame,
            text="0 resultados",
            font=ctk.CTkFont(size=12)
        )
        self.results_label.pack(side="right", padx=(0, 10))
    
    def perform_search(self):
        """Realiza la búsqueda en la base de datos"""
        search_term = self.search_entry.get().strip()
        option = self.search_option.get()
        
        # Guardar términos de búsqueda
        self.current_search_term = search_term
        self.current_search_by = option
        
        # Limpiar tabla
        self.clear_table()
        
        # Validar
        if not search_term and option != "Todos":
            messagebox.showwarning("Advertencia", "Ingrese un término de búsqueda")
            return
        
        try:
            # Mapear opción a parámetro de base de datos
            search_map = {
                "Por Serial": "serialno",
                "Por Tipo": "type",
                "Por Modelo": "model",
                "Por Fecha": "entry_date",
                "Todos": "all"
            }
            
            if option == "Todos":
                results = self.db.get_all_devices()
            elif option == "Por Fecha":
                # Validar y formatear fecha
                formatted_date = self.validate_and_format_date(search_term)
                if not formatted_date:
                    self.show_date_format_help()
                    return
                results = self.db.search_device(f"{formatted_date}%", search_map[option])
            else:
                results = self.db.search_device(search_term, search_map[option])
            
            # Guardar resultados
            self.current_results = results
            
            # Mostrar en tabla
            self.display_results(results)
            
            # Actualizar etiqueta
            self.results_label.configure(text=f"{len(results)} resultados")
            
            # Actualizar estado de botones CON RESTRICCIONES
            self.update_buttons_state(len(results), option, search_term)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def validate_and_format_date(self, date_str):
        """Valida y formatea una fecha para búsqueda"""
        date_str = date_str.strip()
        
        try:
            # Intentar diferentes formatos
            formats = [
                "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y",
                "%Y-%m", "%Y/%m", "%m-%Y", "%m/%Y", "%Y"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    if len(date_str) == 4:  # Solo año
                        return f"{dt.year}"
                    elif len(date_str) == 7:  # Año-mes
                        return f"{dt.year}-{dt.month:02d}"
                    else:  # Fecha completa
                        return f"{dt.year}-{dt.month:02d}-{dt.day:02d}"
                except ValueError:
                    continue
            
            return None
        except:
            return None
    
    def show_date_format_help(self):
        """Muestra ayuda sobre formatos de fecha"""
        messagebox.showerror(
            "Formato de fecha inválido",
            "Formatos aceptados:\n\n"
            "• Solo año: 2024\n"
            "• Año-Mes: 2024-01 o 2024/01\n"
            "• Fecha completa:\n"
            "  - AAAA-MM-DD: 2024-01-15\n"
            "  - DD/MM/AAAA: 15/01/2024"
        )
    
    def display_results(self, results):
        """Muestra resultados en la tabla"""
        for row in results:
            # Asegúrate de que la fila tenga al menos 8 elementos
            if len(row) >= 8:
                # Formatear fecha para mostrar (ahora en índice 7)
                formatted_date = row[7]
                if formatted_date:
                    try:
                        dt = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')
                        formatted_date = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
                
                # Insertar en tabla con 8 columnas
                self.tree.insert("", "end", values=(
                    row[0],      # ID
                    row[1],      # Planta
                    row[2],      # Serial
                    row[3],      # Tipo
                    row[4],      # Modelo
                    row[5],      # Falla
                    row[6] if len(row) > 6 else "",  # Observaciones
                    formatted_date  # Fecha
                ))
    
    def clear_table(self):
        """Limpia la tabla de resultados"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_results = []
        self.selected_device_id = None
        self.update_buttons_state(0, self.current_search_by, self.current_search_term)
    
    def clear_search(self):
        """Limpia la búsqueda"""
        self.search_entry.delete(0, 'end')
        self.search_option.set("Por Serial")
        self.clear_table()
        self.results_label.configure(text="0 resultados")
    
    def on_row_select(self, event):
        """Maneja la selección de una fila"""
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.tree.item(item, 'values')
            if values:
                self.selected_device_id = values[0]
                self.edit_btn.configure(state="normal")
                self.delete_btn.configure(state="normal")
        else:
            self.selected_device_id = None
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
    
    def update_buttons_state(self, result_count, search_by, search_term):
        """Actualiza el estado de los botones con RESTRICCIONES DE SEGURIDAD"""
        
        # Restricción 1: No permitir "Eliminar filtrados" cuando es búsqueda "Todos"
        if search_by == "Todos":
            self.delete_filtered_btn.configure(
                state="disabled",
                text="❌ No permitido (todos)",
                fg_color="gray",
                hover_color="darkgray"
            )
            return
        
        # Restricción 2: No permitir "Eliminar filtrados" cuando es búsqueda "Por Tipo"
        if search_by == "Por Tipo":
            self.delete_filtered_btn.configure(
                state="disabled",
                text=f"❌ No permitido ({search_term})",
                fg_color="gray",
                hover_color="darkgray"
            )
            return
        
        # Restricción 3: Para búsqueda "Por Modelo" con muchos resultados, confirmación extra
        if search_by == "Por Modelo" and result_count > 5:
            self.delete_filtered_btn.configure(
                state="normal",
                text=f"⚠️ Eliminar {result_count}",
                fg_color="#ffc107",
                hover_color="#e0a800"
            )
        elif result_count > 0:
            self.delete_filtered_btn.configure(
                state="normal",
                text=f"🗑️ Eliminar ({result_count})",
                fg_color="#ff6b6b",
                hover_color="#ff5252"
            )
        else:
            self.delete_filtered_btn.configure(
                state="disabled",
                text="🗑️ Eliminar Filtrados",
                fg_color="gray",
                hover_color="darkgray"
            )
    
    def on_export(self):
        """Maneja la exportación"""
        if self.on_export_callback:
            self.on_export_callback(self.current_results, self.current_search_by)
    
    def on_edit(self):
        """Maneja la edición del dispositivo seleccionado"""
        if self.selected_device_id and hasattr(self.master, 'switch_to_edit_mode'):
            self.master.switch_to_edit_mode(self.selected_device_id)
    
    def on_delete_selected(self):
        """Maneja la eliminación del dispositivo seleccionado"""
        if self.selected_device_id and self.on_delete_callback:
            self.on_delete_callback(self.selected_device_id, is_single=True)
    
    def on_delete_filtered(self):
        """Maneja la eliminación de dispositivos filtrados CON VALIDACIONES DE SEGURIDAD"""
        if not self.current_results:
            messagebox.showwarning("Advertencia", "No hay resultados para eliminar")
            return
        
        # VALIDACIÓN 1: No permitir eliminar cuando la búsqueda es "Todos"
        if self.current_search_by == "Todos":
            messagebox.showerror(
                "Operación no permitida",
                "No está permitido eliminar TODOS los dispositivos de la base de datos.\n\n"
                "Realice una búsqueda más específica primero."
            )
            return
        
        # VALIDACIÓN 2: No permitir eliminar cuando la búsqueda es "Por Tipo"
        if self.current_search_by == "Por Tipo":
            messagebox.showerror(
                "Operación no permitida", 
                "No está permitido eliminar todos los dispositivos de un tipo en particular.\n\n"
                "Realice una búsqueda por Serial o Modelo específico."
            )
            return
        
        # VALIDACIÓN 3: Para búsquedas por Modelo, confirmar extra si hay muchos resultados
        if self.current_search_by == "Por Modelo" and len(self.current_results) > 5:
            confirm_modelo = messagebox.askyesno(
                "Confirmación adicional",
                f"Está a punto de eliminar {len(self.current_results)} dispositivos del modelo:\n"
                f"'{self.current_search_term}'\n\n"
                "¿Está completamente seguro?"
            )
            if not confirm_modelo:
                return
        
        # VALIDACIÓN 4: Confirmación final para cualquier eliminación masiva
        confirm = messagebox.askyesno(
            "Confirmar eliminación masiva",
            f"¿Está seguro de eliminar TODOS los {len(self.current_results)} dispositivos de la búsqueda actual?\n\n"
            f"Búsqueda: '{self.current_search_term}' ({self.current_search_by})\n\n"
            "¡Esta acción no se puede deshacer!"
        )
        
        if not confirm:
            return
        
        # Si pasa todas las validaciones, llamar al callback
        if self.on_delete_callback:
            self.on_delete_callback(
                self.current_search_term,
                is_single=False,
                search_by=self.current_search_by
            )
    
    def refresh_results(self):
        """Refresca los resultados actuales"""
        if self.current_search_term or self.current_search_by == "Todos":
            self.perform_search()
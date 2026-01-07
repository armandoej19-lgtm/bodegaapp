"""
Vista para el registro de dispositivos
"""
import customtkinter as ctk
from tkinter import messagebox
from models.device import Device
from config.device_config import PLANT, PLANT_VAL, DEVICE_MODELS, FAILURE_TYPES


class RegisterView(ctk.CTkFrame):
    """Vista para registrar nuevos dispositivos"""
    
    def __init__(self, master, db, on_save_callback=None, on_cancel_callback=None):
        super().__init__(master)
        
        self.db = db
        self.on_save_callback = on_save_callback
        self.on_cancel_callback = on_cancel_callback
        
        # Variables de dispositivo
        self.plant_dict = PLANT
        self.device_plant = PLANT_VAL
        self.device_models = DEVICE_MODELS
        self.device_types = list(DEVICE_MODELS.keys())
        self.failure_types = FAILURE_TYPES
        
        # Variables de control
        self.device = Device()
        self.is_edit_mode = False
        
        # Configurar interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar grid
        self.grid_columnconfigure(1, weight=1)
        
        # Crear campos
        self.create_fields()
        
        # Crear botones
        self.create_buttons()
    
    def create_fields(self):
        """Crea los campos de entrada"""
        self.fields = {}

        # Campo: Número de Planta (Sea: 1, 2 o 3)
        ctk.CTkLabel(self, text="Planta:*", anchor="w").grid(
            row=0, column=0, padx=(20, 10), pady=(20, 8), sticky="w"
        )
        
        self.fields['plant'] = ctk.CTkOptionMenu(
            self,
            values=self.device_plant,               # SOLUCIONAR DETALLE DE LA BD O NOSE QUE!!!
            width=300,
        )
        
        self.fields['plant'].set("Selecciona la planta")
        self.fields['plant'].grid(row=0, column=1, padx=(10, 20), pady=8, sticky="w")

        # Campo: Número de Serie
        ctk.CTkLabel(self, text="Número de Serie:*", anchor="w").grid(
            row=1, column=0, padx=(20, 10), pady=(20, 8), sticky="w"
        )
        self.fields['serial'] = ctk.CTkEntry(self, width=300, placeholder_text="Ej: SN123456789")
        self.fields['serial'].grid(row=1, column=1, padx=(10, 20), pady=(20, 8), sticky="ew")
        
        # Campo: Tipo de Dispositivo
        ctk.CTkLabel(self, text="Tipo de Dispositivo:*", anchor="w").grid(
            row=2, column=0, padx=(20, 10), pady=8, sticky="w"
        )
        self.fields['type'] = ctk.CTkOptionMenu(
            self,
            values=self.device_types,
            width=300,
            command=self.on_device_type_change
        )
        self.fields['type'].set("Seleccionar tipo")
        self.fields['type'].grid(row=2, column=1, padx=(10, 20), pady=8, sticky="w")
        
        # Campo: Modelo
        ctk.CTkLabel(self, text="Modelo:*", anchor="w").grid(
            row=3, column=0, padx=(20, 10), pady=8, sticky="w"
        )
        self.fields['model'] = ctk.CTkComboBox(
            self,
            values=["Selecciona primero el tipo"],
            width=300,
            state="normal"
        )
        self.fields['model'].set("Selecciona primero el tipo")
        self.fields['model'].grid(row=3, column=1, padx=(10, 20), pady=8, sticky="ew")
        
        # Campo: Tipo de Falla
        ctk.CTkLabel(self, text="Tipo de Falla:", anchor="w").grid(
            row=4, column=0, padx=(20, 10), pady=8, sticky="w"
        )
        self.fields['failure'] = ctk.CTkOptionMenu(
            self,
            values=self.failure_types,
            width=300
        )
        self.fields['failure'].set("[0] Sin fallas")
        self.fields['failure'].grid(row=4, column=1, padx=(10, 20), pady=8, sticky="w")
        
        # Campo: Observaciones
        ctk.CTkLabel(self, text="Observaciones:", anchor="w").grid(
            row=5, column=0, padx=(20, 10), pady=8, sticky="w"
        )
        self.fields['observations'] = ctk.CTkTextbox(self, width=300, height=100)
        self.fields['observations'].grid(row=5, column=1, padx=(10, 20), pady=8, sticky="nsew")
        
        # Configurar expansión del textbox
        self.grid_rowconfigure(5, weight=1)
    
    def create_buttons(self):
        """Crea los botones de acción"""
        # Frame para botones
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 20), sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Botón: Guardar y añadir otro
        self.btn_save_add = ctk.CTkButton(
            button_frame,
            text="💾 Guardar y Añadir Otro",
            command=lambda: self.save_device(add_another=True),
            width=150,
            height=35,
            fg_color='#2E86C1',
            hover_color='#1B4F72'
        )
        self.btn_save_add.grid(row=0, column=0, padx=10, pady=10)
        
        # Botón: Guardar
        self.btn_save = ctk.CTkButton(
            button_frame,
            text="💾 Guardar",
            command=lambda: self.save_device(add_another=False),
            width=120,
            height=35,
            fg_color='green',
            hover_color='darkgreen'
        )
        self.btn_save.grid(row=0, column=1, padx=10, pady=10)
        
        # Botón: Cancelar
        self.btn_cancel = ctk.CTkButton(
            button_frame,
            text="✖️ Cancelar",
            command=self.cancel,
            width=120,
            height=35,
            fg_color='red',
            hover_color='darkred'
        )
        self.btn_cancel.grid(row=0, column=2, padx=10, pady=10)
    
    def on_device_type_change(self, selected_type):
        """Actualiza los modelos cuando cambia el tipo de dispositivo"""
        if selected_type in self.device_models:
            models = self.device_models[selected_type]
            self.fields['model'].configure(values=models)
            self.fields['model'].set("Selecciona un modelo")

    def plant_asgined(self, selected_plant):
        """Extrae las opciones para el campo de *Planta* para seleccionar"""
        if selected_plant in self.device_plant:
            plant = self.device_plant[selected_plant]
            self.fields['plant'].configure(values=plant)
            self.fields['plant'].set("Selecciona la planta")
    
    def save_device(self, add_another=True):
        """Guarda el dispositivo en la base de datos"""
        # Obtener datos de los campos
        plant_name = self.fields['plant'].get().strip()  # Esto es "PLANTA 2A"
        serialno = self.fields['serial'].get().strip()
        device_type = self.fields['type'].get()
        model = self.fields['model'].get().strip()
        failure_type = self.fields['failure'].get()
        observations = self.fields['observations'].get("1.0", "end-1c").strip()
        
        # Validaciones
        if not self.validate_inputs(plant_name, serialno, device_type, model):
            return
        
        # OBTENER EL CÓDIGO DE PLANTA
        plant_code = self.get_plant_code(plant_name)  # Esto convierte "PLANTA 2A" a "UP02"
        
        # Extraer código de falla
        failure_code = self.extract_failure_code(failure_type)
        
        try:
            # Guardar en base de datos CON EL CÓDIGO
            device_id = self.db.add_device(
                plant_code,                    # ← Aquí va el CÓDIGO "UP02", no el nombre
                serialno=serialno,
                device_type=device_type,
                model=model,
                failuretype=failure_type,
                observations=observations
            )
            
            if device_id:
                messagebox.showinfo("Éxito", f"Dispositivo guardado\nID: {device_id}")
                
                # Actualizar modelos si es nuevo
                self.update_device_lists(device_type, model)
                
                # Llamar al callback si existe
                if self.on_save_callback:
                    self.on_save_callback(device_id, serialno)
                
                if add_another:
                    self.clear_fields()
                else:
                    self.cancel()
            else:
                messagebox.showerror("Error", "No se pudo guardar el dispositivo")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def get_plant_code(self, plant_name):
        """Convierte nombre de planta a código"""
        # Si ya es un código (ej: "UP01"), devolverlo tal cual
        if plant_name in self.plant_dict:
            return plant_name
        
        # Buscar el código que corresponde al nombre
        for code, name in self.plant_dict.items():
            if name == plant_name:
                return code
        
        # Si no encuentra, devolver el nombre original
        # (por si hay un error o nuevo valor no en la lista)
        return plant_name

    def validate_inputs(self, plant_name, serialno, device_type, model):
        """Valida los campos de entrada"""
        errors = []
        
        if plant_name == "Selecciona la planta":
            errors.append("Primero, debes selecccionar la planta!")

        if not serialno:
            errors.append("El número de serie es obligatorio")
        
        if device_type == "Seleccionar tipo":
            errors.append("Selecciona un tipo de dispositivo")
        
        if model in ["Selecciona primero el tipo", "Selecciona un modelo"] or not model:
            errors.append("Selecciona o ingresa un modelo")
        
        if errors:
            messagebox.showerror("Error de validación", "\n".join(errors))
            return False
        
        return True
    
    def extract_failure_code(self, failure_type):
        """Extrae el código numérico del tipo de falla"""
        try:
            if failure_type.startswith("[") and "]" in failure_type:
                return failure_type.split("[")[1].split("]")[0]
        except:
            pass
        return "0"
    
    def update_device_lists(self, device_type, model):
        """Actualiza las listas de tipos y modelos si son nuevos"""
        # Actualizar tipo si es nuevo
        if device_type not in self.device_types:
            self.device_types.append(device_type)
            self.device_types.sort()
            self.fields['type'].configure(values=self.device_types)
        
        # Actualizar modelo si es nuevo
        if model not in self.device_models.get(device_type, []):
            if device_type not in self.device_models:
                self.device_models[device_type] = []
            self.device_models[device_type].append(model)
            self.device_models[device_type].sort()
            self.on_device_type_change(device_type)
    
    def clear_fields(self):
        """Limpia todos los campos"""
        self.fields['plant'].set("Selecciona la planta")  # ← Cambiado de 'UP01' al texto por defecto
        self.fields['serial'].delete(0, 'end')
        self.fields['type'].set("Seleccionar tipo")
        self.fields['model'].set("Selecciona primero el tipo")
        self.fields['model'].configure(values=["Selecciona primero el tipo"])
        self.fields['failure'].set("[0] Sin fallas")
        self.fields['observations'].delete("1.0", "end")
        self.fields['serial'].focus()    

    def cancel(self):
        """Cancela el registro"""
        if self.on_cancel_callback:
            self.on_cancel_callback()
        else:
            self.clear_fields()
    
    def load_device_for_editing(self, device_id):
        """Carga un dispositivo existente para editar"""
        try:
            # Obtener dispositivo de la base de datos
            self.db.cur.execute("SELECT * FROM DeviceReg WHERE id = ?", (device_id,))
            row = self.db.cur.fetchone()
            
            if row:
                self.device = Device.from_db_row(row)
                self.is_edit_mode = True
                
                # Obtener código de planta de la base de datos
                plant_code = row[1]  # Índice 1 es plant (código "UP02")
                
                # Convertir código a nombre para mostrar
                plant_name = self.plant_dict.get(plant_code, plant_code)
                
                # Rellenar campos
                self.fields['plant'].set(plant_name)  # Mostrar nombre
                self.fields['serial'].insert(0, self.device.serialno)
                self.fields['type'].set(self.device.device_type)
                
                # Actualizar modelos para el tipo seleccionado
                self.on_device_type_change(self.device.device_type)
                self.fields['model'].set(self.device.model)
                
                self.fields['failure'].set(self.device.failure_type)
                self.fields['observations'].insert("1.0", self.device.observations)
                
                # Cambiar texto del botón
                self.btn_save.configure(text="💾 Actualizar")
                self.btn_save_add.grid_forget()
                
                return True
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el dispositivo: {str(e)}")
        
        return False
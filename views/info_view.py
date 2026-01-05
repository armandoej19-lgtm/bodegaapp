"""
Vista para mostrar la información general de la aplicación
"""

import customtkinter as ctk
import webbrowser

class InfoView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Diccionario para almacenar los frames de cada sección
        self.section_frames = {}
        self.section_states = {}  # Para controlar estado (abierto/cerrado)
        
        # Configurar interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Título principal
        title_label = ctk.CTkLabel(
            self,
            text="📚 Bodega Register App - Documentación",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 30), sticky="n")
        
        # Frame para contenido con scroll
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Contenido de la documentación
        self.create_content()
    
    def create_content(self):
        """Crea el contenido de información con secciones desplegables"""
        current_row = 0
        
        # Sección 1: Información de la Aplicación
        self.create_collapsible_section(
            title="Información de la Aplicación",
            content="""
Versión: 1.0.0
Autor: Armando Esparza
Fecha de Lanzamiento: Enero 2026
Lenguaje: Python 3.12
Framework GUI: CustomTkinter
Base de Datos: SQLite

Descripción:
Bodega Register App es una aplicación de escritorio para gestionar
el inventario de dispositivos tecnológicos. Permite registrar, buscar,
modificar y eliminar dispositivos con información detallada sobre
su estado y ubicación.
""",
            row=current_row
        )
        current_row += 2
        
        # Sección 2: Características Principales
        self.create_collapsible_section(
            title="Características Principales",
            content="""
• Registro completo de dispositivos con número de serie único
• Gestión de múltiples plantas/locaciones
• Clasificación por tipos y modelos de dispositivos
• Control de estados de falla (hardware/software)
• Sistema de búsqueda avanzada por múltiples criterios
• Exportación de datos a formato Excel
• Interfaz moderna e intuitiva
• Base de datos local segura
""",
            row=current_row
        )
        current_row += 2
        
        # Sección 3: Uso Básico
        self.create_collapsible_section(
            title="Uso Básico",
            content="""
1. Pestaña 'Registro':
   - Selecciona la planta donde se encuentra el dispositivo
   - Ingresa el número de serie (único por dispositivo)
   - Selecciona tipo y modelo del dispositivo
   - Especifica si tiene alguna falla
   - Añade observaciones si es necesario

2. Pestaña 'Búsqueda':
   - Busca dispositivos por serial, modelo o tipo
   - Exporta resultados a Excel
   - Modifica o elimina registros

3. Pestaña 'Información':
   - Consulta documentación de la aplicación
   - Accede al repositorio del proyecto
""",
            row=current_row
        )
        current_row += 2
        
        # Sección 4: Enlaces y Recursos
        self.create_collapsible_section(
            title="Enlaces y Recursos",
            content="",
            row=current_row,
            is_special=True  # Esta sección tiene botones especiales
        )
        current_row += 2
        
        # Botón para GitHub (dentro de la sección 4)
        github_button = ctk.CTkButton(
            self.section_frames["Enlaces y Recursos"],
            text="Ver Proyecto en GitHub",
            command=self.open_github,
            width=200,
            height=40,
            fg_color="#24292e",
            hover_color="#444d56"
        )
        github_button.pack(pady=(10, 10))
        
        # Frame para botones adicionales
        button_frame = ctk.CTkFrame(
            self.section_frames["Enlaces y Recursos"], 
            fg_color="transparent"
        )
        button_frame.pack(pady=(0, 10))
        
        # Botón para ver documentación
        docs_button = ctk.CTkButton(
            button_frame,
            text="Documentación Completa",
            command=self.open_documentation,
            width=180,
            height=35
        )
        docs_button.pack(side="left", padx=(0, 10))
        
        # Botón para reportar problemas
        issues_button = ctk.CTkButton(
            button_frame,
            text="Reportar Problema",
            command=self.report_issue,
            width=180,
            height=35,
            fg_color="#d73a49",
            hover_color="#b31d28"
        )
        issues_button.pack(side="left")
        
        # Sección 5: Licencia
        self.create_collapsible_section(
            title="Licencia",
            content="""
Este proyecto está bajo la Licencia MIT.

La Licencia MIT es una licencia de software permisiva que permite
el uso, copia, modificación y distribución del software con muy
pocas restricciones.

Para más información, consulta el archivo LICENSE incluido en el
repositorio del proyecto.
""",
            row=current_row
        )
        current_row += 2
        
        # Sección 6: Contacto
        self.create_collapsible_section(
            title="Contacto",
            content="""
Para consultas, sugerencias o colaboración:

• GitHub: github.com/tuusuario/bodegaapp
• Email: tuemail@example.com

¡Todas las contribuciones son bienvenidas!
""",
            row=current_row
        )
        current_row += 2
        
    
    def create_collapsible_section(self, title, content, row, is_special=False):
        """Crea una sección desplegable"""
        
        # Frame principal para la sección
        section_frame = ctk.CTkFrame(self.scrollable_frame)
        section_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=(5, 0))
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Botón desplegable
        toggle_button = ctk.CTkButton(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
            command=lambda t=title: self.toggle_section(t),
            fg_color="transparent",
            hover_color="#2b2b2b",
            text_color="white"
        )
        toggle_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        # Frame para el contenido (inicialmente oculto)
        content_frame = ctk.CTkFrame(section_frame)
        content_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(20, 0), pady=(5, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Almacenar referencia al frame de contenido
        self.section_frames[title] = content_frame
        self.section_states[title] = False  # Inicialmente cerrado
        content_frame.grid_remove()  # Ocultar al inicio
        
        # Agregar contenido si no es especial
        if not is_special and content:
            content_label = ctk.CTkLabel(
                content_frame,
                text=content,
                font=ctk.CTkFont(size=14),
                justify="left",
                anchor="w"
            )
            content_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
    
    def toggle_section(self, title):
        """Alterna entre mostrar y ocultar una sección"""
        content_frame = self.section_frames[title]
        
        if self.section_states[title]:
            # Si está abierto, cerrarlo
            content_frame.grid_remove()
            self.section_states[title] = False
        else:
            # Si está cerrado, abrirlo
            content_frame.grid()
            self.section_states[title] = True
    
    def open_github(self):
        """Abre el repositorio de GitHub"""
        github_url = "https://github.com/tuusuario/bodegaapp"
        webbrowser.open_new(github_url)
    
    def open_documentation(self):
        """Abre la documentación (puedes personalizar la URL)"""
        docs_url = "https://github.com/tuusuario/bodegaapp/wiki"
        webbrowser.open_new(docs_url)
    
    def report_issue(self):
        """Abre la página para reportar issues"""
        issues_url = "https://github.com/tuusuario/bodegaapp/issues"
        webbrowser.open_new(issues_url)
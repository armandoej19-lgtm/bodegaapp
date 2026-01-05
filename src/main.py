"""
Módulo principal de Bodega-App
"""

from src.app import App

def main():
    """Función principal que inicia la aplicación"""
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
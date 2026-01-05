# 🏭 Bodega Register App

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)

Sistema de gestión de inventario para dispositivos electrónicos con interfaz gráfica moderna.

## ✨ Características

- ✅ Registro de dispositivos con número de serie único
- 🔍 Búsqueda avanzada por múltiples criterios
- 📊 Exportación a Excel con un clic
- 🛡️ Protecciones contra eliminaciones accidentales
- 📁 Gestión de tipos de fallas predefinidas
- 🔄 Sistema de logs para auditoría
- 🎨 Interfaz moderna con CustomTkinter

## 🚀 Instalación Rápida

### Windows (Usuarios finales)
1. Descarga `BodegaApp.exe` de la [última release](https://github.com/armandoej19-lgtm/bodegaapp/releases/latest)
2. Ejecuta el instalador
3. ¡Listo para usar!

### Desarrollo
```bash
# Clonar repositorio
git clone https://github.com/armandoej19-lgtm/bodegaapp.git
cd bodega-app

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python run.py

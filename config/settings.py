# config/settings.py
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Paths
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "bodega.db"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUP_DIR = DATA_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"

# App settings
APP_NAME = "Bodega Register App"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Tu Nombre"

# UI settings
WINDOW_SIZE = "1366x768"
THEME = "dark-blue"  # For customtkinter
FONT_FAMILY = "Segoe UI"

# Database settings
BACKUP_ENABLED = True  # <-- SOLO UNA VEZ
BACKUP_INTERVAL_DAYS = 7

# Export settings
EXPORT_FORMAT = "xlsx"  # xlsx, csv
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

# Logging
LOG_LEVEL = "INFO"
LOG_RETENTION_DAYS = 30

# Backup settings - CORREGIDO: quitar el BACKUP_ENABLED duplicado
BACKUP_INTERVAL_HOURS = 24  # Horas entre backups automáticos
AUTO_BACKUP_ON_START = True  # Verificar backup al iniciar
AUTO_BACKUP_ON_EXIT = True   # Crear backup al cerrar si es necesario
MAX_BACKUP_FILES = 10        # Máximo número de backups a mantener
BACKUP_MIN_DB_SIZE = 1024    # Tamaño mínimo de BD para hacer backup (bytes)

# Ensure directories exist
for directory in [DATA_DIR, EXPORTS_DIR, BACKUP_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)
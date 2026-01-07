"""
Configuration package for Bodega App
"""
from .settings import *
from .device_config import *

__all__ = [
    'APP_NAME', 'APP_VERSION', 'DATABASE_PATH', 'EXPORTS_DIR',
    'WINDOW_SIZE', 'THEME', 'BACKUP_ENABLED',
    'DEVICE_MODELS', 'DEVICE_TYPES', 'FAILURE_TYPES'
]
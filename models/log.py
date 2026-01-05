"""
Modelo de datos para logs de cambios
"""
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class ChangeLog:
    """Clase que representa un log de cambios"""
    log_id: Optional[int] = None
    device_id: int = 0
    action: str = ""
    change_details: str = ""
    change_date: Optional[datetime] = None
    
    def to_dict(self):
        """Convierte el log a diccionario"""
        return {
            'log_id': self.log_id,
            'device_id': self.device_id,
            'action': self.action,
            'change_details': self.change_details,
            'change_date': self.change_date.strftime('%Y-%m-%d %H:%M:%S') if self.change_date else None
        }
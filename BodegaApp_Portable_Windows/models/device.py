"""
Modelo de datos para dispositivos
"""
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Device:
    """Clase que representa un dispositivo en el sistema"""
    id: Optional[int] = None
    plant: str = ""
    serialno: str = ""
    device_type: str = ""
    model: str = ""
    failure_type: str = "[0] Sin fallas"
    observations: str = ""
    entry_date: Optional[datetime] = None
    
    def to_dict(self):
        """Convierte el dispositivo a diccionario"""
        return {
            'id': self.id,
            'plant': self.plant,
            'serialno': self.serialno,
            'type': self.device_type,
            'model': self.model,
            'failuretype': self.failure_type,
            'observations': self.observations,
            'entry_date': self.entry_date.strftime('%Y-%m-%d %H:%M:%S') if self.entry_date else None
        }
    
    @classmethod
    def from_db_row(cls, row):
        """Crea un Device a partir de una fila de base de datos"""
        return cls(
            id=row[0],
            plant = row[1],
            serialno=row[2],
            device_type=row[3],
            model=row[4],
            failure_type=row[5],
            observations=row[6],
            entry_date=datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S') if row[7] else None
        )
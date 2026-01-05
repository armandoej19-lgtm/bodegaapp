"""
Pruebas unitarias para los modelos de datos
"""
import unittest
from datetime import datetime
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from models.device import Device
    from models.log import ChangeLog
    HAS_MODELS = True
except ImportError as e:
    print(f"⚠️  No se pueden importar modelos: {e}")
    HAS_MODELS = False
    Device = None
    ChangeLog = None


@unittest.skipIf(not HAS_MODELS, "Modelos no disponibles")
class TestDeviceModel(unittest.TestCase):
    """Pruebas para el modelo Device"""
    
    def test_device_creation_default(self):
        """Prueba la creación de un dispositivo con valores por defecto"""
        device = Device()
        
        self.assertIsNone(device.id)
        self.assertEqual(device.serialno, "")
        self.assertEqual(device.device_type, "")
        self.assertEqual(device.model, "")
        self.assertEqual(device.failure_type, "[0] Sin fallas")
        self.assertEqual(device.observations, "")
        self.assertIsNone(device.entry_date)
    
    def test_device_creation_with_values(self):
        """Prueba la creación de un dispositivo con valores específicos"""
        test_date = datetime.now()
        device = Device(
            id=1,
            serialno="SN123456",
            device_type="Laptop",
            model="Dell XPS 13",
            failure_type="[1] Falla de Hardware",
            observations="Dispositivo de prueba",
            entry_date=test_date
        )
        
        self.assertEqual(device.id, 1)
        self.assertEqual(device.serialno, "SN123456")
        self.assertEqual(device.device_type, "Laptop")
        self.assertEqual(device.model, "Dell XPS 13")
        self.assertEqual(device.failure_type, "[1] Falla de Hardware")
        self.assertEqual(device.observations, "Dispositivo de prueba")
        self.assertEqual(device.entry_date, test_date)
    
    def test_to_dict_method(self):
        """Prueba la conversión a diccionario"""
        test_date = datetime(2024, 1, 15, 10, 30, 0)
        device = Device(
            id=1,
            serialno="SN123456",
            device_type="Laptop",
            model="Dell XPS",
            failure_type="[0] Sin fallas",
            observations="Test",
            entry_date=test_date
        )
        
        device_dict = device.to_dict()
        
        expected_dict = {
            'id': 1,
            'serialno': 'SN123456',
            'type': 'Laptop',
            'model': 'Dell XPS',
            'failuretype': '[0] Sin fallas',
            'observations': 'Test',
            'entry_date': '2024-01-15 10:30:00'
        }
        
        self.assertEqual(device_dict, expected_dict)
    
    def test_to_dict_without_date(self):
        """Prueba la conversión a diccionario sin fecha"""
        device = Device(
            id=1,
            serialno="SN123456"
        )
        
        device_dict = device.to_dict()
        
        self.assertIsNone(device_dict['entry_date'])
        self.assertEqual(device_dict['id'], 1)
        self.assertEqual(device_dict['serialno'], 'SN123456')
    
    def test_from_db_row(self):
        """Prueba la creación desde una fila de base de datos"""
        # Simular fila de base de datos
        db_row = (
            1,                      # id
            "SN123456",             # serialno
            "Laptop",               # type
            "Dell XPS 13",          # model
            "[1] Falla de Hardware", # failuretype
            "Observaciones",        # observations
            "2024-01-15 10:30:00"   # entry_date
        )
        
        device = Device.from_db_row(db_row)
        
        self.assertEqual(device.id, 1)
        self.assertEqual(device.serialno, "SN123456")
        self.assertEqual(device.device_type, "Laptop")
        self.assertEqual(device.model, "Dell XPS 13")
        self.assertEqual(device.failure_type, "[1] Falla de Hardware")
        self.assertEqual(device.observations, "Observaciones")
        self.assertIsInstance(device.entry_date, datetime)
        self.assertEqual(device.entry_date.year, 2024)
        self.assertEqual(device.entry_date.month, 1)
        self.assertEqual(device.entry_date.day, 15)
    
    def test_from_db_row_invalid_date(self):
        """Prueba la creación con fecha inválida"""
        # Fila con fecha None
        db_row = (
            1, "SN123456", "Laptop", "Model", "[0] Sin fallas", "Obs", None
        )
        
        device = Device.from_db_row(db_row)
        
        self.assertIsNone(device.entry_date)
    
    def test_device_equality(self):
        """Prueba la igualdad entre dispositivos"""
        device1 = Device(id=1, serialno="SN001")
        device2 = Device(id=1, serialno="SN001")
        device3 = Device(id=2, serialno="SN002")
        
        # Usar __dict__ para comparar, ya que dataclass no sobrescribe __eq__
        self.assertEqual(device1.__dict__, device2.__dict__)
        self.assertNotEqual(device1.__dict__, device3.__dict__)
    
    def test_device_string_representation(self):
        """Prueba la representación en string del dispositivo"""
        device = Device(id=1, serialno="SN123456", model="Dell XPS")
        
        # Verificar que __repr__ funciona (generado por dataclass)
        repr_str = repr(device)
        self.assertIn("Device", repr_str)
        self.assertIn("id=1", repr_str)
        self.assertIn("serialno='SN123456'", repr_str)
        self.assertIn("model='Dell XPS'", repr_str)


@unittest.skipIf(not HAS_MODELS, "Modelos no disponibles")
class TestChangeLogModel(unittest.TestCase):
    """Pruebas para el modelo ChangeLog"""
    
    def test_changelog_creation_default(self):
        """Prueba la creación de un log con valores por defecto"""
        log = ChangeLog()
        
        self.assertIsNone(log.log_id)
        self.assertEqual(log.device_id, 0)
        self.assertEqual(log.action, "")
        self.assertEqual(log.change_details, "")
        self.assertIsNone(log.change_date)
    
    def test_changelog_creation_with_values(self):
        """Prueba la creación de un log con valores específicos"""
        test_date = datetime.now()
        log = ChangeLog(
            log_id=1,
            device_id=123,
            action="INSERT",
            change_details="Dispositivo agregado",
            change_date=test_date
        )
        
        self.assertEqual(log.log_id, 1)
        self.assertEqual(log.device_id, 123)
        self.assertEqual(log.action, "INSERT")
        self.assertEqual(log.change_details, "Dispositivo agregado")
        self.assertEqual(log.change_date, test_date)
    
    def test_to_dict_method(self):
        """Prueba la conversión a diccionario"""
        test_date = datetime(2024, 1, 15, 10, 30, 0)
        log = ChangeLog(
            log_id=1,
            device_id=123,
            action="UPDATE",
            change_details="Modelo actualizado",
            change_date=test_date
        )
        
        log_dict = log.to_dict()
        
        expected_dict = {
            'log_id': 1,
            'device_id': 123,
            'action': 'UPDATE',
            'change_details': 'Modelo actualizado',
            'change_date': '2024-01-15 10:30:00'
        }
        
        self.assertEqual(log_dict, expected_dict)
    
    def test_changelog_string_representation(self):
        """Prueba la representación en string del log"""
        log = ChangeLog(
            log_id=1,
            device_id=123,
            action="DELETE"
        )
        
        repr_str = repr(log)
        self.assertIn("ChangeLog", repr_str)
        self.assertIn("log_id=1", repr_str)
        self.assertIn("device_id=123", repr_str)
        self.assertIn("action='DELETE'", repr_str)


class TestModelsIntegration(unittest.TestCase):
    """Pruebas de integración entre modelos"""
    
    @unittest.skipIf(not HAS_MODELS, "Modelos no disponibles")
    def test_device_and_log_relationship(self):
        """Prueba la relación conceptual entre Device y ChangeLog"""
        # Crear un dispositivo
        device = Device(
            id=1,
            serialno="SN123456",
            device_type="Laptop"
        )
        
        # Crear un log relacionado con el dispositivo
        log = ChangeLog(
            device_id=device.id,
            action="CREATE",
            change_details=f"Dispositivo {device.serialno} creado"
        )
        
        # Verificar la relación
        self.assertEqual(log.device_id, device.id)
        self.assertIn(device.serialno, log.change_details)
    
    @unittest.skipIf(not HAS_MODELS, "Modelos no disponibles")
    def test_serialization_deserialization_cycle(self):
        """Prueba el ciclo completo de serialización/deserialización"""
        # Crear dispositivo original
        original_device = Device(
            id=1,
            serialno="SN987654",
            device_type="Tablet",
            model="iPad Pro",
            failure_type="[0] Sin fallas",
            observations="Nuevo en caja"
        )
        
        # Convertir a diccionario
        device_dict = original_device.to_dict()
        
        # Crear nuevo dispositivo desde diccionario (simulado)
        # Nota: Esto no es una funcionalidad real, solo para demostración
        restored_device = Device(
            id=device_dict['id'],
            serialno=device_dict['serialno'],
            device_type=device_dict['type'],
            model=device_dict['model'],
            failure_type=device_dict['failuretype'],
            observations=device_dict['observations']
        )
        
        # Verificar que los datos se preservaron
        self.assertEqual(original_device.serialno, restored_device.serialno)
        self.assertEqual(original_device.device_type, restored_device.device_type)
        self.assertEqual(original_device.model, restored_device.model)


if __name__ == '__main__':
    # Ejecutar pruebas con mayor detalle
    unittest.main(verbosity=2, failfast=False)
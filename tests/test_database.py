"""
Pruebas unitarias para el módulo de base de datos
"""
import unittest
import os
import tempfile
from src.database import Database
from models.device import Device


class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear base de datos temporal
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.db = Database(db_name=self.db_path)
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        self.db.close()
        os.unlink(self.db_path)
    
    def test_create_tables(self):
        """Prueba que las tablas se crean correctamente"""
        # Verificar que la tabla DeviceReg existe
        self.db.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DeviceReg'")
        result = self.db.cur.fetchone()
        self.assertIsNotNone(result)
        
        # Verificar que la tabla ChangeLogs existe
        self.db.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ChangeLogs'")
        result = self.db.cur.fetchone()
        self.assertIsNotNone(result)
    
    def test_add_device(self):
        """Prueba agregar un dispositivo"""
        device_id = self.db.add_device(
            serialno="TEST123",
            device_type="Laptop",
            model="Dell XPS 13",
            failuretype="[0] Sin fallas",
            observations="Dispositivo de prueba"
        )
        
        self.assertIsNotNone(device_id)
        
        # Verificar que se insertó
        self.db.cur.execute("SELECT * FROM DeviceReg WHERE id = ?", (device_id,))
        result = self.db.cur.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "TEST123")
    
    def test_search_device(self):
        """Prueba búsqueda de dispositivos"""
        # Agregar dispositivo de prueba
        self.db.add_device(
            serialno="SEARCH001",
            device_type="Desktop",
            model="Dell OptiPlex",
            failuretype="[1] Falla de Hardware",
            observations="Para búsqueda"
        )
        
        # Buscar por serial
        results = self.db.search_device("SEARCH001", "serialno")
        self.assertEqual(len(results), 1)
        
        # Buscar por tipo
        results = self.db.search_device("Desktop", "type")
        self.assertGreaterEqual(len(results), 1)
    
    def test_delete_device(self):
        """Prueba eliminación de dispositivos"""
        # Agregar dispositivo
        device_id = self.db.add_device(
            serialno="DELETE001",
            device_type="Tablet",
            model="iPad",
            failuretype="[0] Sin fallas",
            observations="Para eliminar"
        )
        
        # Eliminar
        deleted = self.db.del_SData("DELETE001", "serialno")
        self.assertEqual(deleted, 1)


if __name__ == '__main__':
    unittest.main()
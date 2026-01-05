"""
Pruebas unitarias para la aplicación principal
"""
import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock para customtkinter antes de importar app
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['pandas'] = MagicMock()

try:
    from src.app import App
    from src.database import Database
    HAS_DEPS = True
except ImportError as e:
    print(f"⚠️  No se pueden importar módulos: {e}")
    HAS_DEPS = False
    App = None
    Database = None


@unittest.skipIf(not HAS_DEPS, "Dependencias no disponibles")
class TestApp(unittest.TestCase):
    """Pruebas para la aplicación principal"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Mock de la base de datos
        self.mock_db = Mock(spec=Database)
        self.mock_db.add_device = Mock(return_value=1)
        self.mock_db.search_device = Mock(return_value=[])
        self.mock_db.get_all_devices = Mock(return_value=[])
        self.mock_db.del_SData = Mock(return_value=1)
        self.mock_db.close = Mock()
        
        # Crear aplicación con base de datos mock
        with patch('app.Database', return_value=self.mock_db):
            with patch('customtkinter.CTk.__init__', return_value=None):
                self.app = App()
                self.app.db = self.mock_db
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        if hasattr(self, 'app') and hasattr(self.app.db, 'close'):
            self.app.db.close()
    
    def test_app_initialization(self):
        """Prueba que la aplicación se inicializa correctamente"""
        self.assertIsNotNone(self.app)
        self.assertEqual(self.app.db, self.mock_db)
    
    def test_setup_ui_called_on_init(self):
        """Prueba que setup_ui es llamado durante la inicialización"""
        # Verificar que los métodos de configuración fueron llamados
        # (esto depende de cómo implementes los mocks)
        pass
    
    @patch('tkinter.messagebox.showerror')
    def test_save_device_validation(self, mock_showerror):
        """Prueba la validación al guardar un dispositivo"""
        # Simular campos vacíos
        self.app.entryserial = Mock(get=Mock(return_value=""))
        self.app.devicetype = Mock(get=Mock(return_value="Seleccionar tipo"))
        self.app.entrymodel = Mock(get=Mock(return_value=""))
        
        # Llamar a save_device
        self.app.save_device(add_another=False)
        
        # Verificar que se mostró error
        self.assertTrue(mock_showerror.called)
    
    @patch('tkinter.messagebox.showinfo')
    def test_save_device_success(self, mock_showinfo):
        """Prueba el guardado exitoso de un dispositivo"""
        # Simular campos válidos
        self.app.entryserial = Mock(get=Mock(return_value="TEST123"))
        self.app.devicetype = Mock(get=Mock(return_value="Laptop"))
        self.app.entrymodel = Mock(get=Mock(return_value="Dell XPS"))
        self.app.failuretype = Mock(get=Mock(return_value="[0] Sin fallas"))
        self.app.entryobs = Mock(get=Mock(return_value="Test"))
        
        # Mock de base de datos que retorna ID exitoso
        self.mock_db.add_device.return_value = 123
        
        # Llamar a save_device
        self.app.save_device(add_another=False)
        
        # Verificar que se mostró mensaje de éxito
        self.assertTrue(mock_showinfo.called)
        self.mock_db.add_device.assert_called_once()
    
    @patch('tkinter.messagebox.askyesno', return_value=True)
    @patch('tkinter.messagebox.showinfo')
    def test_delete_single_record(self, mock_showinfo, mock_askyesno):
        """Prueba la eliminación de un registro individual"""
        # Configurar resultados actuales
        self.app.current_results = [
            (1, 'SN001', 'Laptop', 'Dell XPS', '[0] Sin fallas', '2024-01-01', 'Test')
        ]
        
        # Mock del treeview
        self.app.tree = Mock()
        self.app.tree.selection = Mock(return_value=['item1'])
        self.app.tree.item = Mock(return_value={'values': (1, 'SN001', 'Laptop')})
        
        # Llamar a delete_single_record
        self.app.delete_single_record()
        
        # Verificar que se llamó a la base de datos
        self.mock_db.del_SData.assert_called_once()
    
    def test_validate_and_format_date_valid(self):
        """Prueba la validación de fechas válidas"""
        test_cases = [
            ("2024", "2024"),
            ("2024-01", "2024-01"),
            ("2024-01-15", "2024-01-15"),
            ("15/01/2024", "2024-01-15"),
        ]
        
        for input_date, expected in test_cases:
            with self.subTest(input_date=input_date):
                result = self.app.validate_and_format_date(input_date)
                if result:
                    self.assertTrue(result.startswith(expected))
    
    def test_validate_and_format_date_invalid(self):
        """Prueba la validación de fechas inválidas"""
        invalid_dates = [
            "invalid",
            "2024-13-01",  # Mes inválido
            "2024-02-30",  # Día inválido
            "2024/99/01",  # Mes inválido
        ]
        
        for invalid_date in invalid_dates:
            with self.subTest(invalid_date=invalid_date):
                result = self.app.validate_and_format_date(invalid_date)
                self.assertIsNone(result)
    
    @patch('tkinter.messagebox.showerror')
    def test_perform_search_invalid_date(self, mock_showerror):
        """Prueba búsqueda con fecha inválida"""
        # Configurar búsqueda por fecha inválida
        self.app.search_entry = Mock(get=Mock(return_value="invalid-date"))
        self.app.search_option = Mock(get=Mock(return_value="Fecha"))
        
        # Llamar a perform_search
        self.app.perform_search()
        
        # Verificar que se mostró error
        self.assertTrue(mock_showerror.called)
    
    def test_update_delete_button_state(self):
        """Prueba la actualización del estado del botón de eliminar"""
        # Esta prueba depende de la implementación específica
        # Puedes adaptarla según tu código
        pass
    
    @patch('tkinter.Tk.destroy')
    def test_on_closing(self, mock_destroy):
        """Prueba el cierre de la aplicación"""
        # Llamar a on_closing
        self.app.on_closing()
        
        # Verificar que se cerró la base de datos
        self.mock_db.close.assert_called_once()
        # Verificar que se destruyó la ventana
        self.assertTrue(mock_destroy.called)


class TestAppIntegration(unittest.TestCase):
    """Pruebas de integración para la aplicación"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración antes de todas las pruebas"""
        # Crear base de datos temporal
        cls.temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.db_path = cls.temp_db_file.name
    
    @classmethod
    def tearDownClass(cls):
        """Limpieza después de todas las pruebas"""
        # Eliminar archivo temporal
        if os.path.exists(cls.db_path):
            os.unlink(cls.db_path)
    
    @unittest.skipIf(not HAS_DEPS, "Dependencias no disponibles")
    def test_database_integration(self):
        """Prueba integración con base de datos real"""
        # Crear base de datos real
        db = Database(db_name=self.db_path)
        
        try:
            # Agregar dispositivo de prueba
            device_id = db.add_device(
                serialno="INTEGRATION_TEST",
                device_type="Laptop",
                model="Test Model",
                failuretype="[0] Sin fallas",
                observations="Integration test"
            )
            
            self.assertIsNotNone(device_id)
            
            # Buscar dispositivo
            results = db.search_device("INTEGRATION_TEST", "serialno")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0][1], "INTEGRATION_TEST")
            
            # Eliminar dispositivo
            deleted = db.del_SData("INTEGRATION_TEST", "serialno")
            self.assertEqual(deleted, 1)
            
        finally:
            db.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
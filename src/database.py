# src/database.py
import sqlite3 as sql
import os
from datetime import datetime


class Database:
    def __init__(self, db_name='bodega.db'):
        # Asegurar que la base de datos esté en el directorio data/
        self.db_name = os.path.join('data', db_name)
        self.conn = None
        self.cur = None
        self._connect()
        self.create_tables()
    
    def _connect(self):
        """Establece conexión a la base de datos"""
        try:
            # Crear directorio data si no existe
            os.makedirs('data', exist_ok=True)
            
            self.conn = sql.connect(self.db_name)
            self.cur = self.conn.cursor()
            print(f"✅ Conectado a: {self.db_name}")
        except sql.Error as e:
            print(f'❌ Error al conectar: {e}')
            raise
    
    def create_tables(self):
        """Crea todas las tablas necesarias"""
        try:
            # Tabla principal de dispositivos - AÑADIDA COLUMNA plant
            self.cur.execute('''CREATE TABLE IF NOT EXISTS DeviceReg (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                plant TEXT,
                serialno TEXT UNIQUE,
                type VARCHAR(60), 
                model TEXT, 
                failuretype VARCHAR(60), 
                entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observations TEXT)
                ''')
            
            # Tabla de logs para cambios
            self.cur.execute('''CREATE TABLE IF NOT EXISTS ChangeLogs (
                log_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                action TEXT,
                change_details TEXT,
                change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES DeviceReg(id))''')
            
            self.conn.commit()
            print("✅ Tablas creadas/verificadas")
        except sql.Error as e:
            print(f'❌ Error creando tablas: {e}')
            if self.conn:
                self.conn.rollback()
    
    def add_device(self, plant, serialno, device_type, model, failuretype, observations):
        """Añade un dispositivo y registra en logs"""
        try:
            # Insertar dispositivo - AGREGADO plant
            self.cur.execute('''INSERT INTO DeviceReg 
                              (plant, serialno, type, model, failuretype, observations) 
                              VALUES (?, ?, ?, ?, ?, ?)''',
                              (plant, serialno, device_type, model, failuretype, observations))
            device_id = self.cur.lastrowid
            
            # Registrar en logs
            self.cur.execute('''INSERT INTO ChangeLogs 
                              (device_id, action, change_details) 
                              VALUES (?, ?, ?)''',
                              (device_id, 'INSERT', 
                               f'Dispositivo {serialno} ({model}) de planta {plant} agregado'))
            
            self.conn.commit()
            print(f"✅ Dispositivo agregado: {serialno} (ID: {device_id})")
            return device_id
        except sql.IntegrityError:
            print(f'❌ Error: Serial {serialno} ya existe')
            if self.conn:
                self.conn.rollback()
            return None
        except sql.Error as e:
            print(f'❌ Error: {e}')
            if self.conn:
                self.conn.rollback()
            return None
    
    def del_SData(self, search_term, search_by="serialno", exact_match=False):
        """Elimina datos según criterio de búsqueda"""
        try:
            if search_by == "serialno":
                if exact_match:
                    self.cur.execute('DELETE FROM DeviceReg WHERE serialno = ?', (search_term,))
                else:
                    self.cur.execute('DELETE FROM DeviceReg WHERE serialno LIKE ?', 
                                (f'%{search_term}%',))
            elif search_by == "model":
                if exact_match:
                    self.cur.execute('DELETE FROM DeviceReg WHERE model = ?', (search_term,))
                else:
                    self.cur.execute('DELETE FROM DeviceReg WHERE model LIKE ?', 
                                (f'%{search_term}%',))
            elif search_by == "type":
                if exact_match:
                    self.cur.execute('DELETE FROM DeviceReg WHERE type = ?', (search_term,))
                else:
                    self.cur.execute('DELETE FROM DeviceReg WHERE type LIKE ?', 
                                (f'%{search_term}%',))
            elif search_by == "plant":
                if exact_match:
                    self.cur.execute('DELETE FROM DeviceReg WHERE plant = ?', (search_term,))
                else:
                    self.cur.execute('DELETE FROM DeviceReg WHERE plant LIKE ?', 
                                (f'%{search_term}%',))
            elif search_by == "entry_date":
                self.cur.execute('DELETE FROM DeviceReg WHERE entry_date = ?', 
                            (search_term,))
            else:
                self.cur.execute('DELETE FROM DeviceReg WHERE serialno LIKE ? OR model LIKE ? OR plant LIKE ?', 
                            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            deleted_count = self.cur.rowcount
            self.conn.commit()
            print(f"✅ Eliminados {deleted_count} registros")
            return deleted_count
        except Exception as e:
            print(f'❌ Error al eliminar información: {e}')
            if self.conn:
                self.conn.rollback()
            return 0

    def search_device(self, search_term, search_by="serialno"):
        """Busca dispositivos por criterio"""
        try:
            if search_by == "serialno":
                self.cur.execute('SELECT * FROM DeviceReg WHERE serialno LIKE ?', 
                            (f'%{search_term}%',))
            elif search_by == "type":
                self.cur.execute('SELECT * FROM DeviceReg WHERE type LIKE ?', 
                            (f'%{search_term}%',))
            elif search_by == "model":
                self.cur.execute('SELECT * FROM DeviceReg WHERE model LIKE ?', 
                            (f'%{search_term}%',))
            elif search_by == "plant":
                self.cur.execute('SELECT * FROM DeviceReg WHERE plant LIKE ?', 
                            (f'%{search_term}%',))
            elif search_by == "entry_date":
                self.cur.execute('SELECT * FROM DeviceReg WHERE entry_date LIKE ?', 
                            (f'{search_term}%',))
            else:
                self.cur.execute('SELECT * FROM DeviceReg WHERE serialno LIKE ? OR type LIKE ? OR model LIKE ? OR plant LIKE ?', 
                            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            results = self.cur.fetchall()
            print(f"✅ Búsqueda encontrada: {len(results)} resultados")
            return results
        except sql.Error as e:
            print(f'❌ Error en búsqueda: {e}')
            return []
                
    def get_all_devices(self):
        """Obtiene todos los dispositivos"""
        try:
            self.cur.execute('SELECT * FROM DeviceReg ORDER BY entry_date DESC')
            results = self.cur.fetchall()
            print(f"✅ Total dispositivos: {len(results)}")
            return results
        except sql.Error as e:
            print(f'❌ Error en consulta: {e}')
            return []
    
    def close(self):
        """Cierra la conexión de forma segura"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cur = None
            print("✅ Conexión a base de datos cerrada")
    
    def __enter__(self):
        """Para usar con 'with' statement"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Se ejecuta automáticamente al salir del bloque 'with'"""
        self.close()
"""
Utility functions for Bodega App
"""
import re
from datetime import datetime
from typing import Optional, Tuple, List, Any
import pandas as pd


def validate_serial_number(serial: str) -> Tuple[bool, str]:
    """Validates a serial number"""
    if not serial or len(serial.strip()) < 3:
        return False, "Serial number must be at least 3 characters"
    
    # Alphanumeric, hyphens, underscores allowed
    if not re.match(r'^[A-Za-z0-9\-_]+$', serial):
        return False, "Invalid characters in serial number"
    
    return True, "Valid serial number"


def format_date_for_display(date_str: str, include_time: bool = True) -> str:
    """Formats a date string for display"""
    if not date_str:
        return ""
    
    try:
        # Try different formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y'
        ]
        
        dt = None
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if not dt:
            return date_str
        
        if include_time:
            return dt.strftime('%d/%m/%Y %H:%M')
        else:
            return dt.strftime('%d/%m/%Y')
            
    except Exception:
        return date_str


def safe_int(value: Any, default: int = 0) -> int:
    """Safely converts any value to integer"""
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def parse_search_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """Parses and validates a date for search operations"""
    date_str = date_str.strip()
    
    if not date_str:
        return False, None
    
    # Try different date formats
    formats = [
        ('%Y-%m-%d', True),      # 2024-01-15
        ('%Y/%m/%d', True),      # 2024/01/15
        ('%d-%m-%Y', True),      # 15-01-2024
        ('%d/%m/%Y', True),      # 15/01/2024
        ('%Y-%m', False),        # 2024-01
        ('%Y/%m', False),        # 2024/01
        ('%m-%Y', False),        # 01-2024
        ('%m/%Y', False),        # 01/2024
        ('%Y', False),           # 2024
    ]
    
    for fmt, has_day in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            
            # Format for SQLite LIKE query
            if not has_day:
                if fmt == '%Y':
                    return True, f"{dt.year}%"
                else:
                    return True, f"{dt.year}-{dt.month:02d}%"
            else:
                return True, f"{dt.year}-{dt.month:02d}-{dt.day:02d}%"
                
        except ValueError:
            continue
    
    return False, None


def is_valid_date(year: int, month: int, day: Optional[int] = None) -> bool:
    """Checks if a date is valid"""
    try:
        if not (1900 <= year <= 2100):
            return False
        if not (1 <= month <= 12):
            return False
        
        if day is not None:
            # Days in month
            if month == 2:
                # February
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                    days_in_month = 29
                else:
                    days_in_month = 28
            elif month in [4, 6, 9, 11]:
                days_in_month = 30
            else:
                days_in_month = 31
            
            if not (1 <= day <= days_in_month):
                return False
        
        return True
    except:
        return False


def extract_failure_code(failure_type: str) -> str:
    """Extracts the numeric code from failure type string"""
    try:
        if failure_type.startswith("[") and "]" in failure_type:
            return failure_type.split("[")[1].split("]")[0]
    except:
        pass
    return "0"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncates text to specified length, adds ellipsis if needed"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def validate_device_inputs(serial: str, device_type: str, model: str) -> List[str]:
    """Validates device input fields, returns list of errors"""
    errors = []
    
    if not serial or len(serial.strip()) < 3:
        errors.append("El número de serie es obligatorio (mínimo 3 caracteres)")
    
    if not device_type or device_type in ["Seleccionar tipo", ""]:
        errors.append("Selecciona un tipo de dispositivo")
    
    if not model or model in ["Selecciona primero el tipo", "Selecciona un modelo", ""]:
        errors.append("Selecciona o ingresa un modelo")
    
    return errors


def get_safe_value(row: tuple, index: int, default: Any = "") -> Any:
    """Safely gets a value from a tuple/row, handles IndexError"""
    try:
        value = row[index]
        return value if value is not None else default
    except IndexError:
        return default


def export_to_excel(data: List, columns: List[str], filepath: str) -> Tuple[bool, str]:
    """Exports data to Excel file"""
    try:
        if not data:
            return False, "No hay datos para exportar"
        
        df = pd.DataFrame(data, columns=columns)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos')
        
        return True, f"Datos exportados exitosamente a {filepath}"
        
    except PermissionError:
        return False, "Error de permisos. ¿El archivo está abierto en otro programa?"
    except Exception as e:
        return False, f"Error al exportar: {str(e)}"


def generate_filename(prefix: str = "export", extension: str = "xlsx") -> str:
    """Generates a filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass
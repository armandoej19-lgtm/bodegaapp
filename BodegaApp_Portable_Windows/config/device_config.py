"""
Device configuration for Bodega App
"""

PLANT = {   
    "UP01" : "PLANTA 1",
    "UP02" : "PLANTA 2A",
    "UP03" : "PLANTA 2B",
    "UP04" : "PLANTA 3",
    "UP05" : "PLANTA 1C",
    "UP06" : "PLANTA 1D"    
}

PLANT_VAL = list(PLANT.values())

DEVICE_MODELS = {
    "Laptop": [
        
    ],
    "Desktop": [
        
    ],
    "Tablet": [
        
    ],
    "Teléfono Inteligente": [
        
    ],
    "Server": [
        
    ],
    "Switch": [
        
    ],
    "Punto de Acceso": [
        
    ],
    "Impresora": [
        
    ],
    "Camara": [
        
    ],
    "Altavoz": [
        
    ],
    "Monitor": [
        
    ],
    "Other": [
        "Otro modelo"
    ]
}

DEVICE_TYPES = list(DEVICE_MODELS.keys())

FAILURE_TYPES = [
    "[0] Sin fallas", 
    "[1] Falla de Hardware", 
    "[2] Falla Crítica de Hardware",
    "[3] Falla de Software", 
    "[4] Falla Crítica de Software"
]

# Failure type descriptions
FAILURE_DESCRIPTIONS = {
    "0": "Sin fallas - Dispositivo en perfecto estado",
    "1": "Falla de Hardware - Problema físico menor",
    "2": "Falla Crítica de Hardware - Problema físico grave",
    "3": "Falla de Software - Problema de sistema/software",
    "4": "Falla Crítica de Software - Sistema inoperable"
}
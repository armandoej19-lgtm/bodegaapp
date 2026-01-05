import requests
import json
from config.settings import APP_VERSION

def check_for_updates():
    """Verifica si hay actualizaciones disponibles"""
    try:
        # URL de tu API o GitHub releases
        response = requests.get(
            "https://api.github.com/repos/tuusuario/bodega-app/releases/latest",
            timeout=5
        )
        
        if response.status_code == 200:
            latest_version = response.json()["tag_name"]
            if latest_version != APP_VERSION:
                return {
                    "update_available": True,
                    "latest_version": latest_version,
                    "current_version": APP_VERSION,
                    "release_url": response.json()["html_url"]
                }
        
        return {"update_available": False}
        
    except requests.RequestException:
        return {"update_available": False, "error": "No se pudo verificar"}
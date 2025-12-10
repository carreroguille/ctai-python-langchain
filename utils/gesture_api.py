
import logging
import requests
from typing import Union, Dict

logger = logging.getLogger(__name__)

def search_referee_gesture(action: str) -> Union[Dict, str]:
    API_URL = "http://127.0.0.1:8001/api/gesture/"

    normalized_action = action.lower().replace(" ", "_").strip()
        
    MAPPING = {
        "dos_minutos": ["exclusion", "dos minutos"],
        "juego_pasivo": ["pasivo", "juego pasivo"],
    }
        
    target_key = None
        
    logger.info(f"Buscando gesto para: {normalized_action}")
    
    for key, synonyms in MAPPING.items():
        if key == normalized_action or any(s in normalized_action for s in synonyms):
            target_key = key
            break 
    
    if target_key:
        logger.info(f"Gesto encontrado: {target_key}") 

        try:
            response = requests.get(f"{API_URL}{target_key}", timeout=3)
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 404:
                logger.info(f"Gesto no encontrado (404): {target_key}")
                return "El gesto solicitado no está disponible en la base de datos."

            else:
                logger.info(f"Error al acceder a la API de gestos (status code): {response.status_code}")
                return "La información visual del gesto no pudo ser recuperada en este momento."
        
        except requests.exceptions.Timeout:
            logger.error("Timeout conectando a la API de gestos")
            return "El servicio de imágenes de gestos está tardando demasiado, por favor intenta de nuevo." 
        
        except Exception as e:
            logger.error(f"Error al acceder a la API de gestos: {str(e)}")
            return "Información del gesto no disponible temporalmente." 
    else:
        logger.info(f"Gesto no encontrado: {normalized_action}")
        return "No se encontró un gesto arbitral específico para esa descripción en la base de datos."

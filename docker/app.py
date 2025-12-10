from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI()

GESTURE_DB = {
    "dos_minutos": {
        "description": "La gestoforma de exclusión de dos minutos en balonmano se realiza cuando el árbitro señala con un brazo extendido al jugador sancionado y, simultáneamente, levanta el otro brazo en vertical mostrando dos dedos extendidos hacia arriba, indicando de forma clara que ese jugador debe abandonar el terreno de juego durante dos minutos.",
        "url": "https://drive.google.com/file/d/12bYVRVGg7YHgA2b1vF0lVqwwTOUpwxRn/view?usp=sharing"
    },
    "juego_pasivo": {
        "description": "La gestoforma de juego pasivo en balonmano se realiza cuando el árbitro levanta uno de sus brazos en vertical con la palma de la mano abierta y orientada hacia adelante, manteniéndolo extendido por encima de la cabeza.",
        "url": "https://drive.google.com/file/d/1J7zlqqMY7xWnkzuxnzfSIGHeGalp6m5P/view?usp=sharing"
    },
    "saque_porteria": {
        "description": "La gestoforma de saque de portería en balonmano se realiza cuando el árbitro extiende un brazo en dirección a la portería del equipo que va a sacar, con la mano abierta y la palma orientada hacia esa portería, indicando que la reanudación del juego corresponde al portero de ese equipo.",
        "url": "https://drive.google.com/file/d/1vUzr0kDF1pIq92-xzPsZVp6B1RorTIRC/view?usp=sharing"
    },
}

@app.get("/api/gesture/{action_key}")
def get_gesture(action_key: str):
    """Consulta el gesto por su clave normalizada."""
    
    # Intenta obtener el gesto por la clave proporcionada
    gesture = GESTURE_DB.get(action_key.lower())
    
    if gesture:
        return {
            "status": "success",
            "gesture": gesture
        }
    else:
        return {
            "status": "not_found",
            "message": f"Gesto no encontrado para la clave: {action_key}"
        }

# Punto de montaje para Uvicorn (el servidor ASGI)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
Script de prueba para validar el sistema RAG de asistente de balonmano.
Prueba la inicialización, herramientas y conversación interactiva.
"""

import logging
from rag.retriever import Retriever
from agents.ai_agent import AIAgent

# Configurar logging para ver el razonamiento del agente
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("\n" + "="*70)
    print("ASISTENTE DE REGLAMENTACION DE BALONMANO - MODO PRUEBA")
    print("="*70)
    
    print("\n[SISTEMA] Inicializando sistema...")
    
    try:
        # Crear retriever
        print("   -> Creando Retriever...")
        retriever = Retriever()
        
        # Crear agente
        print("   -> Creando AIAgent...")
        agent = AIAgent(
            retriever=retriever,
            model_name="openai/gpt-4o-mini",  # Modelo económico para pruebas
            temperature=0.5,  # Más determinista para RAG
            use_memory=True
        )
        
        print("[OK] Sistema iniciado correctamente\n")
        
    except Exception as e:
        print(f"[ERROR] Error al inicializar el sistema: {e}")
        return
    
    # ==================== PRUEBAS AUTOMÁTICAS ====================
    print("\n" + "="*70)
    print("[TEST] EJECUTANDO PRUEBAS AUTOMÁTICAS")
    print("="*70)
    
    test_queries = [
        ("Saludo", "Hola, ¿qué tal?"),
        ("Estadísticas", "¿Cuántos documentos tienes indexados?"),
        ("Capacidades", "¿Qué puedes hacer?"),
    ]
    
    for i, (name, query) in enumerate(test_queries, 1):
        print(f"\n{'-'*70}")
        print(f"PRUEBA {i}: {name}")
        print(f"{'-'*70}")
        print(f"[Usuario]: {query}")
        print(f"[Asistente]: ", end="", flush=True)
        
        try:
            response = agent.process_message(query)
            print(response)
        except Exception as e:
            print(f"[ERROR]: {e}")
    
    # ==================== MODO INTERACTIVO ====================
    print("\n" + "="*70)
    print("[CHAT] MODO INTERACTIVO")
    print("="*70)
    print("Escribe tus preguntas y el asistente responderá.")
    print("Comandos especiales:")
    print("  - 'salir' / 'exit' : Terminar la sesión")
    print("  - 'limpiar' / 'reset' : Limpiar memoria conversacional")
    print("  - 'historial' : Ver historial de la conversación")
    print("="*70 + "\n")
    
    while True:
        try:
            user_input = input("[Tu]: ").strip()
            
            if not user_input:
                continue
            
            # Comandos especiales
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("\n[SISTEMA] ¡Hasta luego!")
                break
            
            if user_input.lower() in ['limpiar', 'reset']:
                agent.reset_memory()
                print("[SISTEMA] Memoria limpiada\n")
                continue
            
            if user_input.lower() == 'historial':
                history = agent.get_conversation_history()
                if history:
                    print("\n[HISTORIAL] Conversación:")
                    for msg in history:
                        role = "Usuario" if hasattr(msg, 'type') and msg.type == "human" else "Asistente"
                        print(f"  {role}: {msg.content[:100]}...")
                else:
                    print("[HISTORIAL] No hay historial\n")
                continue
            
            # Procesar mensaje normal
            print("[Asistente]: ", end="", flush=True)
            response = agent.process_message(user_input)
            print(response + "\n")
            
        except KeyboardInterrupt:
            print("\n\n[SISTEMA] Sesión interrumpida. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"[ERROR]: {e}\n")

if __name__ == "__main__":
    main()

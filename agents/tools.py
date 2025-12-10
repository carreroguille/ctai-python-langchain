from typing import Optional, Dict, Any
import logging
from pathlib import Path
import requests

from langchain.tools import Tool

from rag.retriever import Retriever
from utils.gesture_api import search_referee_gesture

logger = logging.getLogger(__name__)


# ==================== FUNCIONES DE LAS HERRAMIENTAS ====================
class RAGTools:
    """
    Clase que encapsula todas las herramientas relacionadas con RAG.
    """
    
    def __init__(self, retriever: Retriever):
        """
        Inicializa las herramientas con un retriever.
        
        Args:
            retriever: Instancia del Retriever para interactuar con el vectorstore
        """
        self.retriever = retriever
        logger.info("RAGTools inicializado correctamente")
    
    def search_documents(self, query: str) -> str:
        """
        Busca informacion relevante en los documentos indexados.
        
        Args:
            query: Pregunta o consulta del usuario
        Returns:
            Contexto consolidado con la informacion encontrada
        """
        try:
            logger.info(f"Buscando: '{query}'")
            
            context = self.retriever.build_context(
                query=query,
                n_results=3,
                include_metadata=True  
            )
            
            if not context:
                return "No se encontro informacion relevante en los documentos indexados."
            
            return context
            
        except Exception as e:
            logger.error(f"Error en busqueda: {e}")
            return "Error al buscar en los documentos indexados"
    
    def get_stats(self, tool_input: str = "") -> str:
        """
        Obtiene estadisticas del indice vectorial.
        
        Args:
            tool_input: Input opcional
        
        Returns:
            Informacion sobre el estado del sistema
        """
        try:
            stats = self.retriever.stats()
            
            # Format the list of documents
            docs_list = stats.get('indexed_documents', [])
            if docs_list:
                docs_formatted = "\n            - ".join(docs_list)
                docs_section = f"Documentos indexados:\n            - {docs_formatted}"
            else:
                docs_section = "No hay documentos indexados"
            
            return f"""[STATS] Estadisticas del sistema:
            - Total de chunks: {stats['total_documents']}
            - {docs_section}
            """
            
        except Exception as e:
            logger.error(f"Error obteniendo estadisticas: {e}")
            return "Error al obtener estadisticas del sistema"
    
    def generate_incident_report(self, event_description: str) -> str:
        """
        Genera un borrador de acta o informe formal/tecnico basado en una descripcion de un evento.
        Utiliza el contexto RAG para incluir citas normativas relevantes.
        
        Args:
            event_description: Descripcion del evento o incidencia
            
        Returns:
            Borrador del informe con estructura formal y citas normativas
        """
        try:
            logger.info(f"Generando informe de incidencia: {event_description[:50]}...")
            
            # Buscar contexto normativo relevante
            context = self.retriever.build_context(
                query=f"normativa y procedimientos relacionados con: {event_description}",
                n_results=3,
                include_metadata=True
            )
            
            # Construir el borrador del informe
            report = f"""
            === BORRADOR DE INFORME ===

            DESCRIPCION DEL EVENTO:
            {event_description}

            CONTEXTO NORMATIVO Y REFERENCIAS:
            {context if context else 'No se encontraron referencias normativas especificas en los documentos indexados.'}

            === FIN DEL BORRADOR ===

            NOTA: Revise y ajuste el contenido segun sea necesario antes de su uso oficial."""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generando informe: {e}")
            return f"Error al generar el informe: {str(e)}"
    
    def retrieve_referee_gesture(self, action: str) -> str:
        """
        Recupera el gesto de arbitro correspondiente a una accion especifica. Llama al metodo para la API
        Args:
            action: Descripcion de la accion del arbitro
        Returns:
            Mensaje retornador del método.
        """
        return search_referee_gesture(action)

# ==================== CREAR HERRAMIENTAS DE LANGCHAIN ====================
def create_tools(retriever: Retriever) -> list[Tool]:
    """
    Crea la lista de herramientas (Tools) que puede usar el agente.
    
    Args:
        retriever: Instancia del Retriever
        
    Returns:
        Lista de herramientas de LangChain
    """
    rag_tools = RAGTools(retriever)
    
    tools = [
        Tool(
            name="search_documents",
            func=rag_tools.search_documents,
            description="""Busca informacion relevante en los documentos PDF indexados.

            USA ESTA HERRAMIENTA cuando el usuario:
            - Pregunte sobre contenido especifico de los documentos
            - Necesite datos, hechos, definiciones o citas extraidas de los PDFs
            - Use frases como "segun el documento", "en los PDFs", "que informacion hay sobre..."
            - Pida resumir o explicar algo mencionado en los documentos

            NO USAR cuando:
            - Sea un saludo o conversacion casual ("hola", "como estas")
            - Pregunte sobre funcionalidades del sistema ("que puedes hacer?")
            - Quiera gestionar documentos (anadir/eliminar PDFs) - usar otras herramientas
            - La pregunta no requiera consultar documentos almacenados

            Input: La pregunta exacta del usuario como string
            Output: Fragmentos de texto relevantes con sus fuentes (archivo y pagina)""",
        ),
        Tool(
            name="get_stats",
            func=rag_tools.get_stats,
            description="""Obtiene estadisticas sobre los documentos indexados en el sistema.

            USA ESTA HERRAMIENTA cuando el usuario:
            - Pregunte "cuantos documentos hay indexados?"
            - Pida informacion del sistema ("dame estadisticas", "estado del indice")
            - Quiera saber que PDFs estan disponibles para consultar
            - Pregunte sobre el estado de la base de datos vectorial

            NO USAR cuando:
            - Quiera buscar contenido en los documentos (usar search_documents)
            - Quiera anadir o eliminar documentos (usar ingest_pdf o delete_source)

            Input: Ninguno (esta herramienta no necesita parametros, pasa un string vacio)
            Output: Estadisticas con nombre de coleccion, total de documentos y directorio""",
        ),
        Tool(
            name="generate_incident_report",
            func=rag_tools.generate_incident_report,
            description="""Genera un borrador de acta o informe formal/tecnico basado en una descripcion de un evento o incidencia.

            USA ESTA HERRAMIENTA cuando el usuario:
            - Pida generar un informe, acta o reporte de una incidencia
            - Solicite documentar formalmente un evento
            - Necesite un borrador de informe tecnico

            NO USAR cuando:
            - Solo quiera buscar informacion (usar search_documents)
            - La consulta no requiera generar un documento formal

            La herramienta utiliza el contexto RAG (normativa, manuales) para incluir citas normativas
            relevantes, definir el tono y estructura adecuados, y producir un documento listo para revision.

            Input: Descripcion detallada del evento o incidencia
            Output: Borrador del informe con estructura formal y referencias normativas""",
        ),
        Tool(
            name="retrieve_referee_gesture",
            func=rag_tools.retrieve_referee_gesture,
            description="""Recupera el gesto de arbitro correspondiente a una accion especifica.

            USA ESTA HERRAMIENTA cuando el usuario:
            - Pregunte sobre gestos de arbitro en balonmano
            - Necesite saber como se señala una accion especifica
            - Pida informacion sobre señales arbitrales (ej: "como se señala dos minutos?")

            NO USAR cuando:
            - Solo quiera buscar informacion general (usar search_documents)
            - La consulta no este relacionada con gestos o señales de arbitraje

            La herramienta normaliza el input, mapea sinonimos y busca en la API de gestos de arbitro
            la URL sobre el gesto solicitado.
            
            IMPORTANTE: Si la herramienta devuelve que el gesto no está disponible, DEBES informar al usuario
            exactamente eso. NUNCA proporciones información alternativa de otras fuentes, enlaces externos,
            ni uses tu conocimiento general. Solo devuelve gestos que estén en la base de datos.

            Input: Descripcion de la accion del arbitro (ej: "dos minutos", "juego pasivo")
            Output: URL del gesto del arbitro encontrado en la API o mensaje de error si no existe""",
        ),
    ]
    
    logger.info(f"Creadas {len(tools)} herramientas para el agente")
    return tools

from typing import Optional, Dict, Any
import logging
from pathlib import Path

from langchain.tools import Tool

from rag.retriever import Retriever

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
    
    def search_documents(self, query: str, n_results: int = 2) -> str:
        """
        Busca informacion relevante en los documentos indexados.
        
        Args:
            query: Pregunta o consulta del usuario
            n_results: Numero de fragmentos a recuperar
            
        Returns:
            Contexto consolidado con la informacion encontrada
        """
        try:
            logger.info(f"Buscando: '{query}' (n_results={n_results})")
            
            # Usar build_context para obtener un string consolidado
            context = self.retriever.build_context(
                query=query,
                n_results=n_results,
                include_metadata=True  # Incluir fuentes para que el agente las cite
            )
            
            if not context:
                return "No se encontro informacion relevante en los documentos indexados."
            
            return context
            
        except Exception as e:
            logger.error(f"Error en busqueda: {e}")
            return f"Error al buscar en los documentos: {str(e)}"
    
    def ingest_pdf(self, pdf_path: str) -> str:
        """
        Indexa un nuevo PDF en el sistema.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Mensaje indicando el resultado de la operacion
        """
        try:
            # Verificar que el archivo existe
            if not Path(pdf_path).exists():
                return f"Error: El archivo '{pdf_path}' no existe."
            
            # Verificar que es un PDF
            if not pdf_path.lower().endswith('.pdf'):
                return f"Error: El archivo '{pdf_path}' no es un PDF."
            
            logger.info(f"Indexando PDF: {pdf_path}")
            count = self.retriever.add_pdf(pdf_path)
            
            return f"[OK] PDF indexado correctamente: '{Path(pdf_path).name}' ({count} fragmentos anadidos)"
            
        except Exception as e:
            logger.error(f"Error indexando PDF {pdf_path}: {e}")
            return f"Error al indexar el PDF: {str(e)}"
    
    def get_stats(self, tool_input: str = "") -> str:
        """
        Obtiene estadisticas del indice vectorial.
        
        Args:
            tool_input: Input opcional (ignorado, pero LangChain lo pasa)
        
        Returns:
            Informacion sobre el estado del sistema
        """
        try:
            stats = self.retriever.stats()
            
            return f"""[STATS] Estadisticas del sistema:
            - Coleccion: {stats['collection_name']}
            - Total de documentos indexados: {stats['total_documents']}
            - Directorio de persistencia: {stats['persist_dir']}"""
            
        except Exception as e:
            logger.error(f"Error obteniendo estadisticas: {e}")
            return f"Error al obtener estadisticas: {str(e)}"
    
    def delete_source(self, source: str) -> str:
        """
        Elimina todos los fragmentos de un PDF especifico.
        
        Args:
            source: Nombre del archivo PDF a eliminar
            
        Returns:
            Mensaje indicando el resultado
        """
        try:
            logger.info(f"Eliminando fuente: {source}")
            self.retriever.delete_source(source)
            
            return f"[DELETE] Documentos eliminados correctamente: '{source}'"
            
        except Exception as e:
            logger.error(f"Error eliminando fuente {source}: {e}")
            return f"Error al eliminar la fuente: {str(e)}"


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
            - Pregunte sobre contenido especifico de los documentos (ej: "Que dice sobre machine learning?")
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
            name="ingest_pdf",
            func=rag_tools.ingest_pdf,
            description="""Indexa un nuevo archivo PDF en el sistema para que pueda ser consultado posteriormente.

            USA ESTA HERRAMIENTA cuando el usuario:
            - Pida anadir, subir, indexar o cargar un PDF nuevo
            - Diga "anade este documento", "indexa este PDF", "sube este archivo", "actualiza la documentacion"
            - Quiera que un PDF este disponible para consultas futuras

            NO USAR cuando:
            - El usuario solo quiera buscar informacion (usar search_documents)
            - Pregunte cuantos PDFs hay (usar get_stats)
            - Quiera eliminar un PDF (usar delete_source)

            IMPORTANTE: El usuario debe proporcionar la ruta completa al archivo PDF.

            Input: Ruta absoluta al archivo PDF (ej: "C:/documentos/manual.pdf")
            Output: Confirmacion con numero de fragmentos indexados""",
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
            name="delete_source",
            func=rag_tools.delete_source,
            description="""Elimina todos los fragmentos de un PDF especifico del indice vectorial.

            USA ESTA HERRAMIENTA cuando el usuario:
            - Pida eliminar, borrar o quitar un PDF especifico
            - Diga "elimina el documento X", "borra el PDF Y", "quita el archivo Z"
            - Quiera remover un documento que ya no necesita

            NO USAR cuando:
            - Quiera buscar informacion (usar search_documents)
            - Quiera anadir documentos (usar ingest_pdf)
            - Solo quiera ver que hay indexado (usar get_stats)

            ADVERTENCIA: Esta accion es irreversible. Si se elimina, hay que volver a indexar.

            Input: Nombre exacto del archivo PDF a eliminar (ej: "manual.pdf")
            Output: Confirmacion de eliminacion""",
        ),
    ]
    
    logger.info(f"Creadas {len(tools)} herramientas para el agente")
    return tools

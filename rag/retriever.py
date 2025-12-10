from typing import List, Optional, Dict, Any
import logging
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from rag.vectorstore import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """
    Capa de abstracción sobre VectorStore.
    Proporciona API sencilla para RAG y compatibilidad con LangChain.
    """

    def __init__(self):
        """
        Inicializa el Retriever.
        
        Args:
            persist_dir: Directorio donde persisten los embeddings
            collection_name: Nombre de la colecciÃ³n de Chroma
        """
        self.vectorstore = VectorStore()
        logger.info("Retriever inicializado")

    # ==================== INGESTA ====================
    def add_pdf(self, pdf_path: str) -> int:
        """
        Añade un PDF al índice vectorial.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Número de chunks indexados
        """
        try:
            count = self.vectorstore.ingest_pdf(pdf_path)
            logger.info(f"PDF indexado: {pdf_path} ({count} chunks)")
            return count
        except Exception as e:
            logger.error(f"Error indexando PDF {pdf_path}: {e}")
            raise

    # ==================== BÚSQUEDA ====================
    def search(self, query: str, n_results: int) -> List[Document]:
        """
        Realiza una búsqueda semántica en el índice.
        
        Args:
            query: Consulta del usuario
            n_results: Número de resultados a devolver
            
        Returns:
            Lista de documentos más relevantes
        """
        try:
            docs = self.vectorstore.query(query, n_results=n_results)
            logger.info(f"Búsqueda: '{query[:50]}...' {len(docs)} resultados")
            return docs
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []

    # ==================== CONTEXTO PARA RAG ====================
    def build_context(
        self, 
        query: str, 
        n_results: int = 2,
        include_metadata: bool = False
    ) -> str:
        """
        Construye un contexto consolidado para el LLM a partir de los documentos recuperados.
        
        Args:
            query: Consulta del usuario
            n_results: Número de chunks a recuperar
            include_metadata: Si incluir información de fuente y página
            
        Returns:
            Contexto como string único, listo para pasar al LLM
        """
        docs = self.search(query, n_results)
        
        if not docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content.strip()
            
            if include_metadata:
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                context_parts.append(
                    f"[Fuente {i}: {source}, pagina. {page}]\n{content}"
                )
            else:
                context_parts.append(content)
        
        return "\n\n---\n\n".join(context_parts)

    # ==================== GESTION DE COLECCION ====================
    def stats(self) -> Dict[str, Any]:
        """
        Devuelve estadísticas básicas de la colección.
        
        Returns:
            Diccionario con información sobre el estado del índice
        """
        return {
            "collection_name": self.vectorstore.collection_name,
            "total_documents": self.vectorstore.get_collection_count(),
            "indexed_documents": self.vectorstore.get_indexed_sources()
        }


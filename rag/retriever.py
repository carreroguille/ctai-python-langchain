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

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "pdf_collection"
    ):
        """
        Inicializa el Retriever.
        
        Args:
            persist_dir: Directorio donde persisten los embeddings
            collection_name: Nombre de la colecciÃ³n de Chroma
        """
        self.vectorstore = VectorStore(
            persist_dir=persist_dir,
            collection_name=collection_name
        )
        logger.info(f"Retriever inicializado: {collection_name}")

    # ==================== INGESTA ====================
    def add_pdf(self, pdf_path: str) -> int:
        """
        AÃ±ade un PDF al índice vectorial.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            NÃºmero de chunks indexados
        """
        try:
            count = self.vectorstore.ingest_pdf(pdf_path)
            logger.info(f"PDF indexado: {pdf_path} ({count} chunks)")
            return count
        except Exception as e:
            logger.error(f"Error indexando PDF {pdf_path}: {e}")
            raise

    # ==================== BÚSQUEDA ====================
    def search(self, query: str, n_results: int = 2) -> List[Document]:
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
                    f"[Fuente {i}: {source}, pag. {page}]\n{content}"
                )
            else:
                context_parts.append(content)
        
        return "\n\n---\n\n".join(context_parts)

    # ==================== COMPATIBILIDAD LANGCHAIN ====================
    def as_langchain_retriever(
        self, 
        search_kwargs: Optional[Dict[str, Any]] = None
    ) -> BaseRetriever:
        """
        Devuelve un retriever compatible con la interfaz estÃ¡ndar de LangChain.
        Ãštil para integrarse con chains y agents de LangChain.
        
        Args:
            search_kwargs: Parámetros de búsqueda como {"k": 4}
            
        Returns:
            BaseRetriever de LangChain
        """
        search_kwargs = search_kwargs or {"k": 3}
        return self.vectorstore.vectorstore.as_retriever(
            search_kwargs=search_kwargs
        )

    # ==================== GESTIÃ“N DE COLECCIÃ“N ====================
    def delete_source(self, source: str) -> None:
        """
        Elimina todos los chunks pertenecientes a un PDF específico.
        
        Args:
            source: Metadata del "source" almacenada en cada chunk
        """
        try:
            self.vectorstore.delete_by_source(source)
            logger.info(f"Documentos eliminados: {source}")
        except Exception as e:
            logger.error(f"Error eliminando {source}: {e}")
            raise

    def reset(self) -> None:
        """
        Vacía completamente la colección.
        ADVERTENCIA: Esta operación es irreversible.
        """
        try:
            self.vectorstore.reset()
            logger.warning("Colección reseteada completamente")
        except Exception as e:
            logger.error(f"Error reseteando colecciÃ³n: {e}")
            raise

    def stats(self) -> Dict[str, Any]:
        """
        Devuelve estadísticas básicas de la colección.
        
        Returns:
            Diccionario con información sobre el estado del índice
        """
        return {
            "collection_name": self.vectorstore.collection_name,
            "persist_dir": self.vectorstore.persist_dir,
            "total_documents": self.vectorstore.get_collection_count()
        }

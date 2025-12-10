from pathlib import Path
from typing import List, Optional, Dict
import logging

from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from utils.pdf_utils import load_and_split_pdf
from config.settings import (GOOGLE_API_KEY, EMBEDDING_MODEL, CHROMA_PERSIST_DIR, CHUNK_SIZE, CHUNK_OVERLAP)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class VectorStore:
    def __init__(self):
        """
        Inicializa ChromaDB persistente.
        """
        
        self.persist_dir = CHROMA_PERSIST_DIR
        self.collection_name = "pdf_cta_collection"
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY
        )
        
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings_model,
            persist_directory=self.persist_dir
        )
        
    def document_exists(self, source: str) -> bool:
        """Verifica si un documento ya ha sido indexado
        
        Args:
            source (str): nombre del archivo fuente
            
        Returns:
            bool: True si ya existe, False en caso contrario
        """
        # Buscamos si hay algún documento con ese source
        # Usamos get con un where filter
        existing = self.vectorstore.get(
            where={"source": source},
            limit=1
        )
        
        return len(existing['ids']) > 0

    def ingest_pdf(self, pdf_path: str) -> int:
        """Convierte un PDF a embeddings y los almacena en ChromaDB

        Args:
            pdf_path (str): ruta al fichero PDF

        Returns:
            int: número de chunks almacenados
        """
        
        filename = Path(pdf_path).name
        
        # Verificar si ya existe
        if self.document_exists(filename):
            raise ValueError(f"El documento '{filename}' ya ha sido indexado previamente.")
            
        chunks: List[Document] = load_and_split_pdf(
            pdf_path,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        
        ids = self.vectorstore.add_documents(documents=chunks)
        
        return len(ids)
    
    def query(self, query_text: str, n_results: int = 2) -> List[Document]:
        """Busqueda semántica usando texto de consulta

        Args:
            query_text (str): consulta
            n_results (int, optional): numero de resultados obtenidos de la consulta. Defaults to 2.

        Returns:
            List[Document]: Devuelve la lista de documentos similares
        """
        
        results = self.vectorstore.similarity_search(
            query=query_text,
            k=n_results
        )
        
        return results
    
    def delete_by_source(self, source: str) -> None:
        """Elimina documentos por fuente

        Args:
            source (str): fuente del documento
        """
        
        all_docs = self.vectorstore.get()
        ids_to_delete = [
            doc_id for doc_id, meta in zip(all_docs['ids'], all_docs['metadata'])
            if meta.get('source') == source
        ]
        
        if ids_to_delete:
            self.vectorstore.delete(ids=ids_to_delete)
            
    def reset(self) -> None:
        """Elimina completamente la colección
        """
        
        try:
            self.vectorstore.delete_collection()
        except Exception as e:
            logger.warning(f"Error al eliminar la colección: {e}")
            
        self.vectorstore = Chroma(
            collection_name= self.collection_name,
            embedding_function=self.embeddings_model,
            persist_directory=self.persist_dir
        )
        
        logger.info("VectorStore reseteado correctamente")
        
    def get_collection_count(self) -> int:
        """Devuelve el número de documentos en la colección

        Returns:
            int: número de docs en la colección
        """
        return self.vectorstore._collection.count()
    
    def get_indexed_sources(self) -> List[str]:
        """Devuelve la lista de nombres de documentos indexados (fuentes únicas)

        Returns:
            List[str]: lista de nombres de archivos indexados
        """
        try:
            all_docs = self.vectorstore.get()
            sources = set()
            for meta in all_docs.get('metadatas', []):
                if meta and 'source' in meta:
                    sources.add(meta['source'])
            return sorted(list(sources))
        except Exception as e:
            logger.error(f"Error obteniendo fuentes indexadas: {e}")
            return []

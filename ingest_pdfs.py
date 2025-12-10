import logging
from pathlib import Path
import sys

from rag.retriever import Retriever
from config.settings import BASE_DIR

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def ingest_pdfs_from_directory(directory: Path, retriever: Retriever):
    """
    Ingesta todos los PDFs de un directorio.
    
    Args:
        directory: Ruta al directorio con PDFs
        retriever: Instancia del Retriever
    """
    pdf_files = list(directory.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No se encontraron archivos PDF en {directory}")
        return
    
    logger.info(f"Encontrados {len(pdf_files)} archivos PDF en {directory}")
    
    successful = 0
    failed = 0
    skipped = 0
    
    for pdf_path in pdf_files:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Procesando: {pdf_path.name}")
            logger.info(f"{'='*60}")
            
            chunks_count = retriever.add_pdf(str(pdf_path))
            
            logger.info(f"✅ {pdf_path.name} indexado exitosamente ({chunks_count} chunks)")
            successful += 1
            
        except ValueError as e:
            # PDF ya indexado
            logger.warning(f"⚠️  {pdf_path.name}: {str(e)}")
            skipped += 1
            
        except Exception as e:
            logger.error(f"❌ Error procesando {pdf_path.name}: {str(e)}", exc_info=True)
            failed += 1
    
    # Resumen final
    logger.info(f"\n{'='*60}")
    logger.info("RESUMEN DE INGESTA")
    logger.info(f"{'='*60}")
    logger.info(f"Total de archivos: {len(pdf_files)}")
    logger.info(f"✅ Indexados exitosamente: {successful}")
    logger.info(f"⚠️  Omitidos (ya indexados): {skipped}")
    logger.info(f"❌ Fallidos: {failed}")
    logger.info(f"{'='*60}\n")


def main():
    """Función principal del script."""
    
    # Directorio de PDFs
    pdf_directory = BASE_DIR / "data" / "raw"
    
    if not pdf_directory.exists():
        logger.error(f"❌ El directorio {pdf_directory} no existe")
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("SCRIPT DE INGESTA DE PDFs")
    logger.info("="*60)
    logger.info(f"Directorio: {pdf_directory}")
    logger.info("="*60 + "\n")
    
    try:
        # Inicializar retriever
        logger.info("Inicializando sistema RAG...")
        retriever = Retriever()
        logger.info("✅ Sistema RAG inicializado\n")
        
        # Ingestar PDFs
        ingest_pdfs_from_directory(pdf_directory, retriever)
        
        # Mostrar estadísticas finales
        stats = retriever.stats()
        logger.info("\n" + "="*60)
        logger.info("ESTADÍSTICAS DEL VECTORSTORE")
        logger.info("="*60)
        logger.info(f"Colección: {stats['collection_name']}")
        logger.info(f"Total de chunks: {stats['total_documents']}")
        logger.info(f"Documentos indexados:")
        for doc in stats.get('indexed_documents', []):
            logger.info(f"  - {doc}")
        logger.info("="*60 + "\n")
        
        logger.info("✅ Proceso de ingesta completado exitosamente")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n❌ Error fatal: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

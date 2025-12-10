import logging
import signal
import sys
import atexit
import shutil
from pathlib import Path

from bot.telegram_agent import TelegramBot
from config.settings import BASE_DIR

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def cleanup_vectorstore():
    """Elimina la carpeta vectorstore al finalizar el programa."""
    vectorstore_path = BASE_DIR / "vectorstore"
    if vectorstore_path.exists():
        try:
            shutil.rmtree(vectorstore_path)
            logger.info(f"🗑️  Carpeta vectorstore eliminada: {vectorstore_path}")
        except Exception as e:
            logger.error(f"Error al eliminar vectorstore: {e}")


# Registrar la función de limpieza para que se ejecute al finalizar
atexit.register(cleanup_vectorstore)


def signal_handler(sig, frame):
    """Maneja señales de interrupción (Ctrl+C)."""
    print("\n\n🛑 Señal de interrupción recibida. Deteniendo bot...")
    sys.exit(0)


def main():
    """Función principal que ejecuta el bot."""
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        logger.info("Iniciando Telegram Bot...")
        bot = TelegramBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        print(f"\n❌ Error fatal al ejecutar el bot: {e}")
        print("Verifica tu configuración en .env y que todas las dependencias estén instaladas.")
        sys.exit(1)


if __name__ == "__main__":
    main()

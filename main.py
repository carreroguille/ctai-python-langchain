import logging
import signal
import sys

from bot.telegram_agent import TelegramBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


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

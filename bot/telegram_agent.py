import logging
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from agents.ai_agent import AIAgent
from rag.retriever import Retriever
from config.settings import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Bot de Telegram que integra el AIAgent RAG.
    Maneja mensajes de texto, archivos PDF y URLs de PDF.
    """
    
    def __init__(self):
        """
        Inicializa el bot de Telegram.
        
        Args:
            token: Token del bot (si no se proporciona, se usa TELEGRAM_BOT_TOKEN del .env)
        """
        self.token = TELEGRAM_BOT_TOKEN
        
        logger.info("Inicializando sistema RAG...")

        self.retriever = Retriever()
        self.agent = AIAgent(self.retriever)
        self.application = Application.builder().token(self.token).build()
        self._register_handlers()

        logger.info("TelegramBot inicializado correctamente")

    def _register_handlers(self):
        """
        Registra los handlers para manejar comandos y mensajes.
        """
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("reset", self.reset_command))

        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.Document.PDF, self.handle_pdf))

        logger.info("Handlers registrados correctamente")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja el comando /start.
        """
        welcome_message = """
        🤾 ¡Hola! Soy tu Asistente de Reglamentación de Balonmano CT.AI 🤾

        Estoy aquí para ayudarte con consultas sobre el reglamento, sanciones y normativa de balonmano.

        **¿Qué puedo hacer?**
        📖 Responder preguntas sobre el reglamento
        📄 Indexar nuevos PDFs (envíamelos directamente o comparte un enlace)
        💬 Mantener conversaciones con contexto

        **Comandos disponibles:**
        /start - Iniciar conversación
        /help - Ver esta ayuda
        /reset - Limpiar memoria de conversación
        
        ¡Pregúntame lo que necesites! 🏐
        """
        await update.message.reply_text(welcome_message, parse_mode="Markdown")
        logger.info(f"Usuario {update.effective_user.id} inició conversación")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja el comando /help.
        """
        help_message = """
        🤾 ¿Necesitas ayuda? Aquí tienes una breve explicación de mi funcionamiento 🤾

        **Cómo usarme:**

        1️⃣ **Hacer preguntas:**
        Simplemente escribe tu pregunta sobre el reglamento.
        Ejemplo: "¿Cuántos pasos puede dar un jugador con el balón?"

        2️⃣ **Indexar PDFs:**
        • Envíame un archivo PDF directamente (máx. 20 MB)
        • O comparte un enlace a un PDF (Google Drive, Dropbox,  etc.)
        Lo indexaré automáticamente para futuras consultas.

        3️⃣ **Comandos:**
        - /start - Mensaje de bienvenida
        - /help - Esta ayuda
        - /reset - Limpiar memoria de conversación

        💡 **Tip:** Puedo mantener el contexto de nuestra conversación, así que puedes hacer preguntas de seguimiento sin repetir información.

        ¿Alguna duda? ¡Pregunta! 😊 🏐
        """

        await update.message.reply_text(help_message, parse_mode="Markdown")
        logger.info(f"Usuario {update.effective_user.id} solicitó ayuda")

    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para el comando /reset."""

        try:
            self.agent.reset_memory()
            await update.message.reply_text("🧹 Memoria de conversación limpiada. ¡Empecemos de nuevo!")

            logger.info(f"Usuario {update.effective_user.id} limpió la memoria")

        except Exception as e:
            logger.error(f"Error al limpiar memoria: {e}", exc_info=True)

            await update.message.reply_text("❌ Error al limpiar la memoria.")

    # ==================== HANDLERS DE MENSAJES ====================
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensajes de texto normales y URLs de PDF."""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Mensaje de usuario {user_id}: {user_message[:50]}...")
        
        try:
            await update.message.chat.send_action(action="typing")
            
            response = self.agent.process_message(
                user_message,
                user_id=str(user_id),
                session_id=str(update.message.chat_id)
            )
            await update.message.reply_text(response, parse_mode="Markdown")
            
            logger.info(f"Respuesta enviada a usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
            
            error_message = (
                "❌ Lo siento, ocurrió un error al procesar tu mensaje.\n\n"
                "Por favor, intenta de nuevo o usa /help para ver cómo puedo ayudarte."
            )
            await update.message.reply_text(error_message)

    async def handle_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para archivos PDF enviados por el usuario."""
        user_id = update.effective_user.id
        document = update.message.document
        temp_path = None  
        
        logger.info(f"Usuario {user_id} envió PDF: {document.file_name}")
        
        file_size_mb = document.file_size / (1024 * 1024)  
        if file_size_mb > 20:
            await update.message.reply_text(
                f"❌ **Archivo demasiado grande**\n\n"
                f"El archivo pesa {file_size_mb:.1f} MB, pero el límite es de 20 MB.\n\n"
                f"💡 **Solución:** Comprime el PDF antes de enviarlo.",
                parse_mode="Markdown"
            )

            logger.warning(f"Usuario {user_id} intentó enviar PDF muy grande: {file_size_mb:.1f} MB")
            return
        
        try:
            await update.message.reply_text(
                f"📄 Recibido: {document.file_name}\n"
                "⏳ Descargando e indexando... Esto puede tardar unos minutos."
            )
            
            file = await document.get_file()
            
            temp_dir = Path("temp_pdfs")
            temp_dir.mkdir(exist_ok=True)
            
            temp_path = temp_dir / document.file_name
            await file.download_to_drive(str(temp_path))
            
            logger.info(f"PDF descargado en: {temp_path}")
            
            ingest_message = f"Indexa el archivo {temp_path}"
            response = self.agent.process_message(ingest_message)
            
            temp_path.unlink()
            logger.info(f"Archivo temporal eliminado: {temp_path}")
            
            await update.message.reply_text(response)
            
            logger.info(f"PDF indexado exitosamente para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error procesando PDF: {e}", exc_info=True)
            
            error_msg = "❌ Error al procesar el PDF.\n\n"
            
            if "File is too big" in str(e):
                error_msg += "El archivo es demasiado grande para descargar."
            elif "Bad Request" in str(e):
                error_msg += "Asegúrate de que el archivo sea un PDF válido."
            else:
                error_msg += "Por favor, intenta de nuevo o envía un archivo diferente."
            
            await update.message.reply_text(error_msg)
            
            if temp_path and temp_path.exists():
                temp_path.unlink()
                logger.info(f"Archivo temporal eliminado tras error: {temp_path}")

    # ==================== EJECUTAR BOT ====================
    
    def run(self):
        """Ejecuta el bot en modo polling."""
        logger.info("Iniciando bot en modo polling...")
        print("\n" + "="*60)
        print("🤾 BOT DE TELEGRAM - ASISTENTE DE BALONMANO 🤾")
        print("="*60)
        print("✅ Bot iniciado correctamente")
        print("📡 Escuchando mensajes...")
        print("🛑 Presiona Ctrl+C para detener")
        print("="*60 + "\n")
        
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    def stop(self):
        """Detiene el bot gracefully."""
        logger.info("Deteniendo bot...")
        print("\n🛑 Bot detenido")
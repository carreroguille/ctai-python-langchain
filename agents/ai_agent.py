from typing import Optional, Dict, Any
import logging

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

from agents.tools import create_tools
from rag.retriever import Retriever
from config.settings import OPENAI_API_KEY

logger = logging.getLogger(__name__)


class AIAgent:
    """
    Agente LLM que usa herramientas para responder consultas sobre documentos PDF.
    El LLM razona y decide qué herramienta usar basándose en el mensaje del usuario.
    Compatible con LangChain 0.2.17
    """
    
    def __init__(
        self,
        retriever: Retriever,
        model_name: str = "qwen/qwen3-32b",
        temperature: float = 0.7,
        use_memory: bool = True
    ):
        """
        Inicializa el agente con LLM y herramientas.
        
        Args:
            retriever: Instancia del Retriever para búsquedas
            model_name: Nombre del modelo (para OpenRouter)
            temperature: Temperatura del LLM (0-1)
            use_memory: Si mantener memoria conversacional
        """
        self.retriever = retriever
        self.use_memory = use_memory
        
        # Inicializar el LLM con OpenRouter
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",  
            temperature=temperature
        )
        
        # Crear las herramientas RAG
        self.tools = create_tools(retriever)
        
        # Crear memoria conversacional si está habilitada
        self.memory = None
        if use_memory:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        
        # Crear el agente
        self.agent = self._create_agent()
        
        logger.info(f"AIAgent inicializado con modelo {model_name}")
    
    def _create_agent(self):
        """
        Crea el agente usando initialize_agent.
        El LLM razona y decide qué herramienta usar.
        
        Returns:
            Agent configurado
        """
        # Prompt del sistema para el agente
        system_message = """Eres un Asistente Experto en Reglamentación y Normativa de Balonmano.
        Tu misión es resolver dudas sobre el reglamento, sanciones, procedimientos de competición y normativa general de forma precisa, actuando como un apoyo técnico confiable para árbitros, entrenadores y jugadores en un chat de Telegram.

        DIRECTRICES DE COMPORTAMIENTO Y ESTILO:

        1. **Tono:** Profesional pero cercano (estilo Telegram). Usa un lenguaje claro y conciso. Puedes usar emojis puntuales (ej: 🤾, ⚠️, 📝) para hacer la lectura amena, pero sin perder seriedad.

        2. **Rigor Normativo:** Cuando respondas dudas de juego (usando `search_documents`), basa tu respuesta ESTRICTAMENTE en el contexto recuperado.
        * Si el documento menciona una regla específica (ej: "Regla 8:5"), CÍTALA explícitamente.
        * NO INVENTES reglas. Si la información no está en los documentos, di: "Lo siento, no encuentro esa normativa específica en mis documentos actuales".

        3. **Estructura de Respuesta:**
        * Empieza con una conclusión directa.
        * Justifica con la norma/artículo.
        * Si es necesario, añade una breve explicación coloquial para aclarar la jerga técnica.

        USO OBLIGATORIO DE HERRAMIENTAS:

        NUNCA inventes información que puedas obtener de una herramienta. SIEMPRE usa herramientas cuando:

        - Usuario pregunta "¿cuántos documentos hay?" o "¿qué documentos tienes?" 
          → OBLIGATORIO usar get_stats (NUNCA inventes un número)
        
        - Usuario pregunta sobre contenido del reglamento, reglas, sanciones, normativa
          → OBLIGATORIO usar search_documents (NUNCA inventes reglas)
        
        - Usuario quiere añadir/indexar un PDF
          → OBLIGATORIO usar ingest_pdf
        
        - Usuario quiere eliminar un documento
          → OBLIGATORIO usar delete_source

        SOLO responde directamente SIN herramientas para:
        - Saludos: "Hola", "Buenos días", "¿Qué tal?"
        - Preguntas sobre tus capacidades: "¿Qué puedes hacer?", "¿Cómo funcionas?"
        - Conversación general que NO requiera datos específicos

        FORMATO ESTRICTO:
        
        Para usar herramientas (OBLIGATORIO en casos arriba):
        Thought: [Identifico que necesito datos verificables, debo usar herramienta X]
        Action: [nombre de la herramienta]
        Action Input: [input para la herramienta]
        
        Para responder sin herramientas (SOLO saludos y preguntas generales):
        Thought: [Es un saludo/pregunta general, no necesito herramientas]
        Final Answer: [tu respuesta directa]

        REGLA DE ORO: Si la respuesta requiere un dato verificable (cantidad, regla, contenido), USA LA HERRAMIENTA.
        
        IMPORTANTE: NUNCA menciones los nombres técnicos de las herramientas (como 'ingest_pdf', 'get_stats', 'search_documents') en tu respuesta final al usuario. 
        En su lugar, usa lenguaje natural: "He consultado los documentos", "He indexado el archivo", "He verificado las estadísticas".
        NO rompas la cuarta pared diciendo "usaré la herramienta X"."""

        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,  
            memory=self.memory,
            handle_parsing_errors=True,  
            max_iterations=5,  
            agent_kwargs={
                "prefix": system_message,
            }
        )
        
        return agent
    
    def process_message(self, message: str) -> str:
        """
        Procesa un mensaje del usuario y devuelve la respuesta.
        El LLM razona y decide qué herramienta usar.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Respuesta del agente
        """
        try:
            logger.info(f"Procesando mensaje: '{message[:100]}...'")
            
            result = self.agent.invoke({"input": message})
            
            response = result.get("output", "No pude generar una respuesta.")
            
            logger.info(f"Respuesta generada exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
            return f"Lo siento, ocurrió un error al procesar tu mensaje: {str(e)}"
    
    def reset_memory(self):
        """Limpia la memoria conversacional del agente."""
        if self.memory:
            self.memory.clear()
            logger.info("Memoria del agente limpiada")
        else:
            logger.warning("No hay memoria configurada para limpiar")
    
    def get_conversation_history(self) -> list:
        """
        Obtiene el historial de la conversación.
        
        Returns:
            Lista de mensajes si hay memoria, lista vacía si no
        """
        if self.memory:
            return self.memory.chat_memory.messages
        return []

# Bot de Telegram RAG - Asistente de Reglamentación de Balonmano

Sistema de bot de Telegram con RAG (Retrieval-Augmented Generation) para responder consultas sobre reglamentación de balonmano.

## 🎯 Características

- 🤾 Responde preguntas sobre el reglamento de balonmano
- 📄 Indexa PDFs automáticamente (envíalos directamente al bot)
- 🧠 Mantiene contexto de la conversación
- 📊 Estadísticas del sistema
- 🔍 Búsqueda semántica en documentos

## 📋 Requisitos

- Python 3.11+
- Cuenta de Telegram y token de bot ([@BotFather](https://t.me/botfather))
- API keys:
  - OpenRouter API key (para LLM)
  - Google API key (para embeddings)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd ctai-python-langchain
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# API Keys
GOOGLE_API_KEY=AIza...                    # Google Generative AI (embeddings)
OPENAI_API_KEY=sk-or-v1-...               # OpenRouter (LLM)
TELEGRAM_BOT_TOKEN=1234567890:ABC...      # Bot de Telegram

# Configuración ChromaDB
CHROMA_PERSIST_DIR=./vectorstore/chroma_db
EMBEDDING_MODEL=models/text-embedding-004
```

### 5. Obtener tokens y API keys

#### **Telegram Bot Token:**
1. Abre Telegram y busca [@BotFather](https://t.me/botfather)
2. Envía `/newbot`
3. Sigue las instrucciones
4. Copia el token que te proporciona

#### **OpenRouter API Key:**
1. Regístrate en [openrouter.ai](https://openrouter.ai/)
2. Ve a Settings → API Keys
3. Crea una nueva key
4. Cópiala (empieza con `sk-or-v1-`)

#### **Google API Key:**
1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crea una API key
3. Cópiala (empieza con `AIza`)

## ▶️ Ejecutar el Bot

```bash
python main.py
```

Deberías ver:
```
============================================================
🤾 BOT DE TELEGRAM - ASISTENTE DE BALONMANO 🤾
============================================================
✅ Bot iniciado correctamente
📡 Escuchando mensajes...
🛑 Presiona Ctrl+C para detener
============================================================
```

## 💬 Uso del Bot

### Comandos disponibles

- `/start` - Mensaje de bienvenida
- `/help` - Ayuda y guía de uso
- `/stats` - Estadísticas del sistema (documentos indexados)
- `/reset` - Limpiar memoria de conversación

### Interacción

**Hacer preguntas:**
```
Usuario: ¿Cuántos pasos puede dar un jugador con el balón?
Bot: [Responde basándose en los documentos indexados]
```

**Indexar PDFs:**
```
1. Envía un archivo PDF directamente al chat
2. El bot lo descarga e indexa automáticamente
3. Confirma cuando está listo
```

**Conversación contextual:**
```
Usuario: ¿Cuál es la sanción por conducta antideportiva?
Bot: [Responde]
Usuario: ¿Y si es reincidente?
Bot: [Mantiene el contexto de la pregunta anterior]
```

## 🧪 Testing

### Test local (sin Telegram)
```bash
python test_agent.py
```

Ejecuta pruebas automáticas y un modo interactivo de chat.

### Test con Telegram
1. Ejecuta `python main.py`
2. Abre Telegram y busca tu bot
3. Envía `/start`
4. Prueba los comandos y envía preguntas

## 📁 Estructura del Proyecto

```
ctai-python-langchain/
├── agents/
│   ├── ai_agent.py          # Agente LLM con ReAct pattern
│   └── tools.py             # Herramientas RAG
├── rag/
│   ├── vectorstore.py       # Gestión de ChromaDB
│   └── retriever.py         # Capa de abstracción RAG
├── telegram/
│   └── telegram_agent.py    # Integración con Telegram
├── config/
│   └── settings.py          # Configuración y variables
├── utils/
│   ├── pdf_utils.py         # Procesamiento de PDFs
│   └── formatting.py        # Formato de respuestas
├── data/                    # PDFs de reglamento
├── test_agent.py            # Script de testing
├── main.py                  # Punto de entrada
└── requirements.txt         # Dependencias
```

## 🛠️ Tecnologías Utilizadas

- **LangChain 0.2.17** - Framework para LLMs
- **python-telegram-bot 21.7** - Librería de Telegram
- **ChromaDB 0.5.23** - Base de datos vectorial
- **OpenRouter** - Proveedor de LLMs
- **Google Generative AI** - Embeddings
- **PyMuPDF** - Procesamiento de PDFs

## 🐛 Troubleshooting

### Error: "TELEGRAM_BOT_TOKEN no encontrado"
- Verifica que el archivo `.env` existe en la raíz
- Verifica que la variable está correctamente definida
- No uses comillas en el `.env`

### Error 401 - OpenRouter
- Verifica que tu API key es válida
- Verifica que tienes créditos en tu cuenta
- La key debe empezar con `sk-or-v1-`

### El bot no responde
- Verifica que `main.py` está ejecutándose
- Revisa los logs en la consola
- Verifica que el token de Telegram es correcto

### PDFs no se indexan
- Verifica que el archivo es un PDF válido
- Revisa los logs para ver errores específicos
- El archivo se guarda temporalmente en `temp_pdfs/`

## 📝 Notas

- El bot mantiene un directorio `vectorstore/` con los embeddings
- Los PDFs se procesan en chunks de 1500 caracteres con overlap de 200
- La memoria conversacional es por sesión (se pierde al reiniciar el bot)
- Usa `/reset` para limpiar la memoria sin reiniciar

## 📄 Licencia

[Tu licencia aquí]

## 🤝 Contribuir

[Instrucciones de contribución aquí]

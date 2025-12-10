# 🤾 Bot de Telegram RAG - Asistente de Reglamentación de Balonmano

Sistema inteligente de bot de Telegram con RAG (Retrieval-Augmented Generation) para responder consultas sobre reglamentación de balonmano, gestos arbitrales y ayuda en la generación de informes técnicos.

## 🎯 Características

- 🤾 **Consultas sobre reglamento**: Responde preguntas basadas en documentos PDF indexados
- 🧠 **Memoria conversacional**: Mantiene contexto de la conversación
- 📊 **Estadísticas del sistema**: Consulta documentos indexados y chunks almacenados
- 🔍 **Búsqueda semántica**: Recuperación eficiente de información relevante
- 🏐 **Gestos arbitrales**: Consulta gestos de árbitro mediante API externa
- 📝 **Generación de informes**: Crea borradores de actas e informes técnicos con referencias normativas
- 📈 **Observabilidad con Langfuse**: Trazabilidad completa de interacciones LLM 

## 📋 Requisitos

- Python 3.11+
- Cuenta de Telegram y token de bot ([@BotFather](https://t.me/botfather))
- API keys:
  - OpenRouter API key (para LLM)
  - Google API key (para embeddings)
- Docker (opcional, para el servicio de gestos arbitrales)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/carreroguille/ctai-python-langchain.git
cd ctai-python-langchain
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate 
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
CHROMA_PERSIST_DIR=./data/vectorstore/chroma_db
EMBEDDING_MODEL=models/text-embedding-004

# Langfuse (opcional - para observabilidad)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
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

#### **Langfuse:**
1. Regístrate en [Langfuse Cloud](https://cloud.langfuse.com/)
2. Crea un nuevo proyecto
3. Copia las claves pública y secreta

### 6. Configurar servicio de gestos arbitrales (Opcional)

Si tienes una API de gestos de árbitro en Docker:

```bash
docker start gesture_service
```

O ejecuta tu contenedor:
```bash
docker run -d --name gesture_service -p 8001:8000 gesture-api
```

### 7. Ingestar PDFs de normativa (IMPORTANTE)

**Antes de ejecutar el bot por primera vez**, debes cargar los documentos PDF en el vectorstore:

1. Coloca tus PDFs de normativa en la carpeta `data/raw/`
2. Ejecuta el script de ingesta:

```bash
python ingest_pdfs.py
```

Este script:
- Procesa todos los PDFs en `data/raw/`
- Los indexa en ChromaDB
- Muestra un resumen de documentos indexados
- Detecta y omite PDFs ya indexados

**Salida esperada:**
```
============================================================
SCRIPT DE INGESTA DE PDFs
============================================================
Directorio: C:\...\data\raw
============================================================

Encontrados 3 archivos PDF en C:\...\data\raw

============================================================
Procesando: RGC-25-WEB.pdf
============================================================
✅ RGC-25-WEB.pdf indexado exitosamente (150 chunks)

============================================================
RESUMEN DE INGESTA
============================================================
Total de archivos: 3
✅ Indexados exitosamente: 3
⚠️  Omitidos (ya indexados): 0
❌ Fallidos: 0
============================================================
```

> **Nota**: Solo necesitas ejecutar este script una vez, o cuando añadas nuevos PDFs a `data/raw/`. Los documentos se persisten en `data/vectorstore/`.


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
- `/reset` - Limpiar memoria de conversación

### Interacción

**Hacer preguntas:**
```
Usuario: ¿Cuántos pasos puede dar un jugador con el balón?
Bot: [Responde basándose en los documentos indexados con citas normativas]
```

**Consultar gestos arbitrales:**
```
Usuario: ¿Cómo se señala dos minutos?
Bot: [Devuelve información del gesto desde la API]
```

**Generar informes:**
```
Usuario: Genera un informe sobre una agresión en el minuto 45
Bot: [Crea un borrador con estructura formal y referencias normativas]
```

**Conversación contextual:**
```
Usuario: ¿Cuál es la sanción por conducta antideportiva?
Bot: [Responde]
Usuario: ¿Y si es reincidente?
Bot: [Mantiene el contexto de la pregunta anterior]
```

## 📁 Estructura del Proyecto

```
ctai-python-langchain/
├── agents/
│   ├── ai_agent.py          # Agente LLM con ReAct pattern y memoria conversacional
│   └── tools.py             # Herramientas RAG (búsqueda, stats, informes, gestos)
├── rag/
│   ├── vectorstore.py       # Gestión de ChromaDB y embeddings
│   └── retriever.py         # Capa de abstracción RAG
├── bot/
│   └── telegram_agent.py    # Integración con Telegram (handlers, comandos)
├── config/
│   └── settings.py          # Configuración y variables de entorno
├── utils/
│   ├── pdf_utils.py         # Procesamiento de PDFs
│   ├── formatting.py        # Formato de respuestas
│   └── gesture_api.py       # Cliente API de gestos arbitrales
├── data/
│   └── raw/                 # PDFs de reglamento (no versionados)
├── main.py                  # Punto de entrada del bot
└── requirements.txt         # Dependencias del proyecto
```

## 🛠️ Tecnologías Utilizadas

- **LangChain 0.2.17** - Framework para LLMs y agentes
- **python-telegram-bot 22.5** - Librería de Telegram
- **ChromaDB 1.3.5** - Base de datos vectorial
- **OpenRouter** - Proveedor de LLMs (Qwen 3 32B)
- **Google Generative AI** - Embeddings (text-embedding-004)
- **PyMuPDF 1.26.6** - Procesamiento de PDFs
- **Langfuse 2.60.10** - Observabilidad y trazabilidad LLM

## 🧪 Testing

### Test con Telegram
1. Ejecuta `python main.py`
2. Abre Telegram y busca tu bot
3. Envía `/start`
4. Prueba los comandos y envía preguntas

## 🏗️ Arquitectura

### Flujo de Procesamiento

1. **Usuario envía mensaje** → Telegram Bot
2. **Bot procesa** → AIAgent (LangChain ReAct)
3. **Agente razona** → Decide qué herramienta usar
4. **Herramientas disponibles**:
   - `search_documents`: Búsqueda semántica en PDFs
   - `get_stats`: Estadísticas del sistema
   - `generate_incident_report`: Generación de informes
   - `retrieve_referee_gesture`: Consulta API de gestos
5. **Retriever** → Consulta ChromaDB
6. **LLM genera respuesta** → OpenRouter (Qwen 3)
7. **Bot responde** → Usuario en Telegram

### Componentes Clave

- **AIAgent**: Orquesta el flujo usando patrón ReAct (Reasoning + Acting)
- **Retriever**: Abstracción sobre VectorStore para búsquedas RAG
- **VectorStore**: Gestiona ChromaDB y embeddings de Google
- **TelegramBot**: Maneja interacción con usuarios (comandos, PDFs, mensajes)
- **Tools**: Herramientas especializadas que el agente puede usar

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

### Gestos arbitrales no funcionan
- Verifica que el servicio Docker está corriendo: `docker ps`
- Verifica que la API está accesible en `http://127.0.0.1:8001/api/gesture/`
- Si no tienes el servicio, el bot seguirá funcionando pero sin esta funcionalidad

### Langfuse no traza
- Verifica que las credenciales están en `.env`
- El sistema funciona sin Langfuse, solo se desactiva el tracing
- Revisa logs para confirmar si está habilitado

## 📝 Notas

- El bot mantiene un directorio `data/vectorstore/` con los embeddings persistentes
- Los PDFs se procesan en chunks de 1500 caracteres con overlap de 200
- La memoria conversacional es por sesión (se pierde al reiniciar el bot)
- Usa `/reset` para limpiar la memoria sin reiniciar
- El sistema detecta PDFs duplicados y rechaza re-indexarlos
- Langfuse permite monitorear costos, latencias y calidad de respuestas

## 🔒 Seguridad

- **No versiones el archivo `.env`** (ya incluido en `.gitignore`)
- **No compartas tus API keys** públicamente
- Los PDFs se almacenan localmente y no se envían a servicios externos (excepto para embeddings)
- Considera usar variables de entorno del sistema en producción

## 📄 Licencia

[MIT](https://choosealicense.com/licenses/mit/)

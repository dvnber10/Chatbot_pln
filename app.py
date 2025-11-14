from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.Controllers.chat_controller import router as chatbot_router
import uvicorn

app = FastAPI(
    title="ChatBot Computex API",
    description="API RESTful para chatbot de ventas de computadoras con procesamiento NLP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(chatbot_router)

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API del ChatBot Computex",
        "endpoints": {
            "chat": "/api/chatbot/chat (POST)",
            "analyze": "/api/chatbot/analyze (POST)",
            "health": "/api/chatbot/health (GET)",
            "stats": "/api/chatbot/stats (GET)",
            "docs": "/docs"
        }
    }

@app.get("/info")
async def api_info():
    return {
        "name": "ChatBot Computex API",
        "version": "1.0.0",
        "description": "API para chatbot de ventas con procesamiento de lenguaje natural",
        "features": [
            "Procesamiento NLP con NLTK y spaCy",
            "Gestión de sesiones de chat",
            "Análisis de tokens y lematización",
            "Estadísticas en tiempo real",
            "API RESTful completa"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )
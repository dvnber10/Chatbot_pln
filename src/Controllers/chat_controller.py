from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
from src.Services.chat_service import ChatbotService
from src.Repositories.chat_repo import ChatbotRepository
from src.Models.chat_model import (
    ChatRequest, ChatResponse, ChatSession, NLPAnalysis, HealthCheck
)

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

# Inicializar repositorio y servicio
repository = ChatbotRepository()
chatbot_service = ChatbotService(repository)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(chat_request: ChatRequest):
    """
    Envía un mensaje al chatbot y recibe una respuesta procesada con NLP
    """
    try:
        return chatbot_service.process_message(chat_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando el mensaje: {str(e)}"
        )

@router.post("/analyze", response_model=NLPAnalysis)
async def analyze_message(message: str):
    """
    Análisis detallado NLP de un mensaje (tokens, lemas, POS tags)
    """
    try:
        return chatbot_service.analyze_message(message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en análisis NLP: {str(e)}"
        )

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Obtiene el historial completo de una sesión de chat
    """
    history = chatbot_service.get_chat_history(session_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    return history

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Obtiene información de una sesión específica
    """
    session_info = chatbot_service.get_session_info(session_id)
    if not session_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    return session_info

@router.get("/sessions")
async def get_all_sessions(active_only: bool = False):
    """
    Obtiene todas las sesiones (opcionalmente solo las activas)
    """
    sessions = repository.get_all_sessions()
    if active_only:
        # Sesiones activas en las últimas 2 horas
        cutoff = datetime.now() - timedelta(hours=2)
        sessions = [s for s in sessions if s.last_activity > cutoff]
    
    return [{
        "session_id": s.session_id,
        "message_count": len(s.messages),
        "created_at": s.created_at,
        "last_activity": s.last_activity
    } for s in sessions]

@router.get("/stats")
async def get_statistics():
    """
    Obtiene estadísticas del chatbot
    """
    return chatbot_service.get_stats()

@router.delete("/cleanup")
async def cleanup_sessions(hours: int = 24, background_tasks: BackgroundTasks = None):
    """
    Limpia sesiones inactivas (por defecto más de 24 horas)
    """
    if background_tasks:
        background_tasks.add_task(chatbot_service.cleanup_sessions, hours)
        return {"message": f"Limpieza programada para sesiones mayores a {hours} horas"}
    else:
        chatbot_service.cleanup_sessions(hours)
        return {"message": f"Sesiones mayores a {hours} horas eliminadas"}

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Verifica el estado del servicio y modelos NLP
    """
    try:
        # Probar que los modelos NLP funcionan
        test_message = "Hola"
        analysis = chatbot_service.analyze_message(test_message)
        
        return HealthCheck(
            status="healthy",
            nlp_models_loaded=True,
            timestamp=datetime.now()
        )
    except Exception as e:
        return HealthCheck(
            status="unhealthy",
            nlp_models_loaded=False,
            timestamp=datetime.now()
        )

@router.get("/keywords")
async def get_available_keywords():
    """
    Obtiene todas las palabras clave y categorías disponibles
    """
    from src.Utils.PLN_utils import response_chat
    # Esta es una forma de obtener las keywords, necesitarías modificar response_chat
    # o crear una función auxiliar que exponga el keyword_dict
    return {
        "categories": [
            "modelo", "Hola", "precio", "compra", "características",
            "computadora", "gracias", "dell", "hp", "lenovo", "pagar"
        ],
        "message": "Las keywords exactas están definidas en la función response_chat"
    }
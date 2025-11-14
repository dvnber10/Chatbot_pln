from typing import Dict, List, Optional
from datetime import datetime
import time
from src.Repositories.chat_repo import ChatbotRepository
from src.Models.chat_model import ChatRequest, ChatResponse, NLPAnalysis
from src.Utils.PLN_utils import response_chat

class ChatbotService:
    def __init__(self, repository: ChatbotRepository):
        self.repository = repository

    def process_message(self, chat_request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        
        # Obtener o crear session_id
        session_id = chat_request.session_id or self.repository.create_session()
        
        # Procesar el mensaje con NLP
        nlp_result = response_chat(chat_request.message)
        
        # Calcular tiempo de procesamiento
        processing_time = time.time() - start_time
        
        # Guardar mensaje del usuario en el historial
        user_message = {
            "type": "user",
            "message": chat_request.message,
            "timestamp": datetime.now(),
            "processing_time": processing_time
        }
        self.repository.save_message(session_id, user_message)
        
        # Guardar respuesta del bot
        bot_response = {
            "type": "bot",
            "message": nlp_result["response"],
            "category": nlp_result["category"],
            "matched_keyword": nlp_result.get("matched_keyword"),
            "timestamp": datetime.now(),
            "processing_time": processing_time
        }
        self.repository.save_message(session_id, bot_response)
        
        return ChatResponse(
            response=nlp_result["response"],
            session_id=session_id,
            category=nlp_result["category"],
            matched_keyword=nlp_result.get("matched_keyword"),
            timestamp=datetime.now(),
            processing_time=processing_time
        )

    

    def get_chat_history(self, session_id: str) -> List[dict]:
        return self.repository.get_chat_history(session_id)

    def get_session_info(self, session_id: str) -> Optional[dict]:
        session = self.repository.get_session(session_id)
        if session:
            return {
                "session_id": session.session_id,
                "message_count": len(session.messages),
                "created_at": session.created_at,
                "last_activity": session.last_activity,
                "user_messages": len([m for m in session.messages if m["type"] == "user"]),
                "bot_messages": len([m for m in session.messages if m["type"] == "bot"])
            }
        return None

    def get_stats(self) -> dict:
        return self.repository.get_stats()

    def cleanup_sessions(self, hours: int = 24):
        self.repository.cleanup_old_sessions(hours)
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import logging
import asyncio

# Import our custom modules
from models import get_db, create_tables
from database_service import DatabaseService
from ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI service
ai_service = AIService()

# Create FastAPI app
app = FastAPI(
    title="Mental Health Support Chatbot",
    description="A supportive AI chatbot for mental health and addiction recovery (one chat per user)",
    version="2.2.0"
)

# Enable CORS for all origins (allow any website to call the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class MessageRequest(BaseModel):
    message: str
    user_id: str  # Required user identifier

# Response schema
class MessageResponse(BaseModel):
    response: str
    response_html: str
    user_id: str
    message_id: int
    context_analysis: Optional[dict] = None

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(
    req: MessageRequest,
    db: Session = Depends(get_db)
):
    """
    Enhanced chat endpoint with user-specific conversation history and contextual analysis
    """
    try:
        # Initialize database service
        db_service = DatabaseService(db)
        
        # Get or create conversation for specific user
        conversation = db_service.get_or_create_conversation(req.user_id)
        
        # Save user message
        user_message = db_service.save_message(req.user_id, conversation.id, "user", req.message)
        
        # Get conversation history for context
        conversation_history = db_service.get_conversation_history(req.user_id, limit=10)
        
        # Analyze user's conversation patterns and sentiment (across all conversations)
        user_analysis = db_service.get_user_sentiment_history(req.user_id)
        
        # Analyze current message for immediate context
        current_message_analysis = ai_service.analyze_user_message(req.message)
        
        # Generate contextual response
        # Add a timeout to the Gemini API call
        loop = asyncio.get_event_loop()
        try:
            ai_response = await loop.run_in_executor(
                None,
                ai_service.generate_response,
                req.user_id,
                req.message,
                conversation_history,
                user_analysis,
                db_service
            )
        except Exception as e:
            logger.error(f"AI service error: {e}")
            ai_response = "I'm sorry, I'm having trouble responding right now. Please try again later."
        
        # Save AI response
        assistant_message = db_service.save_message(req.user_id, conversation.id, "assistant", ai_response)
        
        # Prepare context analysis for response
        context_analysis = {
            "user_id": req.user_id,
            "total_messages": user_analysis["total_messages"],
            "sentiment_trend": user_analysis["sentiment"],
            "engagement_level": user_analysis["engagement_level"],
            "common_topics": user_analysis["topics"],
            "current_message_analysis": current_message_analysis
        }
        
        # Crisis detection and response
        if current_message_analysis["is_crisis"]:
            logger.warning(f"Crisis detected for user {req.user_id}")
            # You could add emergency contact information or crisis hotline numbers here
            ai_response += "\n\n⚠️ If you're having thoughts of self-harm, please contact the National Suicide Prevention Lifeline at 988 or 1-800-273-8255. You're not alone, and help is available 24/7."
        
        # Add HTML-formatted response
        ai_response_html = ai_response.replace('\n', '<br>')
        
        return MessageResponse(
            response=ai_response,
            response_html=ai_response_html,
            user_id=req.user_id,
            message_id=assistant_message.id,
            context_analysis=context_analysis
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/conversation/{user_id}/history")
async def get_conversation_history(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get conversation history for a specific user and chat
    """
    try:
        db_service = DatabaseService(db)
        history = db_service.get_conversation_history(user_id, limit=limit)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/analysis")
async def get_user_analysis(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analysis of user's conversation patterns and sentiment
    """
    try:
        db_service = DatabaseService(db)
        analysis = db_service.get_user_sentiment_history(user_id)
        summary = db_service.get_user_conversation_summary(user_id)
        
        return {
            "user_id": user_id,
            "analysis": analysis,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting user analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/summary")
async def get_user_summary(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a summary of all user's conversations and patterns
    """
    try:
        db_service = DatabaseService(db)
        summary = db_service.get_user_conversation_summary(user_id)
        return {"user_id": user_id, "summary": summary}
    except Exception as e:
        logger.error(f"Error getting user summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

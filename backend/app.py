from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import os
from .llm_service import generate_response
from .safety import (
    validate_message, validate_persona, validate_history,
    detect_harmful_content, detect_injection_attempts,
    sanitize_message, validate_response
)

app = FastAPI()

# Add CORS middleware with strict settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Request rate limiting tracking (in production, use Redis)
requests_per_ip = {}

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message (1-1000 chars)")
    persona: str = Field(..., description="AI persona: teacher, doctor, or friend")
    history: list = Field(default=[], max_items=50, description="Conversation history")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/chat")
async def chat_ui(request: Request):
    return templates.TemplateResponse(request=request, name="chat.html")

@app.post("/api/chat")
async def chat(request: ChatRequest, req: Request):
    # Get client IP for rate limiting
    client_ip = req.client.host if req.client else "unknown"
    
    # Step 1: Validate input format
    is_valid, error = validate_message(request.message)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    is_valid, error = validate_persona(request.persona)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    is_valid, error = validate_history(request.history)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Step 2: Detect injection attempts
    is_injection, reason = detect_injection_attempts(request.message)
    if is_injection:
        raise HTTPException(status_code=400, detail=f"Request blocked: {reason}")
    
    # Step 3: Detect harmful content
    is_harmful, reason = detect_harmful_content(request.message)
    if is_harmful:
        raise HTTPException(status_code=400, detail=f"Request blocked: {reason}")
    
    # Step 4: Sanitize message
    sanitized_message = sanitize_message(request.message)
    
    # Step 5: Generate response with safety guardrails
    response_text = await generate_response(
        sanitized_message, 
        request.persona.lower(), 
        request.history
    )
    
    # Step 6: Validate response meets safety requirements
    response_text = validate_response(response_text, request.persona)
    
    return {
        "response": response_text,
        "safety_checked": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "message": "Chatbot service running"}

# This is for running locally or with gunicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

import httpx
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for security monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2:0.5b" # Lightweight model for local execution (matches your pulled model)
REQUEST_TIMEOUT = 60.0  # Timeout to prevent hanging requests

# Safety configuration
RESPONSE_MAX_LENGTH = 4000  # Prevent extremely long responses
RESPONSE_MIN_LENGTH = 10    # Prevent empty/minimal responses

SYSTEM_PROMPTS = {
    "teacher": (
        "You are an academic Teacher AI Assistant. "
        "Your responses should be structured, easy to understand, and step-by-step. "
        "Keep responses simple but highly educational. "
        "SAFETY: Do not provide instructions for harmful activities. "
        "Always prioritize educational value and user safety."
    ),
    "doctor": (
        "You are a Doctor AI Assistant. "
        "Your responses must be highly professional, clinical, and supportive. "
        "CRITICAL: ALWAYS append the following disclaimer at the very end of your response exactly as written: "
        "'Disclaimer: This is not a substitute for a licensed medical professional. Please seek real medical advice for critical issues.' "
        "SAFETY: Never prescribe medications or suggest treatments without clear medical disclaimers."
    ),
    "friend": (
        "You are a caring Friend AI Assistant. "
        "Your tone should be casual, warm, supportive, and highly empathetic. "
        "SAFETY: Do not provide harmful advice. If the user seems to be in crisis, "
        "encourage them to seek professional help immediately."
    )
}

async def generate_response(prompt: str, persona: str, history: list = None, model: str = None) -> str:
    """
    Generate response from Ollama with safety guardrails.
    
    Args:
        prompt: User input message
        persona: Selected AI persona (teacher, doctor, friend)
        history: Conversation history
        model: Override model name (optional)
    
    Returns:
        Response text with safety validation
    """
    if history is None:
        history = []
    
    # Sanitize persona input
    persona_normalized = persona.lower().strip()
    system_prompt = SYSTEM_PROMPTS.get(persona_normalized, SYSTEM_PROMPTS["friend"])
    
    # Validate and limit history to prevent context explosion
    validated_history = history[:50] if history else []  # Max 50 messages
    
    # Constructing a unified context for Ollama with safety limits
    history_text = ""
    for entry in validated_history:
        role = entry.get("role", "User")
        content = entry.get("content", "")
        
        # Truncate individual history entries that are too long
        if len(content) > 500:
            content = content[:500] + "..."
        
        role_label = "User" if role == "User" else "Assistant"
        history_text += f"{role_label}: {content}\n\n"
    
    # Build full prompt with safety constraints
    full_prompt = f"System Instruction: {system_prompt}\n\n{history_text}User: {prompt}\n\nAssistant:"
    
    payload = {
        "model": model or MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Ollama response parsing with validation
            response_text = data.get('response', "Error: Could not parse response from Ollama.")
            
            if not isinstance(response_text, str):
                return "Error: Invalid response format from model."
            
            # Enforce response length limits
            if len(response_text) > RESPONSE_MAX_LENGTH:
                response_text = response_text[:RESPONSE_MAX_LENGTH] + "\n[Response truncated for safety]"
            
            if len(response_text) < RESPONSE_MIN_LENGTH:
                return "I couldn't generate a proper response. Please try again."
            
            # Enforce safety constraint programmatically for doctor persona
            if persona_normalized == "doctor":
                disclaimer = "Disclaimer: This is not a substitute for a licensed medical professional. Please seek real medical advice for critical issues."
                if disclaimer not in response_text:
                    response_text += f"\n\n{disclaimer}"
            
            # Log response for safety monitoring (in production, use proper audit logging)
            logger.info(f"[{persona_normalized}] Response generated successfully")
            
            return response_text
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            return f"Error communicating with local Ollama: {e}. Please ensure Ollama is running and '{MODEL_NAME}' model is installed."
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            return f"Ollama error (HTTP {e.response.status_code}): {e.response.text}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"An unexpected error occurred: {str(e)}. Please try again."


"""
Safety and content filtering module for the chatbot.
Implements input validation, sanitization, and content filtering.
"""

import re
from typing import Tuple

# Configuration
MAX_MESSAGE_LENGTH = 1000
MIN_MESSAGE_LENGTH = 1
MAX_HISTORY_LENGTH = 50
VALID_PERSONAS = {"teacher", "doctor", "friend"}

# Harmful patterns to detect and block
HARMFUL_PATTERNS = [
    r"(?i)(self\s*harm|suicide|kill\s*yourself|hang\s*yourself)",
    r"(?i)(bomb|explosive|attack|weapon)",
    r"(?i)(how\s*to\s*make\s*drugs|cook|methamphetamine|cocaine)",
    r"(?i)(illegal\s*content|child\s*abuse)",
    r"(?i)(racism|racial\s*slur|hate\s*speech)",
]

# Injection attack patterns
INJECTION_PATTERNS = [
    r"<script[^>]*>.*?</script>",  # XSS attempts
    r"__.*?__",  # Python dunder attempts
    r"\{.*?\{.*?prompt.*?\}.*?\}",  # Template injection
    r"(?i)(eval|exec|__import__)",  # Code execution attempts
]


def validate_message(message: str) -> Tuple[bool, str]:
    """
    Validate user message for safety and format.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not isinstance(message, str):
        return False, "Message must be text."
    
    if not message.strip():
        return False, "Message cannot be empty."
    
    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters."
    
    if len(message) < MIN_MESSAGE_LENGTH:
        return False, "Message is too short."
    
    return True, ""


def validate_persona(persona: str) -> Tuple[bool, str]:
    """
    Validate that persona is one of the allowed personas.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not isinstance(persona, str):
        return False, "Persona must be text."
    
    if persona.lower() not in VALID_PERSONAS:
        valid_list = ", ".join(VALID_PERSONAS)
        return False, f"Invalid persona. Valid options: {valid_list}"
    
    return True, ""


def validate_history(history: list) -> Tuple[bool, str]:
    """
    Validate conversation history format and length.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not isinstance(history, list):
        return False, "History must be a list."
    
    if len(history) > MAX_HISTORY_LENGTH:
        return False, f"History exceeds maximum length of {MAX_HISTORY_LENGTH} messages."
    
    for entry in history:
        if not isinstance(entry, dict):
            return False, "Each history entry must be a dictionary."
        
        if "role" not in entry or "content" not in entry:
            return False, "Each history entry must have 'role' and 'content'."
        
        if entry["role"] not in ["User", "Assistant"]:
            return False, "History role must be 'User' or 'Assistant'."
        
        if not isinstance(entry["content"], str):
            return False, "History content must be text."
    
    return True, ""


def detect_harmful_content(message: str) -> Tuple[bool, str]:
    """
    Detect potentially harmful content in user message.
    
    Returns:
        Tuple[bool, str]: (is_harmful, reason)
    """
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, message):
            return True, "Request appears to involve harmful or dangerous content."
    
    return False, ""


def detect_injection_attempts(message: str) -> Tuple[bool, str]:
    """
    Detect potential injection attacks in user message.
    
    Returns:
        Tuple[bool, str]: (is_injection, reason)
    """
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, message):
            return True, "Request contains potentially malicious patterns."
    
    return False, ""


def sanitize_message(message: str) -> str:
    """
    Sanitize user message by removing or escaping dangerous patterns.
    Preserves legitimate content while removing injection attempts.
    """
    # Remove HTML tags
    sanitized = re.sub(r"<[^>]*>", "", message)
    
    # Remove excessive whitespace
    sanitized = " ".join(sanitized.split())
    
    # Escape special regex characters
    sanitized = sanitized.strip()
    
    return sanitized


def validate_response(response: str, persona: str) -> str:
    """
    Validate and potentially modify response based on safety requirements.
    Ensures critical disclaimers are included for specific personas.
    """
    if not isinstance(response, str):
        return "Error: Invalid response format."
    
    # Doctor persona must have disclaimer
    if persona.lower() == "doctor":
        disclaimer = "Disclaimer: This is not a substitute for a licensed medical professional. Please seek real medical advice for critical issues."
        if disclaimer not in response:
            response += f"\n\n{disclaimer}"
    
    # Teacher persona can include educational note
    if persona.lower() == "teacher" and len(response) < 50:
        # Ensure minimum quality for educational content
        response = f"[Educational Response] {response}"
    
    return response


def rate_limit_check(client_ip: str, request_count: dict) -> Tuple[bool, str]:
    """
    Simple rate limiting check (100 requests per minute per IP).
    In production, use Redis or similar backend.
    
    Returns:
        Tuple[bool, str]: (is_allowed, message)
    """
    MAX_REQUESTS_PER_MINUTE = 100
    
    # This is a basic implementation. For production, use proper rate limiting.
    if client_ip in request_count:
        count, timestamp = request_count[client_ip]
        if count >= MAX_REQUESTS_PER_MINUTE:
            return False, "Rate limit exceeded. Please try again later."
    
    return True, ""

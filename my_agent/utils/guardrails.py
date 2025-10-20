"""
Minimal guardrails for AI agent safety and reliability.
Implements: input validation, sensitive operation confirmation, content safety.
"""
from typing import Dict, Optional

# Sensitive operations requiring confirmation
SENSITIVE_KEYWORDS = ["delete", "remove", "send email", "send message"]

# Blocked unsafe keywords
UNSAFE_KEYWORDS = ["hack", "illegal", "steal", "password", "exploit"]

def validate_request(message) -> Dict[str, any]:
    """
    Validate user request with minimal checks.
    
    Args:
        message: User message (can be str or list)
    
    Returns:
        dict: {
            "allowed": bool,
            "reason": Optional[str],
            "requires_confirmation": bool,
            "confirmation_message": Optional[str]
        }
    """
    # Handle list messages (multimodal)
    if isinstance(message, list):
        # Extract text from list messages
        message = " ".join([str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in message])
    
    # Convert to string if needed
    message = str(message) if message else ""
    
    if not message or len(message.strip()) == 0:
        return {
            "allowed": False,
            "reason": "Please provide a valid message.",
            "requires_confirmation": False,
            "confirmation_message": None
        }
    
    # Check message length
    if len(message) > 1000:
        return {
            "allowed": False,
            "reason": "Message too long. Please keep it under 1000 characters.",
            "requires_confirmation": False,
            "confirmation_message": None
        }
    
    message_lower = message.lower()
    
    # Check for unsafe content
    for keyword in UNSAFE_KEYWORDS:
        if keyword in message_lower:
            return {
                "allowed": False,
                "reason": f"⚠️ This request is out of scope. I cannot help with: '{keyword}'",
                "requires_confirmation": False,
                "confirmation_message": None
            }
    
    # Check for sensitive operations
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in message_lower:
            return {
                "allowed": True,
                "reason": None,
                "requires_confirmation": True,
                "confirmation_message": f"⚠️ This action involves '{keyword}'. Please confirm you want to proceed by adding 'confirmed' to your message."
            }
    
    # Request is safe and allowed
    return {
        "allowed": True,
        "reason": None,
        "requires_confirmation": False,
        "confirmation_message": None
    }


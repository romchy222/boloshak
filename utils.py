import logging
from models import FAQ
from sqlalchemy import or_
from typing import List

logger = logging.getLogger(__name__)

def get_relevant_context(user_message: str, language: str = "ru", limit: int = 3) -> str:
    """Get relevant context from FAQ database based on user message"""
    try:
        user_message_lower = user_message.lower()
        
        # Choose question field based on language
        question_field = FAQ.question_ru if language == 'ru' else FAQ.question_kz
        answer_field = FAQ.answer_ru if language == 'ru' else FAQ.answer_kz
        
        # Search for relevant FAQs using simple text matching
        # In production, you might want to use more sophisticated search like full-text search
        relevant_faqs = FAQ.query.filter(
            FAQ.is_active == True,
            or_(
                question_field.ilike(f'%{word}%') 
                for word in user_message_lower.split() 
                if len(word) > 2  # Skip short words
            )
        ).limit(limit).all()
        
        if not relevant_faqs:
            # If no direct matches, try to find FAQs with any keyword
            keywords = [word for word in user_message_lower.split() if len(word) > 2]
            if keywords:
                relevant_faqs = FAQ.query.filter(
                    FAQ.is_active == True,
                    or_(*[question_field.ilike(f'%{keyword}%') for keyword in keywords[:3]])
                ).limit(limit).all()
        
        # Format context
        context_parts = []
        for faq in relevant_faqs:
            if language == 'ru':
                context_parts.append(f"В: {faq.question_ru}\nО: {faq.answer_ru}")
            else:
                context_parts.append(f"С: {faq.question_kz}\nЖ: {faq.answer_kz}")
        
        return "\n\n".join(context_parts) if context_parts else ""
        
    except Exception as e:
        logger.error(f"Error getting relevant context: {str(e)}")
        return ""

def format_response_time(seconds: float) -> str:
    """Format response time for display"""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    else:
        return f"{seconds:.2f}s"

def validate_language(language: str) -> str:
    """Validate and return supported language code"""
    return language if language in ['ru', 'kz'] else 'ru'

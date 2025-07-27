import os
import logging
import requests
import json
from typing import Optional

logger = logging.getLogger(__name__)

class MistralClient:
    """Client for interacting with Mistral AI API"""
    
    def __init__(self):
        self.api_key = os.environ.get("MISTRAL_API_KEY", "nxJcrPGFtx89fMeaLM2FdJS6STblMHAf")
        self.base_url = "https://api.mistral.ai/v1"
        self.model = "mistral-small-latest"
        
        # System prompts for different languages
        self.system_prompts = {
            'ru': """Ты - помощник для абитуриентов Кызылординского университета "Болашак". 
            Отвечай кратко, дружелюбно и информативно на русском языке. 
            Используй предоставленный контекст из базы FAQ для формирования ответов.
            Если информации нет в контексте, так и скажи, что нужно обратиться в приемную комиссию.""",
            
            'kz': """Сіз Қызылорда "Болашақ" университетінің абитуриенттеріне арналған көмекшісіз. 
            Қазақ тілінде қысқа, достық және ақпараттық жауап беріңіз.
            Жауаптарды қалыптастыру үшін FAQ дерекқорынан берілген контекстті пайдаланыңыз.
            Егер контекстте ақпарат болмаса, қабылдау комиссиясына жүгіну керектігін айтыңыз."""
        }
    
    def get_response(self, user_message: str, context: str = "", language: str = "ru") -> str:
        """Get response from Mistral AI"""
        try:
            # Prepare the system prompt
            system_prompt = self.system_prompts.get(language, self.system_prompts['ru'])
            
            # Create the message with context
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Контекст из FAQ:\n{context}\n\nВопрос пользователя: {user_message}"}
            ]
            
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # Make the request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(language)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error to Mistral API: {str(e)}")
            return self._get_fallback_response(language)
        except Exception as e:
            logger.error(f"Unexpected error in Mistral client: {str(e)}")
            return self._get_fallback_response(language)
    
    def _get_fallback_response(self, language: str = "ru") -> str:
        """Get fallback response when API is unavailable"""
        fallback_responses = {
            'ru': "Извините, я временно недоступен. Пожалуйста, обратитесь в приемную комиссию университета по телефону или электронной почте.",
            'kz': "Кешіріңіз, мен уақытша қолжетімсізбін. Университеттің қабылдау комиссиясына телефон немесе электрондық пошта арқылы хабарласыңыз."
        }
        return fallback_responses.get(language, fallback_responses['ru'])

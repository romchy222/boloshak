# Импорт необходимых модулей для работы с API и обработки данных
import os                    # Для работы с переменными окружения
import logging              # Для логирования событий и ошибок
import requests             # Для выполнения HTTP запросов к API
import json                 # Для работы с JSON данными
from typing import Optional # Для типизации возвращаемых значений

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

class MistralClient:
    """
    Клиент для взаимодействия с API Mistral AI
    
    Класс обеспечивает интеграцию с сервисом Mistral AI для генерации
    ответов чат-бота на основе пользовательских запросов и контекста из FAQ.
    
    Основные возможности:
    - Отправка запросов к Mistral AI API
    - Поддержка русского и казахского языков
    - Обработка ошибок и fallback ответы
    - Настройка параметров генерации текста
    """

    def __init__(self):
        """
        Инициализация клиента Mistral AI
        
        Настраивает API ключ, базовый URL, модель и системные подсказки
        для каждого поддерживаемого языка.
        """
        # Получение API ключа из переменной окружения или использование значения по умолчанию
        # В продакшене рекомендуется всегда использовать переменные окружения
        self.api_key = os.environ.get("MISTRAL_API_KEY", "nxJcrPGFtx89fMeaLM2FdJS6STblMHAf")
        
        # Базовый URL для API Mistral AI
        self.base_url = "https://api.mistral.ai/v1"
        
        # Используемая модель - оптимальная по соотношению качество/скорость
        self.model = "mistral-small-latest"

        # Системные подсказки для разных языков
        # Определяют поведение и стиль ответов бота
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
        """
        Получение ответа от Mistral AI на основе сообщения пользователя и контекста
        
        Отправляет запрос к API Mistral AI с учетом контекста из FAQ и
        системной подсказки для соответствующего языка.
        
        Аргументы:
            user_message (str): Сообщение/вопрос пользователя
            context (str): Релевантный контекст из базы FAQ и знаний
            language (str): Язык ответа ('ru' для русского, 'kz' для казахского)
            
        Возвращает:
            str: Сгенерированный ответ от AI или fallback сообщение при ошибке
        """
        try:
            # Получение системной подсказки для указанного языка
            # Если язык не поддерживается, используется русский по умолчанию
            system_prompt = self.system_prompts.get(language, self.system_prompts['ru'])

            # Формирование массива сообщений для API
            # Включает системную подсказку и пользовательский запрос с контекстом
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Контекст из FAQ:\n{context}\n\nВопрос пользователя: {user_message}"}
            ]

            # Подготовка заголовков для HTTP запроса
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Подготовка данных для отправки к API
            data = {
                "model": self.model,                # Используемая модель
                "messages": messages,               # Диалог для обработки
                "max_tokens": 500,                 # Максимальная длина ответа
                "temperature": 0.7                 # Креативность ответа (0.0 - детерминированный, 1.0 - творческий)
            }

            # Выполнение POST запроса к API Mistral
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # Таймаут 30 секунд для предотвращения зависания
            )

            # Проверка успешности запроса
            if response.status_code == 200:
                # Парсинг JSON ответа и извлечение сгенерированного текста
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                # Логирование ошибки API и возврат fallback ответа
                logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(language)

        except requests.exceptions.RequestException as e:
            # Обработка ошибок сетевого соединения
            logger.error(f"Request error to Mistral API: {str(e)}")
            return self._get_fallback_response(language)
        except Exception as e:
            # Обработка любых других неожиданных ошибок
            logger.error(f"Unexpected error in Mistral client: {str(e)}")
            return self._get_fallback_response(language)

    def _get_fallback_response(self, language: str = "ru") -> str:
        """
        Получение резервного ответа при недоступности API
        
        Возвращает предустановленное сообщение на случай, когда API Mistral
        недоступен или возвращает ошибку. Помогает поддерживать работоспособность
        чат-бота даже при проблемах с внешним сервисом.
        
        Аргументы:
            language (str): Язык сообщения ('ru' или 'kz')
            
        Возвращает:
            str: Fallback сообщение на соответствующем языке
        """
        # Словарь с резервными ответами для каждого поддерживаемого языка
        fallback_responses = {
            'ru': "Извините, я временно недоступен. Пожалуйста, обратитесь в приемную комиссию университета по телефону или электронной почте.",
            'kz': "Кешіріңіз, мен уақытша қолжетімсізбін. Университеттің қабылдау комиссиясына телефон немесе электрондық пошта арқылы хабарласыңыз."
        }
        
        # Возврат сообщения для указанного языка или русского по умолчанию
        return fallback_responses.get(language, fallback_responses['ru'])
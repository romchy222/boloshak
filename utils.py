# Импорт модуля логирования для отслеживания работы функций
import logging
# Импорт моделей базы данных для работы с FAQ и базой знаний
from models import FAQ, KnowledgeBase
# Импорт операторов SQLAlchemy для построения запросов
from sqlalchemy import or_
# Импорт типов для аннотации функций
from typing import List

# Настройка логгера для данного модуля
logger = logging.getLogger(__name__)

def get_relevant_context(user_message: str, language: str = "ru", limit: int = 3) -> str:
    """
    Получение релевантного контекста из базы данных FAQ и базы знаний
    
    Функция ищет подходящие ответы в FAQ и базе знаний на основе сообщения пользователя.
    Использует простой поиск по ключевым словам для нахождения релевантного контекста.
    
    Аргументы:
        user_message (str): Сообщение пользователя для поиска контекста
        language (str): Язык поиска ('ru' для русского, 'kz' для казахского)
        limit (int): Максимальное количество результатов для возврата
        
    Возвращает:
        str: Найденный контекст, объединенный в строку, или пустую строку если ничего не найдено
    """
    try:
        # Приведение сообщения к нижнему регистру для поиска
        user_message_lower = user_message.lower()
        # Список для хранения найденных частей контекста
        context_parts = []
        
        # Определение полей для поиска в зависимости от языка
        question_field = FAQ.question_ru if language == 'ru' else FAQ.question_kz
        answer_field = FAQ.answer_ru if language == 'ru' else FAQ.answer_kz
        
        # Извлечение ключевых слов из сообщения (слова длиннее 2 символов)
        keywords = [word for word in user_message_lower.split() if len(word) > 2]
        
        if keywords:
            # Построение условий поиска для SQL запроса
            search_conditions = []
            # Ограничиваем поиск первыми 3 ключевыми словами для производительности
            for word in keywords[:3]:
                # Добавление условия поиска с использованием ILIKE (регистронезависимый поиск)
                search_conditions.append(question_field.ilike(f'%{word}%'))
            
            # Выполнение запроса к базе FAQ
            relevant_faqs = FAQ.query.filter(
                FAQ.is_active == True,  # Только активные FAQ
                or_(*search_conditions)  # Любое из условий поиска
            ).limit(limit).all()
            
            # Форматирование найденных FAQ в контекст
            for faq in relevant_faqs:
                if language == 'ru':
                    context_parts.append(f"FAQ - В: {faq.question_ru}\nО: {faq.answer_ru}")
                else:
                    context_parts.append(f"FAQ - С: {faq.question_kz}\nЖ: {faq.answer_kz}")
        
        # Поиск дополнительного контекста в базе знаний
        kb_context = get_knowledge_base_context(user_message, language, limit)
        if kb_context:
            context_parts.extend(kb_context)
        
        # Объединение всех частей контекста в одну строку
        return "\n\n".join(context_parts) if context_parts else ""
        
    except Exception as e:
        # Логирование ошибки при получении контекста
        logger.error(f"Error getting relevant context: {str(e)}")
        return ""

def get_knowledge_base_context(user_message: str, language: str = "ru", limit: int = 3) -> List[str]:
    """
    Получение релевантного контекста из базы знаний
    
    Ищет подходящие фрагменты в базе знаний (документы, веб-источники)
    на основе ключевых слов из сообщения пользователя.
    
    Аргументы:
        user_message (str): Сообщение пользователя для поиска
        language (str): Язык поиска (пока не используется активно)
        limit (int): Максимальное количество фрагментов для возврата
        
    Возвращает:
        List[str]: Список найденных фрагментов текста из базы знаний
    """
    try:
        # Приведение сообщения к нижнему регистру
        user_message_lower = user_message.lower()
        # Извлечение ключевых слов (слова длиннее 2 символов)
        keywords = [word for word in user_message_lower.split() if len(word) > 2]
        
        # Если ключевые слова не найдены, возвращаем пустой список
        if not keywords:
            return []
        
        # Построение условий поиска по базе знаний
        search_conditions = []
        for keyword in keywords[:3]:  # Ограничиваем первыми 3 ключевыми словами
            # Поиск ключевого слова в содержимом фрагментов
            search_conditions.append(KnowledgeBase.content_chunk.ilike(f'%{keyword}%'))
        
        # Выполнение запроса к базе знаний
        relevant_entries = KnowledgeBase.query.filter(
            KnowledgeBase.is_active == True,  # Только активные записи
            or_(*search_conditions)  # Любое из условий поиска
        ).limit(limit).all()
        
        # Форматирование найденных записей
        context_parts = []
        for entry in relevant_entries:
            # Определение типа источника для отображения
            source_label = "Документ" if entry.source_type == 'document' else "Веб-сайт"
            context_parts.append(f"{source_label} - {entry.content_chunk}")
        
        return context_parts
        
    except Exception as e:
        # Логирование ошибки при поиске в базе знаний
        logger.error(f"Error getting knowledge base context: {str(e)}")
        return []

def format_response_time(seconds: float) -> str:
    """
    Форматирование времени ответа для отображения пользователю
    
    Конвертирует время в секундах в удобочитаемый формат:
    - Если меньше 1 секунды - показывает в миллисекундах
    - Если 1 секунда и больше - показывает в секундах с 2 знаками после запятой
    
    Аргументы:
        seconds (float): Время в секундах
        
    Возвращает:
        str: Отформатированная строка времени (например, "150ms" или "2.35s")
    """
    if seconds < 1:
        # Конвертация в миллисекунды для времени меньше секунды
        return f"{int(seconds * 1000)}ms"
    else:
        # Отображение в секундах с точностью до 2 знаков после запятой
        return f"{seconds:.2f}s"

def validate_language(language: str) -> str:
    """
    Валидация и возврат поддерживаемого кода языка
    
    Проверяет, что переданный код языка поддерживается системой.
    Если язык не поддерживается, возвращает русский язык по умолчанию.
    
    Аргументы:
        language (str): Код языка для проверки
        
    Возвращает:
        str: Валидный код языка ('ru' или 'kz')
    """
    # Проверка, что язык входит в список поддерживаемых
    return language if language in ['ru', 'kz'] else 'ru'

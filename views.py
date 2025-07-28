# Импорт необходимых модулей Flask и вспомогательных библиотек
import time  # Для измерения времени ответа
import logging  # Для логирования событий и ошибок
from flask import Blueprint, render_template, request, jsonify, session
# Импорт моделей базы данных
from models import FAQ, UserQuery
# Импорт объекта базы данных
from app import db
# Импорт клиента для взаимодействия с Mistral AI
from mistral_client import MistralClient
# Импорт утилит для получения релевантного контекста
from utils import get_relevant_context

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

# Создание Blueprint для основных маршрутов приложения
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Главная страница с чат-виджетом
    
    Отображает основную страницу приложения, содержащую
    интерфейс чат-бота для взаимодействия с пользователями.
    
    Возвращает:
        HTML страницу с встроенным чат-виджетом
    """
    return render_template('index.html')

@main_bp.route('/widget-demo')
def widget_demo():
    """
    Демонстрационная страница виджета
    
    Показывает пример интеграции чат-виджета на внешнем сайте.
    Используется для тестирования и демонстрации возможностей виджета.
    
    Возвращает:
        HTML страницу с демонстрацией виджета
    """
    return render_template('widget-demo.html')

@main_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    API эндпоинт для обработки сообщений чата
    
    Основная функция обработки сообщений от пользователей:
    1. Получает сообщение пользователя и язык
    2. Ищет релевантный контекст в базе FAQ
    3. Отправляет запрос к Mistral AI для генерации ответа
    4. Сохраняет диалог в базу данных
    5. Возвращает ответ пользователю
    
    Ожидаемые данные в POST запросе:
        message (str): Сообщение пользователя
        language (str, optional): Язык интерфейса ('ru' или 'kz')
        
    Возвращает:
        JSON ответ с полями:
        - response: Ответ бота
        - response_time: Время обработки запроса
        Или ошибку в случае неудачи
    """
    try:
        # Получение JSON данных из запроса
        data = request.get_json()
        
        # Валидация наличия обязательных данных
        if not data or 'message' not in data:
            return jsonify({'error': 'Сообщение не найдено'}), 400

        # Извлечение сообщения пользователя и очистка от лишних пробелов
        user_message = data['message'].strip()
        # Получение языка интерфейса (по умолчанию русский)
        language = data.get('language', 'ru')

        # Проверка на пустое сообщение
        if not user_message:
            return jsonify({'error': 'Пустое сообщение'}), 400

        # Начало отсчета времени обработки для статистики
        start_time = time.time()

        # Поиск релевантного контекста из базы FAQ и базы знаний
        context = get_relevant_context(user_message, language)

        # Инициализация клиента Mistral AI и получение ответа
        mistral_client = MistralClient()
        bot_response = mistral_client.get_response(user_message, context, language)

        # Вычисление времени обработки запроса
        response_time = time.time() - start_time

        # Создание записи в базе данных для анализа и статистики
        user_query = UserQuery(
            user_message=user_message,           # Сообщение пользователя
            bot_response=bot_response,           # Ответ бота
            language=language,                   # Язык диалога
            response_time=response_time,         # Время обработки
            session_id=session.get('session_id', ''),  # ID сессии пользователя
            ip_address=request.remote_addr,      # IP адрес пользователя
            user_agent=request.headers.get('User-Agent', '')  # Браузер пользователя
        )

        # Сохранение записи в базу данных
        db.session.add(user_query)
        db.session.commit()

        # Логирование успешной обработки запроса
        logger.info(f"Chat response generated in {response_time:.2f}s for language: {language}")

        # Возврат ответа клиенту
        return jsonify({
            'response': bot_response,
            'response_time': response_time
        })

    except Exception as e:
        # Логирование ошибки для анализа проблем
        logger.error(f"Error in chat endpoint: {str(e)}")
        
        # Формирование сообщения об ошибке на соответствующем языке
        error_message = ("Извините, произошла ошибка. Попробуйте еще раз." 
                        if language == 'ru' 
                        else "Кешіріңіз, қате орын алды. Қайталап көріңіз.")
        
        # Возврат ошибки клиенту
        return jsonify({'error': error_message}), 500

@main_bp.route('/api/health')
def health_check():
    """
    Эндпоинт для проверки состояния сервиса
    
    Используется для мониторинга и проверки доступности API.
    Возвращает статус сервиса и текущее время.
    
    Возвращает:
        JSON ответ с полями:
        - status: Статус сервиса ('healthy')
        - timestamp: Текущее время в формате Unix timestamp
    """
    return jsonify({'status': 'healthy', 'timestamp': time.time()})
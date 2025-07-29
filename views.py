# Импорт необходимых модулей
import time
import logging
from flask import Blueprint, render_template, request, jsonify, session
from models import FAQ, UserQuery
from app import db
from mistral_client import MistralClient
from utils import get_relevant_context


# Настройка логирования
logger = logging.getLogger(__name__)

# Создание Blueprint для основных маршрутов
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Main page with chat widget"""
    return render_template('index.html')


@main_bp.route('/chat')
def chat_page():
    """ page with chat """
    return render_template('chat.html')


@main_bp.route('/widget-demo')
def widget_demo():
    """Widget integration demo page"""
    return render_template('widget-demo.html')


@main_bp.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Сообщение не найдено'}), 400

        user_message = data['message'].strip()
        language = data.get('language', 'ru')

        if not user_message:
            return jsonify({'error': 'Пустое сообщение'}), 400

        # Record start time for performance tracking
        start_time = time.time()

        # Get relevant context from FAQ database
        context = get_relevant_context(user_message, language)

        # Initialize Mistral client and get response
        mistral_client = MistralClient()
        bot_response = mistral_client.get_response(user_message, context,
                                                   language)

        # Calculate response time
        response_time = time.time() - start_time

        # Log the interaction
        user_query = UserQuery(user_message=user_message,
                               bot_response=bot_response,
                               language=language,
                               response_time=response_time,
                               session_id=session.get('session_id', ''),
                               ip_address=request.remote_addr,
                               user_agent=request.headers.get(
                                   'User-Agent', ''))

        db.session.add(user_query)
        db.session.commit()

        logger.info(
            f"Chat response generated in {response_time:.2f}s for language: {language}"
        )

        return jsonify({
            'response': bot_response,
            'response_time': response_time
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        error_message = "Извините, произошла ошибка. Попробуйте еще раз." if language == 'ru' else "Кешіріңіз, қате орын алды. Қайталап көріңіз."
        return jsonify({'error': error_message}), 500


@main_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

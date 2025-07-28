# Импорт модулей Flask для создания Blueprint, работы с запросами и сессиями
from flask import Blueprint, request, jsonify, session
# Импорт модели пользователя-администратора
from models import AdminUser
# Импорт объекта базы данных
from app import db
# Импорт модуля логирования для отслеживания ошибок
import logging

# Создание Blueprint для маршрутов аутентификации с префиксом /auth
auth_bp = Blueprint('auth', __name__)
# Настройка логгера для данного модуля
logger = logging.getLogger(__name__)

@auth_bp.route('/verify-session', methods=['GET'])
def verify_session():
    """
    Проверка активной сессии администратора
    
    Возвращает:
        JSON ответ с информацией о статусе аутентификации:
        - authenticated: True/False - статус аутентификации
        - username: имя пользователя (если аутентифицирован)
    """
    try:
        # Получение ID администратора из сессии
        admin_id = session.get('admin_id')
        
        # Если ID есть в сессии, проверяем существование активного пользователя
        if admin_id:
            # Поиск активного администратора в базе данных
            admin = AdminUser.query.filter_by(id=admin_id, is_active=True).first()
            
            # Если администратор найден, возвращаем положительный ответ
            if admin:
                return jsonify({'authenticated': True, 'username': admin.username})
        
        # Если администратор не найден или ID отсутствует в сессии
        return jsonify({'authenticated': False})
        
    except Exception as e:
        # Логирование ошибки при проверке сессии
        logger.error(f"Error verifying session: {str(e)}")
        # Возврат отрицательного ответа в случае ошибки
        return jsonify({'authenticated': False})

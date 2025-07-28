# Импорт объекта базы данных и моделей для работы с БД
from app import db
from models import Category, FAQ, UserQuery, AdminUser
# Импорт модуля логирования для отслеживания операций
import logging

# Настройка логгера для данного модуля
logger = logging.getLogger(__name__)

def init_database():
    """
    Инициализация базы данных с созданием всех таблиц
    
    Создает все таблицы, определенные в моделях SQLAlchemy.
    Используется при первом запуске приложения.
    
    Возвращает:
        bool: True если таблицы созданы успешно, False в случае ошибки
    """
    try:
        # Создание всех таблиц в базе данных согласно определенным моделям
        db.create_all()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        # Логирование ошибки при создании таблиц
        logger.error(f"Error creating database tables: {str(e)}")
        return False

def reset_database():
    """
    Сброс базы данных с полным пересозданием всех таблиц
    
    ВНИМАНИЕ: Удаляет все существующие данные!
    Сначала удаляет все таблицы, затем создает их заново.
    Используется для полной очистки БД в процессе разработки.
    
    Возвращает:
        bool: True если БД сброшена успешно, False в случае ошибки
    """
    try:
        # Удаление всех существующих таблиц
        db.drop_all()
        # Создание таблиц заново
        db.create_all()
        logger.info("Database reset successfully")
        return True
    except Exception as e:
        # Логирование ошибки при сбросе БД
        logger.error(f"Error resetting database: {str(e)}")
        return False

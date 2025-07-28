# Импорт необходимых библиотек для создания и настройки Flask приложения
import os                                          # Для работы с переменными окружения
import logging                                     # Для настройки системы логирования
from flask import Flask                           # Основной класс Flask приложения
from flask_sqlalchemy import SQLAlchemy          # ORM для работы с базой данных
from flask_cors import CORS                       # Для настройки CORS (кросс-доменные запросы)
from sqlalchemy.orm import DeclarativeBase       # Базовый класс для моделей SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix  # Middleware для работы за прокси

# Настройка системы логирования на уровне DEBUG для подробного отслеживания
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей базы данных
    
    Используется SQLAlchemy для создания базового класса, от которого
    наследуются все модели. Обеспечивает единообразную структуру таблиц.
    """
    pass

# Инициализация объекта базы данных с указанием базового класса для моделей
db = SQLAlchemy(model_class=Base)

def create_app():
    """
    Функция создания и настройки Flask приложения (Application Factory Pattern)
    
    Реализует паттерн Application Factory для создания экземпляра Flask приложения
    с полной настройкой всех компонентов: базы данных, CORS, маршрутов и middleware.
    
    Настраиваемые компоненты:
    - Секретный ключ для сессий
    - Конфигурация базы данных SQLAlchemy
    - CORS для кросс-доменных запросов
    - Регистрация Blueprint'ов (модулей маршрутов)
    - Инициализация базы данных и тестовых данных
    
    Возвращает:
        Flask: Настроенный экземпляр Flask приложения
    """
    
    # Создание экземпляра Flask приложения
    app = Flask(__name__)
    
    # Установка секретного ключа для работы с сессиями и CSRF защиты
    # В продакшене обязательно должен браться из переменных окружения
    app.secret_key = os.environ.get("SESSION_SECRET",
                                    "dev-secret-key-change-in-production")
    
    # Настройка ProxyFix middleware для корректной работы за обратным прокси
    # x_proto=1: доверять заголовку X-Forwarded-Proto для определения протокола (HTTP/HTTPS)
    # x_host=1: доверять заголовку X-Forwarded-Host для определения хоста
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # === НАСТРОЙКА БАЗЫ ДАННЫХ ===
    
    # Получение URL базы данных из переменной окружения или использование SQLite по умолчанию
    database_url = os.environ.get("DATABASE_URL", "sqlite:///bolashakbot.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    
    # Настройки движка базы данных для повышения надежности соединения
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,      # Переподключение к БД каждые 5 минут (предотвращение таймаутов)
        "pool_pre_ping": True,    # Проверка соединения перед использованием (проверка доступности БД)
    }
    
    # Отключение отслеживания изменений объектов (экономия памяти)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Инициализация объекта базы данных с приложением
    db.init_app(app)

    # === НАСТРОЙКА CORS (Cross-Origin Resource Sharing) ===
    
    # Настройка CORS для разрешения кросс-доменных запросов от веб-виджета
    CORS(
        app,
        origins=[
            # Основной домен Replit для разработки
            "https://7a0463a0-cbab-40ed-8964-1461cf93cb8a-00-tv6bvx5wqo3s.pike.replit.dev",
            
            # Разрешение для всех поддоменов Replit (удобно для разработки)
            "https://*.replit.dev",
            
            # Локальные адреса для разработки (любой порт)
            "http://localhost:*",
            "https://localhost:*"
        ],
        # Разрешение передачи cookies и авторизационных данных
        supports_credentials=True
    )

    # === РЕГИСТРАЦИЯ МОДУЛЕЙ МАРШРУТОВ (BLUEPRINTS) ===
    
    # Импорт модулей с маршрутами (делается здесь для избежания циклических импортов)
    from views import main_bp    # Основные страницы и API чата
    from admin import admin_bp   # Административная панель
    from auth import auth_bp     # Система аутентификации

    # Регистрация Blueprint'ов в приложении
    app.register_blueprint(main_bp)                           # Основные маршруты (/, /api/chat)
    app.register_blueprint(admin_bp, url_prefix='/admin')     # Админ панель (/admin/*)
    app.register_blueprint(auth_bp, url_prefix='/auth')       # Аутентификация (/auth/*)

    # === ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ И ДАННЫХ ===
    
    # Выполнение инициализации в контексте приложения (необходимо для SQLAlchemy)
    with app.app_context():
        # Импорт моделей для регистрации их в SQLAlchemy
        # Должен быть выполнен после инициализации db
        import models

        # Создание всех таблиц в базе данных согласно определенным моделям
        db.create_all()

        # Инициализация базы данных тестовыми/начальными данными
        from setup_db import init_default_data
        init_default_data()

    # Возврат полностью настроенного приложения
    return app

# === СОЗДАНИЕ ЭКЗЕМПЛЯРА ПРИЛОЖЕНИЯ ===

# Создание основного экземпляра приложения с использованием Application Factory
app = create_app()

# === ТОЧКА ВХОДА ДЛЯ ЗАПУСКА В РЕЖИМЕ РАЗРАБОТКИ ===

if __name__ == '__main__':
    """
    Запуск приложения в режиме разработки
    
    Параметры запуска:
    - host='0.0.0.0': Прослушивание на всех сетевых интерфейсах
    - port=5000: Использование порта 5000
    - debug=True: Режим отладки с автоперезагрузкой при изменении кода
    """
    app.run(host='0.0.0.0', port=5000, debug=True)

# Импорт необходимых модулей для работы с базой данных и безопасностью
from datetime import datetime                                      # Для работы с датами и временем
from app import db                                                # Объект базы данных SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  # Для хеширования паролей

class Category(db.Model):
    """
    Модель категории для организации FAQ
    
    Представляет категории вопросов-ответов в системе FAQ.
    Поддерживает многоязычность (русский и казахский языки).
    Используется для группировки связанных вопросов.
    
    Атрибуты:
        id: Уникальный идентификатор категории
        name_ru: Название категории на русском языке
        name_kz: Название категории на казахском языке
        description_ru: Описание категории на русском языке
        description_kz: Описание категории на казахском языке
        created_at: Дата и время создания записи
        faqs: Связанные FAQ записи (отношение один-ко-многим)
    """
    __tablename__ = 'categories'
    
    # Первичный ключ - уникальный идентификатор категории
    id = db.Column(db.Integer, primary_key=True)
    
    # Название категории на русском языке (обязательное поле)
    name_ru = db.Column(db.String(100), nullable=False)
    
    # Название категории на казахском языке (обязательное поле)
    name_kz = db.Column(db.String(100), nullable=False)
    
    # Описание категории на русском языке (необязательное)
    description_ru = db.Column(db.Text)
    
    # Описание категории на казахском языке (необязательное)
    description_kz = db.Column(db.Text)
    
    # Дата создания записи (автоматически устанавливается при создании)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь один-ко-многим с FAQ (одна категория может содержать много FAQ)
    # lazy=True означает ленивую загрузку связанных объектов
    faqs = db.relationship('FAQ', backref='category', lazy=True)
    
    def __repr__(self):
        """
        Строковое представление категории для отладки
        
        Возвращает:
            str: Название категории на русском языке в формате <Category название>
        """
        return f'<Category {self.name_ru}>'

class FAQ(db.Model):
    """
    Модель часто задаваемых вопросов (FAQ)
    
    Хранит вопросы и ответы на двух языках (русский и казахский).
    Каждый FAQ привязан к определенной категории и может быть активирован/деактивирован.
    
    Атрибуты:
        id: Уникальный идентификатор FAQ
        question_ru: Вопрос на русском языке
        question_kz: Вопрос на казахском языке
        answer_ru: Ответ на русском языке
        answer_kz: Ответ на казахском языке
        category_id: ID связанной категории
        is_active: Флаг активности FAQ
        created_at: Дата создания
        updated_at: Дата последнего обновления
    """
    __tablename__ = 'faqs'
    
    # Первичный ключ - уникальный идентификатор FAQ
    id = db.Column(db.Integer, primary_key=True)
    
    # Вопрос на русском языке (обязательное поле)
    question_ru = db.Column(db.Text, nullable=False)
    
    # Вопрос на казахском языке (обязательное поле)
    question_kz = db.Column(db.Text, nullable=False)
    
    # Ответ на русском языке (обязательное поле)
    answer_ru = db.Column(db.Text, nullable=False)
    
    # Ответ на казахском языке (обязательное поле)
    answer_kz = db.Column(db.Text, nullable=False)
    
    # Внешний ключ на категорию (обязательная связь)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Флаг активности FAQ (по умолчанию активен)
    is_active = db.Column(db.Boolean, default=True)
    
    # Дата создания записи
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Дата последнего обновления (автоматически обновляется при изменении)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """
        Строковое представление FAQ для отладки
        
        Возвращает:
            str: Первые 50 символов вопроса на русском языке
        """
        return f'<FAQ {self.question_ru[:50]}...>'

class UserQuery(db.Model):
    """
    Модель для хранения запросов пользователей и ответов бота
    
    Используется для аналитики, мониторинга качества ответов и улучшения системы.
    Сохраняет полную информацию о диалоге между пользователем и ботом.
    
    Атрибуты:
        id: Уникальный идентификатор запроса
        user_message: Сообщение пользователя
        bot_response: Ответ бота
        language: Язык диалога
        response_time: Время генерации ответа в секундах
        session_id: Идентификатор сессии пользователя
        ip_address: IP адрес пользователя
        user_agent: Информация о браузере пользователя
        created_at: Дата и время создания записи
    """
    __tablename__ = 'user_queries'
    
    # Первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    
    # Сообщение пользователя (обязательное поле)
    user_message = db.Column(db.Text, nullable=False)
    
    # Ответ бота (обязательное поле)
    bot_response = db.Column(db.Text, nullable=False)
    
    # Язык диалога (по умолчанию русский)
    language = db.Column(db.String(5), nullable=False, default='ru')
    
    # Время генерации ответа в секундах (для анализа производительности)
    response_time = db.Column(db.Float)
    
    # Идентификатор сессии пользователя (для группировки диалогов)
    session_id = db.Column(db.String(100))
    
    # IP адрес пользователя (для аналитики и безопасности)
    ip_address = db.Column(db.String(45))  # Достаточно для IPv6
    
    # Информация о браузере пользователя
    user_agent = db.Column(db.String(500))
    
    # Дата и время создания записи
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        """
        Строковое представление запроса пользователя
        
        Возвращает:
            str: Первые 30 символов сообщения пользователя
        """
        return f'<UserQuery {self.user_message[:30]}...>'

class Document(db.Model):
    """
    Модель для хранения информации о загруженных документах
    
    Управляет документами, которые используются для формирования базы знаний бота.
    Поддерживает различные типы файлов и отслеживает статус их обработки.
    
    Атрибуты:
        id: Уникальный идентификатор документа
        title: Название документа
        filename: Имя файла на диске
        file_path: Полный путь к файлу
        file_type: MIME тип файла
        file_size: Размер файла в байтах
        content_text: Извлеченный текстовый контент
        is_processed: Флаг завершения обработки
        is_active: Флаг активности документа
        uploaded_by: ID администратора, загрузившего файл
        created_at: Дата загрузки
        updated_at: Дата последнего обновления
    """
    __tablename__ = 'documents'
    
    # Первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    
    # Название документа (пользовательское, обязательное)
    title = db.Column(db.String(200), nullable=False)
    
    # Имя файла на диске (обязательное)
    filename = db.Column(db.String(200), nullable=False)
    
    # Полный путь к файлу в файловой системе
    file_path = db.Column(db.String(500), nullable=False)
    
    # MIME тип файла (pdf, doc, txt и т.д.)
    file_type = db.Column(db.String(50), nullable=False)
    
    # Размер файла в байтах
    file_size = db.Column(db.Integer)
    
    # Извлеченный текстовый контент документа
    content_text = db.Column(db.Text)
    
    # Флаг завершения обработки документа (извлечение текста)
    is_processed = db.Column(db.Boolean, default=False)
    
    # Флаг активности документа (для мягкого удаления)
    is_active = db.Column(db.Boolean, default=True)
    
    # Внешний ключ на администратора, загрузившего документ
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    
    # Дата и время загрузки документа
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Дата последнего обновления
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """
        Строковое представление документа
        
        Возвращает:
            str: Название документа в формате <Document название>
        """
        return f'<Document {self.title}>'

class WebSource(db.Model):
    """
    Модель для хранения информации о веб-источниках
    
    Управляет веб-сайтами, которые используются как источники информации
    для базы знаний. Поддерживает автоматическое обновление контента.
    
    Атрибуты:
        id: Уникальный идентификатор веб-источника
        title: Название источника
        url: URL веб-страницы
        content_text: Извлеченный текстовый контент
        last_scraped: Дата последнего обновления контента
        is_active: Флаг активности источника
        scrape_frequency: Частота обновления контента
        added_by: ID администратора, добавившего источник
        created_at: Дата добавления
        updated_at: Дата последнего обновления
    """
    __tablename__ = 'web_sources'
    
    # Первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    
    # Название веб-источника (пользовательское, обязательное)
    title = db.Column(db.String(200), nullable=False)
    
    # URL веб-страницы (обязательное поле)
    url = db.Column(db.String(500), nullable=False)
    
    # Извлеченный текстовый контент страницы
    content_text = db.Column(db.Text)
    
    # Дата и время последнего обновления контента
    last_scraped = db.Column(db.DateTime)
    
    # Флаг активности источника (для управления обновлениями)
    is_active = db.Column(db.Boolean, default=True)
    
    # Частота обновления контента (daily, weekly, manual)
    scrape_frequency = db.Column(db.String(20), default='daily')
    
    # Внешний ключ на администратора, добавившего источник
    added_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    
    # Дата добавления источника
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Дата последнего обновления записи
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """
        Строковое представление веб-источника
        
        Возвращает:
            str: Название источника в формате <WebSource название>
        """
        return f'<WebSource {self.title}>'

class KnowledgeBase(db.Model):
    """
    Модель базы знаний для хранения фрагментов контента
    
    Централизованное хранилище фрагментов текста из различных источников
    (документы, веб-страницы, ручные записи). Используется для поиска
    релевантного контекста при генерации ответов бота.
    
    Атрибуты:
        id: Уникальный идентификатор записи
        source_type: Тип источника (document, web, manual)
        source_id: ID источника в соответствующей таблице
        content_chunk: Фрагмент текстового контента
        extra_data: Дополнительные метаданные в формате JSON
        is_active: Флаг активности записи
        created_at: Дата создания
        updated_at: Дата последнего обновления
    """
    __tablename__ = 'knowledge_base'
    
    # Первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    
    # Тип источника: 'document', 'web', 'manual'
    source_type = db.Column(db.String(20), nullable=False)
    
    # ID источника (ссылка на Document или WebSource)
    source_id = db.Column(db.Integer)
    
    # Фрагмент текстового контента (основная информация для поиска)
    content_chunk = db.Column(db.Text, nullable=False)
    
    # Дополнительные метаданные (номера страниц, разделы и т.д.)
    # Хранится в формате JSON для гибкости
    extra_data = db.Column(db.JSON)
    
    # Флаг активности записи (для мягкого удаления)
    is_active = db.Column(db.Boolean, default=True)
    
    # Дата создания записи
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Дата последнего обновления
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """
        Строковое представление записи базы знаний
        
        Возвращает:
            str: Тип и ID источника в формате <KnowledgeBase тип:ID>
        """
        return f'<KnowledgeBase {self.source_type}:{self.source_id}>'

class AdminUser(db.Model):
    """
    Модель пользователя-администратора системы
    
    Управляет доступом к административной панели. Администраторы могут
    управлять FAQ, загружать документы, добавлять веб-источники и
    просматривать аналитику системы.
    
    Атрибуты:
        id: Уникальный идентификатор администратора
        username: Имя пользователя (уникальное)
        email: Email адрес (уникальный)
        password_hash: Хеш пароля (безопасное хранение)
        is_active: Флаг активности учетной записи
        created_at: Дата создания учетной записи
        last_login: Дата последнего входа в систему
        documents: Загруженные документы (отношение один-ко-многим)
        web_sources: Добавленные веб-источники (отношение один-ко-многим)
    """
    __tablename__ = 'admin_users'
    
    # Первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    
    # Имя пользователя (уникальное, обязательное)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    # Email адрес (уникальный, обязательный)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Хеш пароля (безопасное хранение, обязательное)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Флаг активности учетной записи (для блокировки пользователей)
    is_active = db.Column(db.Boolean, default=True)
    
    # Дата создания учетной записи
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Дата последнего входа в систему (для аудита)
    last_login = db.Column(db.DateTime)
    
    # Отношения с другими таблицами
    # Документы, загруженные этим администратором
    documents = db.relationship('Document', backref='uploader', lazy=True)
    
    # Веб-источники, добавленные этим администратором
    web_sources = db.relationship('WebSource', backref='creator', lazy=True)
    
    def set_password(self, password):
        """
        Установка пароля с хешированием
        
        Использует безопасное хеширование для защиты пароля.
        Хеш сохраняется в поле password_hash.
        
        Аргументы:
            password (str): Пароль в открытом виде
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Проверка правильности пароля
        
        Сравнивает введенный пароль с сохраненным хешем.
        
        Аргументы:
            password (str): Пароль для проверки
            
        Возвращает:
            bool: True если пароль правильный, False в противном случае
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """
        Строковое представление администратора
        
        Возвращает:
            str: Имя пользователя в формате <AdminUser имя>
        """
        return f'<AdminUser {self.username}>'

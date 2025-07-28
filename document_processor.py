# Импорт необходимых модулей для обработки документов и веб-скрапинга
import os                                    # Для работы с файловой системой
import logging                              # Для логирования событий и ошибок
import mimetypes                           # Для определения типов файлов
from typing import Optional, List, Dict    # Для типизации функций
import trafilatura                         # Библиотека для извлечения текста из веб-страниц
import requests                            # Для выполнения HTTP запросов
from datetime import datetime              # Для работы с датами

# Настройка логгера для данного модуля
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Процессор для извлечения текстового контента из документов
    
    Класс обеспечивает извлечение текста из различных типов документов
    для последующего использования в базе знаний чат-бота.
    
    Поддерживаемые форматы:
    - Текстовые файлы (.txt)
    - HTML файлы (.html)
    - PDF файлы (.pdf) - базовая поддержка
    - Word документы (.doc, .docx) - планируется
    
    Основные возможности:
    - Извлечение и очистка текста из документов
    - Разбивка больших текстов на фрагменты (chunking)
    - Безопасное сохранение загруженных файлов
    - Обработка различных кодировок текста
    """
    
    # Словарь поддерживаемых типов файлов
    SUPPORTED_TYPES = {
        'text/plain': '.txt',           # Обычные текстовые файлы
        'application/pdf': '.pdf',      # PDF документы
        'application/msword': '.doc',   # Word документы (старый формат)
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',  # Word (новый формат)
        'text/html': '.html'            # HTML страницы
    }
    
    def __init__(self, upload_folder: str = 'uploads'):
        """
        Инициализация процессора документов
        
        Аргументы:
            upload_folder (str): Папка для сохранения загруженных файлов
        """
        self.upload_folder = upload_folder
        # Создание папки для загрузок, если она не существует
        os.makedirs(upload_folder, exist_ok=True)
    
    def process_text_file(self, file_path: str) -> str:
        """
        Извлечение текста из текстовых файлов
        
        Обрабатывает обычные текстовые файлы с поддержкой различных кодировок.
        Сначала пытается прочитать в UTF-8, при неудаче - в CP1251 (Windows).
        
        Аргументы:
            file_path (str): Путь к текстовому файлу
            
        Возвращает:
            str: Извлеченный текст или пустая строка при ошибке
        """
        try:
            # Попытка чтения в кодировке UTF-8 (предпочтительная)
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Резервная попытка с кодировкой CP1251 (русские Windows-файлы)
                with open(file_path, 'r', encoding='cp1251') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading text file {file_path}: {str(e)}")
                return ""
    
    def process_html_file(self, file_path: str) -> str:
        """
        Извлечение текста из HTML файлов
        
        Использует библиотеку trafilatura для извлечения основного контента
        из HTML файлов с удалением разметки и навигационных элементов.
        
        Аргументы:
            file_path (str): Путь к HTML файлу
            
        Возвращает:
            str: Очищенный текстовый контент или пустая строка при ошибке
        """
        try:
            # Чтение HTML файла
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Извлечение основного текстового контента с помощью trafilatura
            # Автоматически удаляет навигацию, рекламу и другие второстепенные элементы
            return trafilatura.extract(html_content) or ""
        except Exception as e:
            logger.error(f"Error processing HTML file {file_path}: {str(e)}")
            return ""
    
    def process_pdf_file(self, file_path: str) -> str:
        """
        Извлечение текста из PDF файлов (базовая реализация)
        
        ПРИМЕЧАНИЕ: Текущая реализация является заглушкой.
        Для полноценной работы с PDF требуется установка PyPDF2, pdfplumber
        или аналогичных библиотек.
        
        Аргументы:
            file_path (str): Путь к PDF файлу
            
        Возвращает:
            str: Placeholder сообщение о необходимости дополнительной обработки
        """
        try:
            # TODO: Реализовать полноценное извлечение текста из PDF
            # Для этого нужно добавить зависимость PyPDF2 или pdfplumber
            logger.warning("PDF processing not fully implemented")
            return f"[PDF файл: {os.path.basename(file_path)}] - содержимое требует дополнительной обработки"
        except Exception as e:
            logger.error(f"Error processing PDF file {file_path}: {str(e)}")
            return ""
    
    def process_document(self, file_path: str, file_type: str) -> str:
        """
        Основной метод обработки документов
        
        Определяет тип файла и вызывает соответствующий метод обработки.
        Служит единой точкой входа для обработки всех поддерживаемых форматов.
        
        Аргументы:
            file_path (str): Путь к файлу для обработки
            file_type (str): MIME тип файла
            
        Возвращает:
            str: Извлеченный текстовый контент или сообщение об ошибке
        """
        try:
            # Определение метода обработки в зависимости от типа файла
            if file_type == 'text/plain':
                return self.process_text_file(file_path)
            elif file_type == 'text/html':
                return self.process_html_file(file_path)
            elif file_type == 'application/pdf':
                return self.process_pdf_file(file_path)
            else:
                # Файл неподдерживаемого типа
                logger.warning(f"Unsupported file type: {file_type}")
                return f"[Неподдерживаемый тип файла: {file_type}]"
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return ""
    
    def save_uploaded_file(self, file, filename: str) -> tuple[str, int]:
        """
        Безопасное сохранение загруженного файла
        
        Сохраняет файл в указанную папку и возвращает путь и размер файла.
        Используется для загрузки файлов через веб-интерфейс.
        
        Аргументы:
            file: Объект файла от Flask (FileStorage)
            filename (str): Безопасное имя файла
            
        Возвращает:
            tuple[str, int]: Кортеж (путь к файлу, размер файла в байтах)
            
        Исключения:
            Exception: При ошибке сохранения файла
        """
        try:
            # Формирование полного пути к файлу
            file_path = os.path.join(self.upload_folder, filename)
            
            # Сохранение файла на диск
            file.save(file_path)
            
            # Получение размера сохраненного файла
            file_size = os.path.getsize(file_path)
            
            return file_path, file_size
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Разбивка текста на фрагменты для базы знаний
        
        Разделяет большие тексты на управляемые фрагменты с перекрытием
        для лучшего поиска и обработки в системе AI. Старается делать
        разрывы в естественных местах (конец предложений).
        
        Аргументы:
            text (str): Исходный текст для разбивки
            chunk_size (int): Максимальный размер фрагмента в символах
            overlap (int): Размер перекрытия между фрагментами в символах
            
        Возвращает:
            List[str]: Список текстовых фрагментов
        """
        # Проверка на пустой текст или текст, не требующий разбивки
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Определение конца текущего фрагмента
            end = start + chunk_size
            
            # Если достигли конца текста, добавляем оставшуюся часть
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Попытка найти хорошее место для разрыва (конец предложения или абзаца)
            chunk = text[start:end]
            last_period = chunk.rfind('.')      # Последняя точка
            last_newline = chunk.rfind('\n')    # Последний перенос строки
            break_point = max(last_period, last_newline)
            
            # Если найдено хорошее место для разрыва (не слишком близко к началу)
            if break_point > start + chunk_size // 2:
                chunks.append(text[start:start + break_point + 1])
                start = start + break_point + 1 - overlap
            else:
                # Если хорошего места не найдено, разрываем по размеру
                chunks.append(chunk)
                start = end - overlap
        
        # Возврат только непустых фрагментов
        return [chunk.strip() for chunk in chunks if chunk.strip()]

class WebScraper:
    """
    Скрапер для извлечения контента с веб-сайтов
    
    Класс обеспечивает загрузку и обработку веб-страниц для получения
    текстового контента, который затем используется в базе знаний.
    
    Основные возможности:
    - Загрузка веб-страниц с помощью trafilatura
    - Извлечение основного контента с удалением навигации и рекламы
    - Валидация доступности URL
    - Обработка ошибок сети и недоступных сайтов
    """
    
    def __init__(self):
        """
        Инициализация веб-скрапера
        
        Настраивает HTTP сессию с пользовательским User-Agent
        для корректной идентификации при запросах к веб-сайтам.
        """
        # Создание HTTP сессии для переиспользования соединений
        self.session = requests.Session()
        
        # Установка User-Agent для идентификации нашего бота
        # Помогает избежать блокировки некоторыми сайтами
        self.session.headers.update({
            'User-Agent': 'BolashakBot/1.0 (Educational Content Scraper)'
        })
    
    def scrape_url(self, url: str) -> Optional[str]:
        """
        Извлечение контента с веб-страницы
        
        Загружает веб-страницу и извлекает основной текстовый контент
        с помощью библиотеки trafilatura, которая автоматически
        фильтрует навигацию, рекламу и другие второстепенные элементы.
        
        Аргументы:
            url (str): URL веб-страницы для обработки
            
        Возвращает:
            Optional[str]: Извлеченный текст или None при ошибке
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Загрузка контента веб-страницы с помощью trafilatura
            # trafilatura.fetch_url автоматически обрабатывает кодировки и ошибки
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                logger.warning(f"Failed to download content from {url}")
                return None
            
            # Извлечение основного текстового контента
            # Автоматически удаляет HTML теги, навигацию, рекламу и боковые панели
            text = trafilatura.extract(downloaded)
            
            if not text:
                logger.warning(f"Failed to extract text from {url}")
                return None
            
            logger.info(f"Successfully scraped {len(text)} characters from {url}")
            return text
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return None
    
    def validate_url(self, url: str) -> bool:
        """
        Валидация доступности URL
        
        Проверяет, доступен ли указанный URL для скрапинга.
        Выполняет HEAD запрос для минимизации трафика.
        
        Аргументы:
            url (str): URL для проверки
            
        Возвращает:
            bool: True если URL доступен, False в противном случае
        """
        try:
            # Выполнение HEAD запроса (только заголовки, без контента)
            # allow_redirects=True разрешает следование перенаправлениям
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            # Проверка успешного статуса ответа (200 OK)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"URL validation failed for {url}: {str(e)}")
            return False

class KnowledgeBaseUpdater:
    """
    Класс для обновления базы знаний из различных источников
    
    Управляет процессом извлечения и обработки контента из документов
    и веб-источников для формирования базы знаний чат-бота.
    
    Основные возможности:
    - Обработка загруженных документов
    - Скрапинг веб-страниц
    - Разбивка контента на фрагменты
    - Обновление записей в базе знаний
    - Поиск релевантного контента по запросам
    """
    
    def __init__(self, db, models):
        """
        Инициализация обновлятора базы знаний
        
        Аргументы:
            db: Объект базы данных SQLAlchemy
            models: Словарь с моделями базы данных (Document, WebSource, KnowledgeBase)
        """
        self.db = db
        # Сохранение ссылок на модели для работы с базой данных
        self.Document = models['Document']
        self.WebSource = models['WebSource']
        self.KnowledgeBase = models['KnowledgeBase']
        
        # Инициализация компонентов для обработки контента
        self.document_processor = DocumentProcessor()
        self.web_scraper = WebScraper()
    
    def update_from_document(self, document_id: int) -> bool:
        """
        Обновление базы знаний из документа
        
        Обрабатывает загруженный документ, извлекает текст, разбивает на фрагменты
        и добавляет в базу знаний для использования чат-ботом.
        
        Аргументы:
            document_id (int): ID документа в базе данных
            
        Возвращает:
            bool: True при успешной обработке, False при ошибке
        """
        try:
            # Получение документа из базы данных
            document = self.Document.query.get(document_id)
            if not document:
                logger.error(f"Document {document_id} not found")
                return False
            
            # Обработка документа, если он еще не был обработан
            if not document.is_processed:
                # Извлечение текстового контента из файла
                text_content = self.document_processor.process_document(
                    document.file_path, 
                    mimetypes.guess_type(document.filename)[0] or 'text/plain'
                )
                
                # Сохранение извлеченного текста в базе данных
                document.content_text = text_content
                document.is_processed = True
                self.db.session.commit()
            
            # Очистка существующих записей в базе знаний для этого документа
            # Позволяет обновлять контент при повторной обработке
            self.KnowledgeBase.query.filter_by(
                source_type='document', 
                source_id=document_id
            ).delete()
            
            # Разбивка текста на фрагменты для лучшего поиска
            chunks = self.document_processor.chunk_text(document.content_text)
            
            # Создание записей в базе знаний для каждого фрагмента
            for i, chunk in enumerate(chunks):
                kb_entry = self.KnowledgeBase(
                    source_type='document',
                    source_id=document_id,
                    content_chunk=chunk,
                    # Сохранение метаданных о фрагменте
                    extra_data={'chunk_index': i, 'total_chunks': len(chunks)}
                )
                self.db.session.add(kb_entry)
            
            # Фиксация всех изменений в базе данных
            self.db.session.commit()
            logger.info(f"Updated knowledge base with {len(chunks)} chunks from document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating knowledge base from document {document_id}: {str(e)}")
            # Откат изменений при ошибке
            self.db.session.rollback()
            return False
    
    def update_from_web_source(self, web_source_id: int) -> bool:
        """
        Обновление базы знаний из веб-источника
        
        Скрапит указанный веб-сайт, извлекает контент, разбивает на фрагменты
        и обновляет соответствующие записи в базе знаний.
        
        Аргументы:
            web_source_id (int): ID веб-источника в базе данных
            
        Возвращает:
            bool: True при успешной обработке, False при ошибке
        """
        try:
            # Получение веб-источника из базы данных
            web_source = self.WebSource.query.get(web_source_id)
            if not web_source:
                logger.error(f"Web source {web_source_id} not found")
                return False
            
            # Скрапинг контента с веб-страницы
            text_content = self.web_scraper.scrape_url(web_source.url)
            if not text_content:
                logger.error(f"Failed to scrape content from {web_source.url}")
                return False
            
            # Обновление записи веб-источника
            web_source.content_text = text_content
            web_source.last_scraped = datetime.utcnow()
            
            # Очистка существующих записей в базе знаний для этого источника
            self.KnowledgeBase.query.filter_by(
                source_type='web', 
                source_id=web_source_id
            ).delete()
            
            # Разбивка контента на фрагменты
            chunks = self.document_processor.chunk_text(text_content)
            
            # Создание новых записей в базе знаний
            for i, chunk in enumerate(chunks):
                kb_entry = self.KnowledgeBase(
                    source_type='web',
                    source_id=web_source_id,
                    content_chunk=chunk,
                    # Сохранение метаданных включая URL источника
                    extra_data={
                        'chunk_index': i, 
                        'total_chunks': len(chunks), 
                        'url': web_source.url
                    }
                )
                self.db.session.add(kb_entry)
            
            # Фиксация изменений
            self.db.session.commit()
            logger.info(f"Updated knowledge base with {len(chunks)} chunks from web source {web_source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating knowledge base from web source {web_source_id}: {str(e)}")
            # Откат изменений при ошибке
            self.db.session.rollback()
            return False
    
    def get_relevant_content(self, query: str, language: str = 'ru', limit: int = 5) -> List[str]:
        """
        Получение релевантного контента из базы знаний
        
        Ищет фрагменты контента, релевантные пользовательскому запросу,
        используя простой поиск по ключевым словам.
        
        Аргументы:
            query (str): Поисковый запрос пользователя
            language (str): Язык запроса (пока не используется активно)
            limit (int): Максимальное количество результатов
            
        Возвращает:
            List[str]: Список релевантных фрагментов текста
        """
        try:
            # Подготовка запроса для поиска
            query_lower = query.lower()
            keywords = [word for word in query_lower.split() if len(word) > 2]
            
            if not keywords:
                return []
            
            # Простой поиск по ключевым словам
            # В продакшене рекомендуется использовать векторный поиск
            relevant_entries = []
            
            # Поиск по каждому ключевому слову
            for keyword in keywords[:3]:  # Ограничиваем первыми 3 ключевыми словами
                # Поиск записей, содержащих ключевое слово
                entries = self.KnowledgeBase.query.filter(
                    self.KnowledgeBase.is_active == True,
                    self.KnowledgeBase.content_chunk.ilike(f'%{keyword}%')
                ).limit(limit).all()
                
                # Добавление уникальных записей
                for entry in entries:
                    if entry not in relevant_entries:
                        relevant_entries.append(entry)
            
            # Возврат текстового контента найденных фрагментов
            return [entry.content_chunk for entry in relevant_entries[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting relevant content: {str(e)}")
            return []
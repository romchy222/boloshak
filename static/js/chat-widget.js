/**
 * Чат-виджет JavaScript для BolashakBot
 * 
 * Основной класс для управления интерфейсом чат-бота на веб-странице.
 * Обеспечивает взаимодействие пользователя с ботом, управление сообщениями,
 * переключение языков и отображение интерфейса.
 */

class ChatWidget {
    /**
     * Конструктор класса ChatWidget
     * 
     * Инициализирует виджет чата с настройками по умолчанию,
     * устанавливает обработчики событий и загружает приветственное сообщение.
     */
    constructor() {
        // Состояние открытия/закрытия виджета
        this.isOpen = false;
        
        // Текущий язык интерфейса (по умолчанию русский)
        this.currentLanguage = 'ru';
        
        // Уникальный идентификатор сессии пользователя
        this.sessionId = this.generateSessionId();
        
        // Массив для хранения истории сообщений
        this.messageHistory = [];
        
        // Инициализация обработчиков событий интерфейса
        this.initializeEventListeners();
        
        // Загрузка и отображение приветственного сообщения
        this.loadWelcomeMessage();
    }
    
    /**
     * Генерация уникального идентификатора сессии
     * 
     * Создает уникальный ID сессии для отслеживания диалога пользователя.
     * Используется для аналитики и группировки сообщений.
     * 
     * @returns {string} Уникальный идентификатор сессии
     */
    generateSessionId() {
        // Формат: session_[случайная строка]_[timestamp]
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    /**
     * Инициализация обработчиков событий интерфейса
     * 
     * Устанавливает слушатели событий для:
     * - Отправки сообщений по нажатию Enter
     * - Переключения языка интерфейса
     * - Автоматического изменения размера поля ввода
     */
    initializeEventListeners() {
        // Обработчик нажатия клавиш в поле ввода сообщения
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                // Отправка сообщения по нажатию Enter (без Shift)
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault(); // Предотвращение перехода на новую строку
                    this.sendMessage();
                }
            });
        }
        
        // Обработчик изменения языка интерфейса
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                // Обновление текущего языка и приветственного сообщения
                this.currentLanguage = e.target.value;
                this.updateWelcomeMessage();
            });
        }
        
        // Автоматическое изменение размера поля ввода при наборе текста
        if (chatInput) {
            chatInput.addEventListener('input', this.autoResizeInput);
        }
    }
    
    /**
     * Автоматическое изменение размера поля ввода
     * 
     * Подстраивает высоту текстового поля под содержимое,
     * обеспечивая удобство ввода многострочного текста.
     * 
     * @param {Event} e - событие изменения содержимого поля ввода
     */
    autoResizeInput(e) {
        const input = e.target;
        // Сброс высоты для корректного пересчета
        input.style.height = 'auto';
        // Установка высоты равной высоте содержимого
        input.style.height = (input.scrollHeight) + 'px';
    }
    
    /**
     * Загрузка приветственного сообщения
     * 
     * Определяет текст приветствия на разных языках.
     * В текущей реализации обработка уже выполняется в HTML шаблоне.
     */
    loadWelcomeMessage() {
        // Словарь приветственных сообщений для разных языков
        const welcomeMessages = {
            'ru': 'Здравствуйте! Я QabyldauBot, ваш помощник по вопросам поступления в университет Болашак. Задавайте любые вопросы!',
            'kz': 'Сәлеметсіз бе! Мен QabyldauBot боламын, Болашақ университетіне түсу мәселелері бойынша сіздің көмекшіңіз. Кез келген сұрақ қойыңыз!'
        };
        
        // Обработка уже выполняется в HTML шаблоне
    }
    
    /**
     * Обновление приветственного сообщения при смене языка
     * 
     * Очищает область сообщений и отображает новое приветствие
     * на выбранном языке интерфейса.
     */
    updateWelcomeMessage() {
        // Словарь приветственных сообщений для разных языков
        const welcomeMessages = {
            'ru': 'Здравствуйте! Я QabyldauBot, ваш помощник по вопросам поступления в университет Болашак. Задавайте любые вопросы!',
            'kz': 'Сәлеметсіз бе! Мен QabyldauBot боламын, Болашақ университетіне түсу мәселелері бойынша сіздің көмекшіңіз. Кез келген сұрақ қойыңыз!'
        };
        
        // Получение контейнера для сообщений
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            // Очистка области сообщений и вставка нового приветствия
            chatMessages.innerHTML = `
                <div class="message bot-message">
                    <div class="message-content">
                        <strong>QabyldauBot:</strong> ${welcomeMessages[this.currentLanguage]}
                    </div>
                    <div class="message-time">Сейчас</div>
                </div>
            `;
        }
    }
    
    /**
     * Переключение состояния виджета чата (открыт/закрыт)
     * 
     * Изменяет видимость виджета чата и кнопки вызова.
     * При открытии устанавливает фокус на поле ввода сообщения.
     */
    toggle() {
        // Получение элементов виджета и кнопки переключения
        const widget = document.getElementById('chatWidget');
        const toggleBtn = document.getElementById('chatToggle');
        
        if (widget && toggleBtn) {
            // Инверсия состояния открытия виджета
            this.isOpen = !this.isOpen;
            
            if (this.isOpen) {
                // Отображение виджета и скрытие кнопки
                widget.style.display = 'flex';
                toggleBtn.style.display = 'none';
                // Установка фокуса на поле ввода для удобства пользователя
                document.getElementById('chatInput')?.focus();
            } else {
                // Скрытие виджета и отображение кнопки
                widget.style.display = 'none';
                toggleBtn.style.display = 'block';
            }
        }
    }
    
    /**
     * Отправка сообщения пользователя и получение ответа от бота
     * 
     * Асинхронная функция, которая:
     * 1. Отправляет сообщение пользователя на сервер
     * 2. Отображает индикатор набора
     * 3. Получает и отображает ответ от бота
     * 4. Обрабатывает ошибки соединения
     */
    async sendMessage() {
        // Получение текста сообщения из поля ввода
        const chatInput = document.getElementById('chatInput');
        const message = chatInput?.value.trim();
        
        // Проверка на пустое сообщение
        if (!message) return;
        
        // Добавление сообщения пользователя в чат
        this.addMessage(message, 'user');
        
        // Очистка поля ввода и сброс его размера
        chatInput.value = '';
        chatInput.style.height = 'auto';
        chatInput.style.color = 'black';
        
        // Отображение индикатора набора ответа
        this.showTypingIndicator();
        
        try {
            // Отправка HTTP запроса к API чат-бота
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,                    // Текст сообщения
                    language: this.currentLanguage,      // Язык интерфейса
                    session_id: this.sessionId          // ID сессии
                })
            });
            
            // Проверка успешности HTTP запроса
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Парсинг JSON ответа от сервера
            const data = await response.json();
            
            // Скрытие индикатора набора
            this.hideTypingIndicator();
            
            // Обработка ответа или ошибки от сервера
            if (data.error) {
                // Отображение сообщения об ошибке
                this.addMessage(data.error, 'bot', true);
            } else {
                // Отображение ответа бота
                this.addMessage(data.response, 'bot');
                
                // Логирование времени ответа (если доступно)
                if (data.response_time) {
                    console.log(`Response time: ${data.response_time.toFixed(2)}s`);
                }
            }
            
        } catch (error) {
            // Обработка ошибок соединения или других проблем
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            
            // Формирование сообщения об ошибке на соответствующем языке
            const errorMessage = this.currentLanguage === 'ru' 
                ? 'Извините, произошла ошибка. Попробуйте еще раз.'
                : 'Кешіріңіз, қате орын алды. Қайталап көріңіз.';
            
            // Отображение сообщения об ошибке пользователю
            this.addMessage(errorMessage, 'bot', true);
        }
    }
    
    /**
     * Добавление сообщения в область чата
     * 
     * Создает HTML элемент сообщения и добавляет его в интерфейс чата.
     * Поддерживает сообщения от пользователя и бота, а также ошибки.
     * 
     * @param {string} content - Текст сообщения
     * @param {string} sender - Отправитель ('user' или 'bot')
     * @param {boolean} isError - Флаг ошибки для специального оформления
     */
    addMessage(content, sender, isError = false) {
        // Получение контейнера для сообщений
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        // Создание элемента сообщения
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        // Получение текущего времени для отметки сообщения
        const currentTime = new Date().toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });

        // Определение иконки в зависимости от отправителя
        const iconHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        // Формирование HTML содержимого сообщения
        messageDiv.innerHTML = `
            <div class="message-content ${isError ? 'text-danger' : ''}">
                ${sender === 'bot' ? iconHTML + '<strong>  QabyldauBot:</strong> ' : ''}
                ${this.formatMessage(content)}
                ${sender === 'user' ? '  ' + iconHTML: ''}
            </div>
            <div class="message-time">${currentTime}</div>
        `;
        
        // Добавление сообщения в интерфейс и прокрутка вниз
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Сохранение сообщения в истории для возможного экспорта
        this.messageHistory.push({
            content,
            sender,
            timestamp: new Date(),
            isError
        });
    }
    
    /**
     * Форматирование текста сообщения
     * 
     * Применяет базовое форматирование к тексту сообщения,
     * например, делает URL ссылками кликабельными.
     * 
     * @param {string} content - Исходный текст сообщения
     * @returns {string} Отформатированный HTML текст
     */
    formatMessage(content) {
        // Регулярное выражение для поиска URL в тексте
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        // Замена URL на кликабельные ссылки
        return content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    }
    
    /**
     * Отображение индикатора набора ответа
     * 
     * Показывает анимированный индикатор того, что бот печатает ответ.
     * Улучшает пользовательский опыт, показывая активность системы.
     */
    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            // Отображение индикатора
            indicator.style.display = 'block';
            
            // Автоматическая прокрутка к нижней части чата
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    }
    
    /**
     * Скрытие индикатора набора ответа
     * 
     * Убирает индикатор после получения ответа от бота.
     */
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            // Скрытие элемента индикатора
            indicator.style.display = 'none';
        }
    }
    
    /**
     * Очистка чата и сброс истории сообщений
     * 
     * Удаляет все сообщения из интерфейса чата и очищает историю.
     * Отображает новое приветственное сообщение.
     */
    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            // Восстановление приветственного сообщения
            this.updateWelcomeMessage();
            // Очистка истории сообщений
            this.messageHistory = [];
        }
    }
    
    /**
     * Экспорт истории чата в JSON файл
     * 
     * Создает JSON файл с полной историей диалога пользователя
     * и автоматически скачивает его через браузер.
     */
    exportHistory() {
        // Формирование объекта с данными для экспорта
        const data = {
            sessionId: this.sessionId,                    // ID сессии
            language: this.currentLanguage,               // Язык интерфейса
            messages: this.messageHistory,                // История сообщений
            exportedAt: new Date().toISOString()         // Дата экспорта
        };
        
        // Преобразование в JSON строку с форматированием
        const dataStr = JSON.stringify(data, null, 2);
        // Создание Blob объекта для скачивания
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        // Создание временной ссылки для скачивания
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `chat-history-${this.sessionId}.json`;
        // Автоматический клик для начала скачивания
        link.click();
    }
}

// === ИНИЦИАЛИЗАЦИЯ И ГЛОБАЛЬНЫЕ ФУНКЦИИ ===

/**
 * Глобальная переменная для хранения экземпляра виджета чата
 */
let chatWidget;

/**
 * Инициализация виджета чата после загрузки DOM
 * 
 * Создает экземпляр ChatWidget после того, как HTML документ
 * полностью загружен и готов к взаимодействию.
 */
document.addEventListener('DOMContentLoaded', function() {
    chatWidget = new ChatWidget();
});

// === ГЛОБАЛЬНЫЕ ФУНКЦИИ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ ===

/**
 * Глобальная функция переключения чата
 * 
 * Обеспечивает обратную совместимость для вызова из HTML.
 * Переключает состояние открытия/закрытия виджета чата.
 */
function toggleChat() {
    if (chatWidget) {
        chatWidget.toggle();
    }
}

/**
 * Глобальная функция отправки сообщения
 * 
 * Обеспечивает обратную совместимость для вызова из HTML.
 * Отправляет сообщение пользователя боту.
 */
function sendMessage() {
    if (chatWidget) {
        chatWidget.sendMessage();
    }
}

/**
 * Глобальная функция очистки чата
 * 
 * Обеспечивает обратную совместимость для вызова из HTML.
 * Очищает историю сообщений и восстанавливает приветствие.
 */
function clearChat() {
    if (chatWidget) {
        chatWidget.clearChat();
    }
}

/**
 * Обработчик нажатия клавиш для отправки сообщений
 * 
 * Обеспечивает отправку сообщения по нажатию Enter без Shift.
 * Используется как глобальный обработчик для интеграции в HTML.
 * 
 * @param {KeyboardEvent} event - Событие нажатия клавиши
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Предотвращение перехода на новую строку
        sendMessage();
    }
}

// === УТИЛИТАРНЫЕ ФУНКЦИИ ===

/**
 * Форматирование времени ответа для отображения
 * 
 * Конвертирует время в секундах в удобочитаемый формат:
 * - Меньше 1 секунды: отображается в миллисекундах
 * - 1 секунда и больше: отображается в секундах с 2 знаками после запятой
 * 
 * @param {number} seconds - Время в секундах
 * @returns {string} Отформатированная строка времени
 */
function formatResponseTime(seconds) {
    if (seconds < 1) {
        return `${Math.round(seconds * 1000)}ms`;
    } else {
        return `${seconds.toFixed(2)}s`;
    }
}

/**
 * Проверка состояния системы (health check)
 * 
 * Асинхронная функция для мониторинга доступности API чат-бота.
 * Отправляет запрос к эндпоинту /api/health и проверяет ответ.
 * 
 * @returns {Promise<boolean>} true если система работает, false при ошибке
 */
async function checkSystemHealth() {
    try {
        // Отправка запроса к health check эндпоинту
        const response = await fetch('/api/health');
        const data = await response.json();
        
        // Логирование результата проверки
        console.log('System health:', data);
        
        // Возврат статуса работоспособности
        return data.status === 'healthy';
    } catch (error) {
        // Логирование ошибки соединения
        console.error('Health check failed:', error);
        return false;
    }
}

// Автоматическая проверка состояния системы каждые 5 минут
setInterval(checkSystemHealth, 5 * 60 * 1000);

// === ЭКСПОРТ ДЛЯ МОДУЛЬНЫХ СИСТЕМ ===

/**
 * Экспорт класса ChatWidget для использования в модульных системах
 * (CommonJS, Node.js и т.д.)
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatWidget;
}

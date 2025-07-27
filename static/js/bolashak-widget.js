
/**
 * BolashakBot Chat Widget
 * Встраиваемый чат-виджет для сайта университета
 */

(function() {
    'use strict';

    // Конфигурация виджета
    const WIDGET_CONFIG = {
        apiEndpoint: window.BOLASHAK_API_URL || window.location.origin,
        position: 'bottom-right', // bottom-right, bottom-left
        theme: 'light', // dark, light
        language: 'ru', // ru, kz
        minimized: true,
        title: 'BolashakBot - Помощник студента',
        welcomeMessage: 'Здравствуйте! Я BolashakBot, ваш помощник по вопросам поступления. Как я могу помочь?'
    };

    // Полные стили виджета
    const widgetStyles = `
        /* CSS переменные */
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #4A6CF7 0%, #3B5BDB 100%);
            --primary-color: #4A6CF7;
            --secondary-color: #3B5BDB;
            --bg-light: #fff;
            --bg-dark: #212529;
            --card-bg: #f8f9fa;
            --border-radius: 12px;
            --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            --transition: 0.2s;
            --color-text-dark: #374151;
            --color-text-light: #fff;
            --color-border: #E5E7EB;
            --color-muted: #9CA3AF;
            --color-blue: #007bff;
            --color-gray: #6c757d;
            --stat-bg: rgba(255, 255, 255, 0.05);
            --feature-bg: rgba(255, 255, 255, 0.1);
            --blur: blur(10px);
        }

        /* Chat Widget */
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 450px;
            background: var(--bg-light);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            display: none;
            flex-direction: column;
            z-index: 1000;
            overflow: hidden;
            border: none;
            transition: box-shadow var(--transition);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .chat-widget.active {
            display: flex;
        }

        .chat-toggle-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: var(--secondary-gradient);
            color: var(--color-text-light);
            border: none;
            box-shadow: 0 4px 16px rgba(74, 108, 247, 0.4);
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-toggle-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(74, 108, 247, 0.5);
        }

        /* Быстрые ответы */
        .quick-replies-container {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }

        .scroll-btn {
            border: none;
            font-size: 14px;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s, transform 0.2s;
            background: rgba(0, 123, 255, 0.1);
            color: #007bff;
        }

        .scroll-btn:hover {
            background: rgba(0, 123, 255, 0.4);
            transform: scale(1.1);
        }

        #quickReplies {
            display: flex;
            overflow-x: auto;
            scrollbar-width: none;
            -webkit-overflow-scrolling: touch;
            width: calc(100% - 70px);
            padding: 4px 0;
        }

        #quickReplies::-webkit-scrollbar {
            display: none;
        }

        .quick-reply {
            flex: 0 0 auto;
            background-color: rgba(0, 123, 255, 0.1);
            color: #007bff;
            padding: 6px 10px;
            margin-right: 6px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 12px;
            white-space: nowrap;
            user-select: none;
            transition: background 0.2s, transform 0.2s;
            border: 1px solid rgba(0, 123, 255, 0.2);
        }

        .quick-reply:hover {
            background-color: rgba(0, 123, 255, 0.3);
            transform: scale(1.05);
        }

        /* Заголовок чата */
        .chat-header {
            background: var(--secondary-gradient);
            color: var(--color-text-light);
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
        }

        .chat-header-info {
            display: flex;
            flex-direction: column;
            font-weight: 600;
            font-size: 16px;
        }

        .chat-header-info i {
            font-size: 20px;
            margin-right: 8px;
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 0.9;
            }
            50% {
                opacity: 0.3;
            }
        }

        .chat-header-status {
            display: flex;
            align-items: center;
            font-size: 12px;
            opacity: 0.9;
            margin-top: 2px;
            animation: pulse 2s infinite ease-in-out;
        }

        .chat-header-status::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #4ADE80;
            border-radius: 50%;
            margin-right: 6px;
        }

        .chat-controls {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .chat-controls select,
        .chat-controls button {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 6px;
            font-size: 12px;
            transition: background var(--transition);
        }

        .chat-controls select {
            color: #ffffff;
            background: rgba(100, 124, 229, 0.8);
            padding: 4px 8px;
        }

        .chat-controls button {
            color: var(--color-text-light);
            padding: 3px 8px;
            cursor: pointer;
        }

        .chat-controls button:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        /* Сообщения чата */
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #FAFBFC;
        }

        .message {
            margin-bottom: 16px;
            animation: fadeInUp 0.3s ease;
        }

        .message-content {
            background: var(--bg-light);
            padding: 12px 16px;
            border-radius: 18px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            word-wrap: break-word;
            line-height: 1.5;
            font-size: 14px;
            position: relative;
            color: var(--color-text-dark);
            border: 1px solid var(--color-border);
            max-width: 85%;
        }

        .bot-message {
            display: flex;
            justify-content: flex-start;
            flex-direction: column;
        }

        .bot-message .message-content {
            background: var(--bg-light);
            color: var(--color-text-dark);
            border-bottom-left-radius: 6px;
        }

        .user-message {
            display: flex;
            justify-content: flex-end;
        }

        .user-message .message-content {
            background: var(--primary-color);
            color: var(--color-text-light);
            border-bottom-right-radius: 6px;
            border: none;
        }

        .message-time {
            font-size: 10px;
            opacity: 0.7;
            margin-top: 4px;
        }

        .bot-message .message-time {
            color: var(--color-muted);
            text-align: left;
        }

        .user-message .message-time {
            color: rgba(255, 255, 255, 0.7);
            text-align: right;
        }

        /* Ввод сообщения */
        .chat-input-container {
            padding: 16px 20px;
            background: var(--bg-light);
            border-top: 1px solid var(--color-border);
        }

        .chat-input-container .input-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .chat-input-container input {
            background: var(--bg-light);
            flex: 1;
            border: 2px solid #dfdfdf;
            border-radius: 24px;
            padding: 12px 16px;
            font-size: 14px;
            outline: none;
            transition: border-color var(--transition);
            color: #212529;
        }

        .chat-input-container input:focus {
            border-color: #898989;
        }

        .chat-input-container input::placeholder {
            color: #6c757d;
            opacity: 1;
        }

        .chat-input-container button {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--primary-color);
            color: var(--color-text-light);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background var(--transition);
        }

        .chat-input-container button:hover {
            background: var(--secondary-color);
        }

        .chat-input-container button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        /* Индикатор набора */
        .typing-indicator {
            padding: 0 20px 16px;
            background: #FAFBFC;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
            background: var(--bg-light);
            border-radius: 18px;
            border-bottom-left-radius: 6px;
            max-width: 85%;
            align-items: center;
        }

        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--color-muted);
            animation: typing 1.4s infinite ease-in-out;
        }

        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes typing {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Адаптивность */
        @media (max-width: 768px) {
            .chat-widget {
                width: calc(100vw - 40px);
                height: calc(100vh - 40px);
                bottom: 20px;
                right: 20px;
                left: 20px;
            }
        }

        /* Темная тема */
        [data-bs-theme="dark"] .chat-widget {
            background: var(--bg-dark);
            border-color: #495057;
        }

        [data-bs-theme="dark"] .chat-messages {
            background: #343a40;
        }

        [data-bs-theme="dark"] .message-content {
            background: #495057;
            color: var(--color-text-light);
        }

        [data-bs-theme="dark"] .bot-message .message-content {
            background: #0d47a1;
        }

        [data-bs-theme="dark"] .chat-input-container {
            background: var(--bg-dark);
            border-color: #495057;
        }

        [data-bs-theme="dark"] .chat-controls select {
            color: #fff;
            background: #343a40;
        }

        [data-bs-theme="dark"] .chat-input-container input {
            color: #fff;
            background: #343a40;
            border-color: #495057;
        }

        [data-bs-theme="dark"] .chat-input-container input::placeholder {
            color: #b0b0b0;
        }

        /* Стили совместимости для внешнего виджета */
        .bolashak-widget {
            position: fixed;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            transition: all 0.3s ease;
        }

        .bolashak-widget.bottom-right {
            bottom: 20px;
            right: 20px;
        }

        .bolashak-widget.bottom-left {
            bottom: 20px;
            left: 20px;
        }

        .bolashak-widget-button {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #ffffff;
            border: 2px solid #e2e8f0;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            position: relative;
        }

        .bolashak-widget-button:hover {
            border-color: #a0aec0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .bolashak-widget-button svg {
            width: 24px;
            height: 24px;
            fill: #4a5568;
        }

        .bolashak-widget-notification {
            position: absolute;
            top: -5px;
            right: -5px;
            width: 20px;
            height: 20px;
            background: #ff4757;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            color: white;
            animation: pulse 2s infinite;
        }

        .bolashak-widget-chat {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            display: none;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid #e1e8ed;
        }

        .bolashak-widget.bottom-left .bolashak-widget-chat {
            right: auto;
            left: 0;
        }

        .bolashak-widget-chat.open {
            display: flex;
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .bolashak-widget-header {
            background: #ffffff;
            color: #2d3748;
            padding: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #e2e8f0;
        }

        .bolashak-widget-header-info {
            display: flex;
            align-items: center;
        }

        .bolashak-widget-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
        }

        .bolashak-widget-avatar svg {
            width: 20px;
            height: 20px;
            fill: #4a5568;
        }

        .bolashak-widget-title {
            font-size: 16px;
            font-weight: 600;
            margin: 0;
        }

        .bolashak-widget-status {
            font-size: 12px;
            opacity: 0.9;
            margin: 0;
        }

        .bolashak-widget-close {
            background: none;
            border: none;
            color: #718096;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: background-color 0.2s;
        }

        .bolashak-widget-close:hover {
            background: #f7fafc;
            color: #4a5568;
        }

        .bolashak-widget-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f8fafc;
        }

        .bolashak-widget-message {
            margin-bottom: 16px;
            display: flex;
            align-items: flex-end;
        }

        .bolashak-widget-message.user {
            justify-content: flex-end;
        }

        .bolashak-widget-message.bot {
            justify-content: flex-start;
        }

        .bolashak-widget-message-content {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.4;
        }

        .bolashak-widget-message.user .bolashak-widget-message-content {
            background: #4a5568;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .bolashak-widget-message.bot .bolashak-widget-message-content {
            background: white;
            color: #1a202c;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 4px;
        }

        .bolashak-widget-typing {
            display: none;
            align-items: flex-end;
            margin-bottom: 16px;
            justify-content: flex-start;
        }

        .bolashak-widget-typing-dots {
            display: flex;
            align-items: center;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            padding: 12px 16px;
            max-width: 80%;
        }

        .bolashak-widget-typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #cbd5e0;
            margin: 0 2px;
            animation: typing 1.4s infinite;
        }

        .bolashak-widget-typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .bolashak-widget-typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        .bolashak-widget-input {
            padding: 16px;
            border-top: 1px solid #e2e8f0;
            background: white;
        }

        .bolashak-widget-input-form {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .bolashak-widget-input-field {
            flex: 1;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 10px 16px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .bolashak-widget-input-field:focus {
            border-color: #4a5568;
        }

        .bolashak-widget-send {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #4a5568;
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s;
        }

        .bolashak-widget-send:hover:not(:disabled) {
            background: #2d3748;
        }

        .bolashak-widget-send:disabled {
            background: #cbd5e0;
            cursor: not-allowed;
        }

        .bolashak-widget-powered {
            text-align: center;
            padding: 8px;
            font-size: 11px;
            color: #718096;
            background: #f7fafc;
            border-top: 1px solid #e2e8f0;
        }

        .bolashak-widget-powered a {
            color: #4a5568;
            text-decoration: none;
        }

        .bolashak-widget-powered a:hover {
            color: #2d3748;
        }

        @media (max-width: 480px) {
            .bolashak-widget-chat {
                width: calc(100vw - 40px);
                height: calc(100vh - 100px);
                bottom: 80px;
                right: 20px;
                left: 20px;
            }

            .bolashak-widget.bottom-left .bolashak-widget-chat {
                left: 20px;
            }
        }
    `;

    // Класс виджета чат-бота Болашак
    class BolashakWidget {
        constructor(config = {}) {
            this.config = { ...WIDGET_CONFIG, ...config };
            this.isOpen = false;
            this.messages = [];
            this.quickReplies = [
                "Как поступить?",
                "Стоимость обучения",
                "Документы для поступления",
                "Специальности",
                "Контакты",
                "Сроки подачи документов"
            ];
            this.init();
        }

        init() {
            this.injectStyles();
            this.createWidget();
            this.bindEvents();
            this.showWelcomeMessage();
            this.createQuickReplies();
        }

        injectStyles() {
            const style = document.createElement('style');
            style.textContent = widgetStyles;
            document.head.appendChild(style);
        }

        createWidget() {
            const widget = document.createElement('div');
            widget.className = 'chat-widget';
            widget.innerHTML = `
                <div class="chat-header">
                    <div class="chat-header-info">
                        <div><i class="fas fa-robot"></i>BolashakBot</div>
                        <div class="chat-header-status">В сети • Отвечает быстро</div>
                    </div>
                    <div class="chat-controls">
                        <select id="languageSelect">
                            <option value="ru">Русский</option>
                            <option value="kz">Қазақша</option>
                        </select>
                        <button onclick="this.closest('.chat-widget').remove()">✕</button>
                    </div>
                </div>
                <div class="chat-messages" id="chatMessages">
                    <!-- Сообщения будут добавляться здесь -->
                </div>
                <div class="typing-indicator" id="typingIndicator" style="display: none;">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                <div class="quick-replies-container">
                    <button class="scroll-btn" onclick="scrollQuickReplies('left')">‹</button>
                    <div id="quickReplies"></div>
                    <button class="scroll-btn" onclick="scrollQuickReplies('right')">›</button>
                </div>
                <div class="chat-input-container">
                    <div class="input-group">
                        <input type="text" id="chatInput" placeholder="Введите ваш вопрос..." maxlength="500">
                        <button id="sendButton">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            `;

            // Создаем кнопку переключения
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'chat-toggle-btn';
            toggleBtn.innerHTML = '<i class="fas fa-comments"></i>';
            
            document.body.appendChild(widget);
            document.body.appendChild(toggleBtn);
            
            this.widget = widget;
            this.toggleBtn = toggleBtn;
            this.messagesContainer = widget.querySelector('#chatMessages');
            this.typingIndicator = widget.querySelector('#typingIndicator');
            this.inputField = widget.querySelector('#chatInput');
            this.sendButton = widget.querySelector('#sendButton');
            this.quickRepliesContainer = widget.querySelector('#quickReplies');
        }

        createQuickReplies() {
            this.quickRepliesContainer.innerHTML = '';
            this.quickReplies.forEach(reply => {
                const replyBtn = document.createElement('div');
                replyBtn.className = 'quick-reply';
                replyBtn.textContent = reply;
                replyBtn.onclick = () => this.sendQuickReply(reply);
                this.quickRepliesContainer.appendChild(replyBtn);
            });
        }

        bindEvents() {
            this.toggleBtn.addEventListener('click', () => this.toggleChat());
            
            this.sendButton.addEventListener('click', () => this.sendMessage());
            
            this.inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Глобальные функции для быстрых ответов
            window.scrollQuickReplies = (direction) => {
                const container = this.quickRepliesContainer;
                const scrollAmount = 100;
                if (direction === 'left') {
                    container.scrollLeft -= scrollAmount;
                } else {
                    container.scrollLeft += scrollAmount;
                }
            };
        }

        toggleChat() {
            this.isOpen = !this.isOpen;
            if (this.isOpen) {
                this.widget.classList.add('active');
                this.toggleBtn.style.display = 'none';
                this.inputField.focus();
            } else {
                this.widget.classList.remove('active');
                this.toggleBtn.style.display = 'flex';
            }
        }

        sendQuickReply(text) {
            this.inputField.value = text;
            this.sendMessage();
        }

        showWelcomeMessage() {
            setTimeout(() => {
                this.addMessage('bot', WIDGET_CONFIG.welcomeMessage);
            }, 1000);
        }

        addMessage(sender, text, isHtml = false) {
            const message = document.createElement('div');
            message.className = `message ${sender}-message`;

            const currentTime = new Date().toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit'
            });

            message.innerHTML = `
                <div class="message-content">
                    ${isHtml ? text : this.escapeHtml(text)}
                </div>
                <div class="message-time">${currentTime}</div>
            `;

            this.messagesContainer.appendChild(message);
            this.messages.push({ sender, text, timestamp: new Date() });
            this.scrollToBottom();
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        scrollToBottom() {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }

        showTyping() {
            this.typingIndicator.style.display = 'block';
            this.scrollToBottom();
        }

        hideTyping() {
            this.typingIndicator.style.display = 'none';
        }

        async sendMessage() {
            const text = this.inputField.value.trim();
            if (!text) return;

            this.addMessage('user', text);
            this.inputField.value = '';
            this.sendButton.disabled = true;

            try {
                this.showTyping();

                const response = await fetch(`${WIDGET_CONFIG.apiEndpoint}/api/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: text,
                        language: WIDGET_CONFIG.language
                    })
                });

                if (!response.ok) {
                    throw new Error('Ошибка сети');
                }

                const data = await response.json();
                this.hideTyping();
                this.addMessage('bot', data.response || 'Извините, произошла ошибка. Попробуйте позже.');

            } catch (error) {
                console.error('Error sending message:', error);
                this.hideTyping();
                this.addMessage('bot', 'Извините, произошла ошибка соединения.');
            } finally {
                this.sendButton.disabled = false;
                this.inputField.focus();
            }
        }
    }

    // Инициализация виджета при загрузке страницы
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new BolashakWidget();
        });
    } else {
        new BolashakWidget();
    }

    // Экспорт для возможности настройки
    window.BolashakWidget = BolashakWidget;
    window.BOLASHAK_WIDGET_CONFIG = WIDGET_CONFIG;

})();

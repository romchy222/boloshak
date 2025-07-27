/**
 * BolashakBot Chat Widget
 * Встраиваемый чат-виджет для сайта университета
 */

(function() {
    'use strict';

    // Конфигурация виджета
    const WIDGET_CONFIG = {
        apiEndpoint: window.BOLASHAK_API_URL || 'https://your-replit-app.replit.app',
        position: 'bottom-right', // bottom-right, bottom-left
        theme: 'dark', // dark, light
        language: 'ru', // ru, kz
        minimized: true,
        title: 'BolashakBot - Помощник студента',
        welcomeMessage: 'Здравствуйте! Я BolashakBot, ваш помощник по вопросам поступления. Как я могу помочь?'
    };

    // Стили виджета
    const widgetStyles = `
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .bolashak-widget-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .bolashak-widget-button svg {
            width: 24px;
            height: 24px;
            fill: white;
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
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .bolashak-widget-header-info {
            display: flex;
            align-items: center;
        }
        
        .bolashak-widget-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
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
            color: white;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        
        .bolashak-widget-close:hover {
            background: rgba(255, 255, 255, 0.1);
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
            background: #667eea;
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
            align-items: center;
            margin-bottom: 16px;
        }
        
        .bolashak-widget-typing-dots {
            display: flex;
            align-items: center;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 12px 16px;
            margin-left: 8px;
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
        
        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
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
            border-color: #667eea;
        }
        
        .bolashak-widget-send {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #667eea;
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s;
        }
        
        .bolashak-widget-send:hover:not(:disabled) {
            background: #5a67d8;
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
            color: #667eea;
            text-decoration: none;
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

    class BolashakWidget {
        constructor() {
            this.isOpen = false;
            this.messages = [];
            this.isTyping = false;
            
            this.init();
        }

        init() {
            this.injectStyles();
            this.createWidget();
            this.bindEvents();
            this.showWelcomeMessage();
        }

        injectStyles() {
            const style = document.createElement('style');
            style.textContent = widgetStyles;
            document.head.appendChild(style);
        }

        createWidget() {
            const widget = document.createElement('div');
            widget.className = `bolashak-widget ${WIDGET_CONFIG.position}`;
            widget.innerHTML = `
                <div class="bolashak-widget-chat">
                    <div class="bolashak-widget-header">
                        <div class="bolashak-widget-header-info">
                            <div class="bolashak-widget-avatar">
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9M19 21H5V3H15V9H19Z"/>
                                </svg>
                            </div>
                            <div>
                                <div class="bolashak-widget-title">BolashakBot</div>
                                <div class="bolashak-widget-status">В сети • Отвечает быстро</div>
                            </div>
                        </div>
                        <button class="bolashak-widget-close">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="bolashak-widget-messages"></div>
                    <div class="bolashak-widget-typing">
                        <div class="bolashak-widget-avatar">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9M19 21H5V3H15V9H19Z"/>
                            </svg>
                        </div>
                        <div class="bolashak-widget-typing-dots">
                            <div class="bolashak-widget-typing-dot"></div>
                            <div class="bolashak-widget-typing-dot"></div>
                            <div class="bolashak-widget-typing-dot"></div>
                        </div>
                    </div>
                    <div class="bolashak-widget-input">
                        <form class="bolashak-widget-input-form">
                            <input type="text" class="bolashak-widget-input-field" placeholder="Введите ваш вопрос..." maxlength="500">
                            <button type="submit" class="bolashak-widget-send">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                                </svg>
                            </button>
                        </form>
                    </div>
                    <div class="bolashak-widget-powered">
                        Работает на <a href="#" target="_blank">BolashakBot AI</a>
                    </div>
                </div>
                <button class="bolashak-widget-button">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z"/>
                    </svg>
                    <div class="bolashak-widget-notification">1</div>
                </button>
            `;

            document.body.appendChild(widget);
            this.widget = widget;
            this.chatContainer = widget.querySelector('.bolashak-widget-chat');
            this.messagesContainer = widget.querySelector('.bolashak-widget-messages');
            this.typingIndicator = widget.querySelector('.bolashak-widget-typing');
            this.inputField = widget.querySelector('.bolashak-widget-input-field');
            this.sendButton = widget.querySelector('.bolashak-widget-send');
            this.notification = widget.querySelector('.bolashak-widget-notification');
        }

        bindEvents() {
            // Открытие/закрытие чата
            this.widget.querySelector('.bolashak-widget-button').addEventListener('click', () => {
                this.toggleChat();
            });

            this.widget.querySelector('.bolashak-widget-close').addEventListener('click', () => {
                this.closeChat();
            });

            // Отправка сообщений
            this.widget.querySelector('.bolashak-widget-input-form').addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });

            // Enter для отправки
            this.inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Закрытие при клике вне виджета
            document.addEventListener('click', (e) => {
                if (!this.widget.contains(e.target) && this.isOpen) {
                    this.closeChat();
                }
            });
        }

        toggleChat() {
            if (this.isOpen) {
                this.closeChat();
            } else {
                this.openChat();
            }
        }

        openChat() {
            this.isOpen = true;
            this.chatContainer.classList.add('open');
            this.inputField.focus();
            this.hideNotification();
        }

        closeChat() {
            this.isOpen = false;
            this.chatContainer.classList.remove('open');
        }

        showNotification() {
            this.notification.style.display = 'flex';
        }

        hideNotification() {
            this.notification.style.display = 'none';
        }

        showWelcomeMessage() {
            setTimeout(() => {
                this.addMessage('bot', WIDGET_CONFIG.welcomeMessage);
                if (!this.isOpen) {
                    this.showNotification();
                }
            }, 1000);
        }

        addMessage(sender, text, isHtml = false) {
            const message = document.createElement('div');
            message.className = `bolashak-widget-message ${sender}`;
            
            const content = document.createElement('div');
            content.className = 'bolashak-widget-message-content';
            
            if (isHtml) {
                content.innerHTML = text;
            } else {
                content.textContent = text;
            }
            
            message.appendChild(content);
            this.messagesContainer.appendChild(message);
            
            this.messages.push({ sender, text, timestamp: new Date() });
            this.scrollToBottom();
        }

        scrollToBottom() {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }

        showTyping() {
            this.isTyping = true;
            this.typingIndicator.style.display = 'flex';
            this.scrollToBottom();
        }

        hideTyping() {
            this.isTyping = false;
            this.typingIndicator.style.display = 'none';
        }

        async sendMessage() {
            const text = this.inputField.value.trim();
            if (!text) return;

            // Добавляем сообщение пользователя
            this.addMessage('user', text);
            this.inputField.value = '';
            this.sendButton.disabled = true;

            try {
                // Показываем индикатор печати
                this.showTyping();

                // Отправляем запрос к API
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
                
                // Скрываем индикатор печати
                this.hideTyping();
                
                // Добавляем ответ бота
                this.addMessage('bot', data.response || 'Извините, произошла ошибка. Попробуйте позже.');

            } catch (error) {
                console.error('Error sending message:', error);
                this.hideTyping();
                this.addMessage('bot', 'Извините, произошла ошибка соединения. Проверьте интернет и попробуйте снова.');
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
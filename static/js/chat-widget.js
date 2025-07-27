// Chat Widget JavaScript for BolashakBot

class ChatWidget {
    constructor() {
        this.isOpen = false;
        this.currentLanguage = 'ru';
        this.sessionId = this.generateSessionId();
        this.messageHistory = [];
        
        this.initializeEventListeners();
        this.loadWelcomeMessage();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    initializeEventListeners() {
        // Chat input enter key
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // Language selector
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.currentLanguage = e.target.value;
                this.updateWelcomeMessage();
            });
        }
        
        // Auto-resize chat input
        if (chatInput) {
            chatInput.addEventListener('input', this.autoResizeInput);
        }
    }
    
    autoResizeInput(e) {
        const input = e.target;
        input.style.height = 'auto';
        input.style.height = (input.scrollHeight) + 'px';
    }
    
    loadWelcomeMessage() {
        const welcomeMessages = {
            'ru': 'Здравствуйте! Я QabyldauBot, ваш помощник по вопросам поступления в университет Болашак. Задавайте любые вопросы!',
            'kz': 'Сәлеметсіз бе! Мен QabyldauBot боламын, Болашақ университетіне түсу мәселелері бойынша сіздің көмекшіңіз. Кез келген сұрақ қойыңыз!'
        };
        
        // This is already handled in the HTML template
    }
    
    updateWelcomeMessage() {
        const welcomeMessages = {
            'ru': 'Здравствуйте! Я QabyldauBot, ваш помощник по вопросам поступления в университет Болашак. Задавайте любые вопросы!',
            'kz': 'Сәлеметсіз бе! Мен QabyldauBot боламын, Болашақ университетіне түсу мәселелері бойынша сіздің көмекшіңіз. Кез келген сұрақ қойыңыз!'
        };
        
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
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
    
    toggle() {
        const widget = document.getElementById('chatWidget');
        const toggleBtn = document.getElementById('chatToggle');
        
        if (widget && toggleBtn) {
            this.isOpen = !this.isOpen;
            
            if (this.isOpen) {
                widget.style.display = 'flex';
                toggleBtn.style.display = 'none';
                document.getElementById('chatInput')?.focus();
            } else {
                widget.style.display = 'none';
                toggleBtn.style.display = 'block';
            }
        }
    }
    
    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput?.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        chatInput.value = '';
        chatInput.style.height = 'auto';
        chatInput.style.color = 'black';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    language: this.currentLanguage,
                    session_id: this.sessionId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (data.error) {
                this.addMessage(data.error, 'bot', true);
            } else {
                this.addMessage(data.response, 'bot');
                
                // Log response time if available
                if (data.response_time) {
                    console.log(`Response time: ${data.response_time.toFixed(2)}s`);
                }
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            
            const errorMessage = this.currentLanguage === 'ru' 
                ? 'Извините, произошла ошибка. Попробуйте еще раз.'
                : 'Кешіріңіз, қате орын алды. Қайталап көріңіз.';
            
            this.addMessage(errorMessage, 'bot', true);
        }
    }
    
    addMessage(content, sender, isError = false) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const currentTime = new Date().toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const iconHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        
        messageDiv.innerHTML = `
            <div class="message-content ${isError ? 'text-danger' : ''}">
                ${sender === 'bot' ? iconHTML + '<strong>  QabyldauBot:</strong> ' : ''}
                ${this.formatMessage(content)}
                ${sender === 'user' ? '  ' + iconHTML: ''}
            </div>
            <div class="message-time">${currentTime}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        this.messageHistory.push({
            content,
            sender,
            timestamp: new Date(),
            isError
        });
    }
    
    formatMessage(content) {
        // Basic formatting: make URLs clickable
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    }
    
    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'block';
            
            // Scroll to bottom
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            this.updateWelcomeMessage();
            this.messageHistory = [];
        }
    }
    
    exportHistory() {
        const data = {
            sessionId: this.sessionId,
            language: this.currentLanguage,
            messages: this.messageHistory,
            exportedAt: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `chat-history-${this.sessionId}.json`;
        link.click();
    }
}

// Initialize chat widget
let chatWidget;

document.addEventListener('DOMContentLoaded', function() {
    chatWidget = new ChatWidget();
});

// Global functions for backward compatibility
function toggleChat() {
    if (chatWidget) {
        chatWidget.toggle();
    }
}

function sendMessage() {
    if (chatWidget) {
        chatWidget.sendMessage();
    }
}

function clearChat() {
    if (chatWidget) {
        chatWidget.clearChat();
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Utility functions
function formatResponseTime(seconds) {
    if (seconds < 1) {
        return `${Math.round(seconds * 1000)}ms`;
    } else {
        return `${seconds.toFixed(2)}s`;
    }
}

// Health check function
async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('System health:', data);
        return data.status === 'healthy';
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

// Auto health check every 5 minutes
setInterval(checkSystemHealth, 5 * 60 * 1000);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatWidget;
}

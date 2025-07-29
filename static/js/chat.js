// Агент: id, label, welcome
const AGENTS = {
    qabyldau: {
        label: '<i class="bi bi-person-badge"></i> QabyldauBot',
        welcome: 'Здравствуйте! Я QabyldauBot — помогу с вопросами поступления.'
    },
    consultant: {
        label: '<i class="bi bi-mortarboard"></i> Виртуальный консультант',
        welcome: 'Привет! Я виртуальный консультант для студентов. Задайте вопрос по учебе или жизни в университете.'
    },
    navigator: {
        label: '<i class="bi bi-compass"></i> Студенческий навигатор',
        welcome: 'Я — студенческий навигатор. Помогу с навигацией по университету и цифровым сервисам.'
    },
    green: {
        label: '<i class="bi bi-briefcase"></i> GreenNavigator',
        welcome: 'Добро пожаловать! GreenNavigator поможет выпускникам с поиском работы и карьерой.'
    },
    dorm: {
        label: '<i class="bi bi-house-door"></i> Агент по общежитию',
        welcome: 'Здравствуйте! Я — агент по вопросам общежития. Помогу с любыми бытовыми вопросами.'
    }
};

let currentAgent = 'qabyldau';

// Смена агента и welcome
document.querySelectorAll('.cgpt-agent-item').forEach(el => {
    el.addEventListener('click', () => {
        if (el.classList.contains('active')) return;
        document.querySelectorAll('.cgpt-agent-item').forEach(i => i.classList.remove('active'));
        el.classList.add('active');
        currentAgent = el.getAttribute('data-agent');
        // Переключить label и welcome
        document.getElementById('current-agent-label').innerHTML = AGENTS[currentAgent].label;
        document.getElementById('welcome-title').textContent = AGENTS[currentAgent].welcome;
        // Очистить старые сообщения
        document.getElementById('cgpt-messages').innerHTML = '';
        // Показать welcome
        addBotMessage(AGENTS[currentAgent].welcome);
    });
});

// Сообщения чата
const messagesBox = document.getElementById('cgpt-messages');
function addMessage(text, sender='user') {
    const msg = document.createElement('div');
    msg.className = 'cgpt-message ' + sender;
    msg.innerHTML = `
        <div class="cgpt-avatar">
            <img src="${sender === 'user'
                ? 'https://cdn.jsdelivr.net/gh/microsoft/fluentui-emoji/assets/People/User/3D/user_3d_default.svg'
                : 'https://chat.openai.com/favicon-32x32.png'}" alt="${sender}">
        </div>
        <div class="cgpt-bubble"><div class="cgpt-text">${text}</div></div>
    `;
    messagesBox.appendChild(msg);
    setTimeout(() => msg.scrollIntoView({behavior: 'smooth', block: 'end'}), 80);
}
function addBotMessage(text) { addMessage(text, 'bot'); }

// Welcome при загрузке
window.addEventListener('DOMContentLoaded', () => {
    addBotMessage(AGENTS[currentAgent].welcome);
});

// Автоувеличение textarea
const input = document.getElementById('cgpt-chat-input');
input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 180) + "px";
});

// Отправка сообщений
document.getElementById('cgpt-chat-form').onsubmit = async function(e) {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    addMessage(text, 'user');
    input.value = '';
    input.style.height = 'auto';
    addBotMessage('<span class="cgpt-typing">Бот печатает…</span>');
    try {
        const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, language: 'ru', agent: currentAgent })
        });
        const data = await resp.json();
        messagesBox.lastChild.remove();
        addBotMessage(data.response || 'Ошибка ответа');
    } catch {
        messagesBox.lastChild.remove();
        addBotMessage('Ошибка соединения с сервером');
    }
};
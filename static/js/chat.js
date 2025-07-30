document.addEventListener('DOMContentLoaded', async () => {
  const input = document.querySelector('.bbx-input');
  const sendBtn = document.querySelector('.bbx-send');
  const messagesContainer = document.querySelector('.bbx-messages');
  const agentSelect = document.querySelector('.bbx-agent-select');

  // Загрузка списка агентов
  async function loadAgents() {
    try {
      const resp = await fetch('/api/agents');
      const data = await resp.json();
      if (data.agents && agentSelect) {
        data.agents.forEach(agent => {
          const opt = document.createElement('option');
          opt.value = agent.type;
          opt.textContent = agent.name + " — " + agent.description;
          agentSelect.appendChild(opt);
        });
      }
    } catch (e) {
      // fallback: только авто-выбор
    }
  }
  await loadAgents();

  function addMessage(text, sender = 'user') {
    const msg = document.createElement('div');
    msg.className = `bbx-message bbx-message-${sender}`;
    msg.textContent = text;
    messagesContainer.appendChild(msg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;
    addMessage(message, 'user');
    input.value = '';
    sendBtn.disabled = true;
    try {
      const payload = { message };
      if (agentSelect && agentSelect.value) payload.agent_type = agentSelect.value;
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (data.response) {
        addMessage(data.response, 'bot');
      } else if (data.error) {
        addMessage('Ошибка: ' + data.error, 'bot');
      }
    } catch (err) {
      addMessage('Ошибка соединения с сервером', 'bot');
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });
});
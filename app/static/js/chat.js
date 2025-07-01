document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    messageInput.addEventListener('input', function() {
        sendButton.disabled = !messageInput.value.trim();
    });
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    messageInput.focus();
});

const sendMessage = async () => {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    addMessage(message, true);
    
    messageInput.value = '';
    updateSendButton();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.error) {
            addMessage('Error: ' + data.error, false, true);
        } else {
            addMessage(data.response, false);
        }
        
    } catch (error) {
        addMessage('Error', false);
    }
    
    updateSendButton();
}

const addMessage = (text, isUser) => {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = 'message ' + (isUser ? 'user' : 'bot');

    const prefix = isUser ? '<strong>You:</strong> ' : '<strong>Gemini:</strong> ';
    messageDiv.innerHTML = prefix + escapeHtml(text);

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

const updateSendButton = () => {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    sendButton.disabled = !messageInput.value.trim();
}

const escapeHtml = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
} 
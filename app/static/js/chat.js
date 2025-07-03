const md = markdownit()

let currentSessionId = null;

document.addEventListener('DOMContentLoaded', function() {
    const msgInput = document.getElementById('msgInput');
    const sendButton = document.getElementById('sendButton');

    msgInput.addEventListener('input', function() {
        sendButton.disabled = !msgInput.value.trim();
    });

    msgInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMsg();
        }
    });

    msgInput.focus();
    
    initializeSession();
});

const initializeSession = async () => {
    try {
        const response = await fetch('/chat/session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const sessionData = await response.json();
        currentSessionId = sessionData.session_id;
        console.log('Initialized session:', currentSessionId);
        
    } catch (error) {
        console.error('Failed to initialize session:', error);
    }
};


const sendMsg = async () => {
    const msgInput = document.getElementById('msgInput');
    const msg = msgInput.value.trim();

    if (!msg) return;

    addMsg(escapeHtml(msg), true);
    msgInput.value = '';
    updateSendButton();
    
    const geminiMsgDiv = createGeminiMsg();
    let accumulatedText = '';
    
    try {
        const eventSource = new EventSource(`/chat/stream/${currentSessionId}?message=${encodeURIComponent(msg)}`);

        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                if (data.error) {
                    updateGeminiMsg(geminiMsgDiv, escapeHtml('Error: ' + data.error));
                    eventSource.close();
                } else if (data.content) {
                    accumulatedText += data.content;
                    updateGeminiMsg(geminiMsgDiv, md.render(accumulatedText));
                } else if (data.done) {
                    eventSource.close();
                }
            } catch (e) {
                console.error('Error parsing SSE data:', e);
                console.log('Raw event data:', event.data);
            }
        };

        eventSource.onerror = function(event) {
            console.error('SSE connection error:', event);
            updateGeminiMsg(geminiMsgDiv, escapeHtml('Error: Connection lost'));
            eventSource.close();
        };

        eventSource.onopen = function(event) {
            console.log('SSE connection opened');
        };
        
    } catch (error) {
        updateGeminiMsg(geminiMsgDiv, escapeHtml('Error: Failed to start conversation'));
        console.error('SSE initialization error:', error);
    }
    
    updateSendButton();
}

const addMsg = (text, isUser) => {
    const chatMsgs = document.getElementById('chatMsgs');
    const msgDiv = document.createElement('div');
    
    msgDiv.className = 'msg ' + (isUser ? 'user' : 'gemini');

    const prefix = isUser ? '<strong>You:</strong> ' : '<strong>Gemini:</strong> ';
    msgDiv.innerHTML = prefix + text;

    chatMsgs.appendChild(msgDiv);
    chatMsgs.scrollTop = chatMsgs.scrollHeight;
    
    return msgDiv;
}

const createGeminiMsg = () => {
    const chatMsgs = document.getElementById('chatMsgs');
    const msgDiv = document.createElement('div');

    msgDiv.className = 'msg gemini'

    msgDiv.innerHTML = '<strong>Gemini:</strong> <span class="typing-indicator">●●●</span>';
    
    chatMsgs.appendChild(msgDiv);
    chatMsgs.scrollTop = chatMsgs.scrollHeight;
    
    return msgDiv;
}

const updateGeminiMsg = (msgDiv, content) => {
    msgDiv.innerHTML = '<strong>Gemini:</strong> ' + content;
    
    const chatMsgs = document.getElementById('chatMsgs');
    chatMsgs.scrollTop = chatMsgs.scrollHeight;
}

const updateSendButton = () => {
    const msgInput = document.getElementById('msgInput');
    const sendButton = document.getElementById('sendButton');
    
    sendButton.disabled = !msgInput.value.trim();
}

const escapeHtml = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

const loadChatHistory = async () => {
    if (!currentSessionId) return;
    
    try {
        const response = await fetch(`/history/${currentSessionId}`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        const chatMsgs = document.getElementById('chatMsgs');
        chatMsgs.innerHTML = '';
        
        data.messages.forEach(message => {
            addMsg(escapeHtml(message.user_message), true);
            addMsg(md.render(message.gemini_response), false);
        });
        
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}

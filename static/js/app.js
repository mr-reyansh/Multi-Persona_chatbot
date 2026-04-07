document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const modeTitle = document.getElementById('current-mode-title');
    
    // Check if we are on the chat page
    if (chatBox) {
        const persona = localStorage.getItem('selectedPersona') || 'friend';
        
        let titleText = "AI Assistant";
        let icon = "";
        
        if (persona === 'teacher') {
            titleText = "Teacher Mode";
            icon = "👨‍🏫";
            modeTitle.style.color = "var(--accent-teacher)";
        } else if (persona === 'doctor') {
            titleText = "Doctor Mode";
            icon = "🩺";
            modeTitle.style.color = "var(--accent-doctor)";
        } else if (persona === 'friend') {
            titleText = "Friend Mode";
            icon = "🤝";
            modeTitle.style.color = "var(--accent-friend)";
        }
        
        modeTitle.innerHTML = `${icon} ${titleText}`;
        
        // Initial greeting
        setTimeout(() => {
            const greeting = `Hello! I am your ${persona}. How can I help you today?`;
            addMessage(greeting, 'bot');
        }, 500);
    }
});

let chatHistory = [];

async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const text = inputField.value.trim();
    
    if (!text) return;
    
    // Add user message
    addMessage(text, 'user');
    inputField.value = '';
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    const persona = localStorage.getItem('selectedPersona') || 'friend';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                persona: persona,
                history: chatHistory
            })
        });
        
        // Add to history BEFORE parsing response to maintain order
        chatHistory.push({role: 'User', content: text});
        
        const data = await response.json();
        
        // Remove typing indicator
        removeElement(typingId);
        
        if (data.response) {
            // Add bot message
            addMessage(data.response, 'bot');
            chatHistory.push({role: 'Assistant', content: data.response});
            
            // Limit history to last 10 exchanges for token efficiency
            if (chatHistory.length > 10) {
                chatHistory = chatHistory.slice(-10);
            }
        } else {
            addMessage('Sorry, I received an empty response from the server.', 'bot');
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeElement(typingId);
        addMessage('Sorry, I encountered an error. Please check your internet connection and API configuration.', 'bot');
    }
}

function handleEnter(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

function addMessage(text, sender) {
    const chatBox = document.getElementById('chat-box');
    if (!chatBox) return;

    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender === 'user' ? 'msg-user' : 'msg-bot');
    
    // Basic formatting for newlines
    msgDiv.innerHTML = text.replace(/\n/g, '<br>');
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const chatBox = document.getElementById('chat-box');
    const id = 'typing-' + Date.now();
    
    const indicator = document.createElement('div');
    indicator.id = id;
    indicator.classList.add('typing-indicator');
    indicator.innerHTML = `
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    `;
    
    chatBox.appendChild(indicator);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return id;
}

function removeElement(id) {
    const el = document.getElementById(id);
    if (el) {
        el.remove();
    }
}

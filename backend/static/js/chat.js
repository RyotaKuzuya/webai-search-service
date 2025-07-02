let socket = null;
let isConnected = false;
let currentMessageDiv = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    setupEventListeners();
});

function initializeWebSocket() {
    // Connect to WebSocket
    socket = io({
        transports: ['websocket'],
        upgrade: false
    });
    
    // Connection events
    socket.on('connect', function() {
        console.log('Connected to WebSocket');
        updateConnectionStatus('connected');
        isConnected = true;
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from WebSocket');
        updateConnectionStatus('disconnected');
        isConnected = false;
    });
    
    socket.on('connect_error', function(error) {
        console.error('Connection error:', error);
        updateConnectionStatus('disconnected');
    });
    
    // Message events
    socket.on('connected', function(data) {
        console.log('Server message:', data.status);
    });
    
    socket.on('message_received', function(data) {
        if (currentMessageDiv) {
            currentMessageDiv.querySelector('.message-content').textContent = data.status;
        }
    });
    
    socket.on('stream_chunk', function(data) {
        handleStreamChunk(data.chunk);
    });
    
    socket.on('stream_complete', function(data) {
        console.log('Stream complete:', data.status);
        currentMessageDiv = null;
        enableInput();
    });
    
    socket.on('error', function(data) {
        console.error('Server error:', data.error);
        if (currentMessageDiv) {
            currentMessageDiv.querySelector('.message-content').textContent = 
                `Error: ${data.error}`;
            currentMessageDiv.classList.add('message-error');
        }
        currentMessageDiv = null;
        enableInput();
    });
}

function setupEventListeners() {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', async function() {
        try {
            const response = await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Logout error:', error);
        }
    });
    
    // Message form
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    // Allow Ctrl+Enter to send
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || !isConnected) {
        return;
    }
    
    // Clear input
    messageInput.value = '';
    
    // Add user message to UI
    addMessage(message, 'user');
    
    // Add AI thinking message
    currentMessageDiv = addMessage('Thinking...', 'ai', true);
    
    // Disable input while processing
    disableInput();
    
    // Send message via WebSocket
    socket.emit('message', { message: message });
}

function addMessage(content, sender, isThinking = false) {
    const messageContainer = document.getElementById('messageContainer');
    
    // Remove welcome message if it exists
    const welcomeMessage = messageContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${sender}`;
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    headerDiv.textContent = sender === 'user' ? 'You' : 'WebAI';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    if (isThinking) {
        contentDiv.className += ' message-thinking';
    }
    contentDiv.textContent = content;
    
    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    
    messageContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messageContainer.scrollTop = messageContainer.scrollHeight;
    
    return messageDiv;
}

function handleStreamChunk(chunk) {
    if (!currentMessageDiv) {
        currentMessageDiv = addMessage('', 'ai');
    }
    
    const contentDiv = currentMessageDiv.querySelector('.message-content');
    contentDiv.classList.remove('message-thinking');
    
    // Parse chunk data
    try {
        const data = JSON.parse(chunk);
        if (data.content) {
            // Append content
            contentDiv.textContent += data.content;
        } else if (data.thinking) {
            // Show thinking process
            contentDiv.textContent = `Thinking: ${data.thinking}`;
            contentDiv.classList.add('message-thinking');
        }
    } catch (e) {
        // If not JSON, append as text
        contentDiv.textContent += chunk;
    }
    
    // Scroll to bottom
    const messageContainer = document.getElementById('messageContainer');
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

function updateConnectionStatus(status) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    statusDot.className = 'status-dot';
    
    switch(status) {
        case 'connected':
            statusDot.classList.add('connected');
            statusText.textContent = 'Connected';
            break;
        case 'disconnected':
            statusDot.classList.add('disconnected');
            statusText.textContent = 'Disconnected';
            break;
        case 'connecting':
            statusDot.classList.add('connecting');
            statusText.textContent = 'Connecting...';
            break;
    }
}

function disableInput() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    messageInput.disabled = true;
    sendBtn.disabled = true;
    
    // Show loading state
    sendBtn.querySelector('.btn-text').style.display = 'none';
    sendBtn.querySelector('.btn-loading').style.display = 'inline-flex';
}

function enableInput() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    messageInput.disabled = false;
    sendBtn.disabled = false;
    messageInput.focus();
    
    // Hide loading state
    sendBtn.querySelector('.btn-text').style.display = 'inline';
    sendBtn.querySelector('.btn-loading').style.display = 'none';
}
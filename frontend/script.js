const API_BASE_URL = 'http://localhost:8000/api';

const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const suggestionChips = document.querySelectorAll('.suggestion-chip');

// SVG Icons
const USER_AVATAR = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;
const ASSISTANT_AVATAR = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>`;

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
}

function formatText(text) {
    // Basic formatting: convert newlines to <br> and bold text to <strong>
    let formatted = escapeHTML(text).replace(/\n/g, '<br>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return `<p>${formatted}</p>`;
}

function createMessageElement(type, contentHTML, extraClass = '') {
    const div = document.createElement('div');
    div.className = `message ${type}-message ${extraClass}`;
    
    const avatar = type === 'user' ? USER_AVATAR : ASSISTANT_AVATAR;
    
    div.innerHTML = `
        <div class="avatar ${type}-avatar">
            ${avatar}
        </div>
        <div class="message-content">
            ${contentHTML}
        </div>
    `;
    
    return div;
}

function showLoadingIndicator() {
    const content = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    const msgElem = createMessageElement('assistant', content, 'loading-message');
    msgElem.id = 'loading-indicator';
    chatWindow.appendChild(msgElem);
    scrollToBottom();
}

function removeLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function addMessage(type, data) {
    let contentHTML = '';
    let extraClass = '';
    
    if (type === 'user') {
        contentHTML = `<p>${escapeHTML(data)}</p>`;
    } else {
        // Assistant message formatting based on response type
        contentHTML = formatText(data.answer);
        
        if (data.type === 'refusal' || data.type === 'PII_DETECTED') {
            extraClass = 'refusal-message';
        } else if (data.type === 'error') {
            extraClass = 'error-message';
        }
        
        // Add citation if available
        if (data.citation) {
            contentHTML += `
                <a href="${escapeHTML(data.citation.url)}" target="_blank" rel="noopener noreferrer" class="citation-link">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    Source: ${escapeHTML(data.citation.title)}
                </a>
            `;
        }
        
        // Add last updated if available
        if (data.last_updated) {
            contentHTML += `
                <div class="message-footer">
                    Last updated from sources: ${escapeHTML(data.last_updated)}
                </div>
            `;
        }
    }
    
    const msgElem = createMessageElement(type, contentHTML, extraClass);
    chatWindow.appendChild(msgElem);
    scrollToBottom();
}

async function sendMessage(query) {
    if (!query.trim()) return;
    
    // UI Updates before sending
    addMessage('user', query);
    userInput.value = '';
    sendButton.disabled = true;
    showLoadingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query.trim() })
        });
        
        const data = await response.json();
        
        removeLoadingIndicator();
        
        if (!response.ok) {
            // Handle HTTP errors
            addMessage('assistant', {
                answer: data.detail || "An error occurred while processing your request.",
                type: "error"
            });
        } else {
            // Success
            addMessage('assistant', data);
        }
        
    } catch (error) {
        console.error("Chat API error:", error);
        removeLoadingIndicator();
        addMessage('assistant', {
            answer: "Unable to connect to the server. Please ensure the backend is running.",
            type: "error"
        });
    } finally {
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Event Listeners
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(userInput.value);
});

suggestionChips.forEach(chip => {
    chip.addEventListener('click', () => {
        sendMessage(chip.textContent);
    });
});

// Initial focus
userInput.focus();

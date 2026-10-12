/**
 * SmartBot - Frontend Integration Script
 * Pure Vanilla JavaScript (ES6+)
 * 
 * Features:
 * - Fetch API with async/await
 * - Safe DOM manipulation (textContent) preventing XSS
 * - CSRF token extraction and submission
 * - Asynchronous chat dispatch with animated typing indicator
 * - Persistent chat history retrieval (GET /api/history/)
 * - Chat history clearance (DELETE /api/history/clear/)
 * - Quick prompt buttons interaction
 * - Auto-scroll, duplicate submission prevention, and mobile navigation
 */

document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // 1. DOM Element Selectors
    // =========================================================================
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatWindow = document.getElementById('chatWindow');
    const typingIndicator = document.getElementById('typingIndicator');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const quickButtons = document.getElementById('quickButtons');
    const charCount = document.getElementById('charCount');
    const chatAlert = document.getElementById('chatAlert');
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');

    // Bot mascot image URL (rendered via Django template or fallback)
    const BOT_AVATAR_SRC = '/static/images/chatbot.svg';

    let isProcessing = false;

    // =========================================================================
    // 2. CSRF Token Utility
    // =========================================================================
    /**
     * Retrieves the CSRF token required by Django for POST and DELETE requests.
     * Checks the meta tag first, then cookies, then the hidden form input.
     */
    function getCsrfToken() {
        // Option A: Read from <meta name="csrf-token">
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag && metaTag.content) {
            return metaTag.content;
        }

        // Option B: Read from cookie 'csrftoken'
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, val] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(val);
            }
        }

        // Option C: Read from hidden input field
        const inputToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (inputToken && inputToken.value) {
            return inputToken.value;
        }

        return '';
    }

    // =========================================================================
    // 3. UI Helpers & Safe DOM Message Rendering
    // =========================================================================
    /**
     * Formats current timestamp or parses given date string into a readable time.
     */
    function formatTime(dateStr = null) {
        const date = dateStr ? new Date(dateStr) : new Date();
        if (isNaN(date.getTime())) {
            return 'Just now';
        }
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Automatically scrolls the chat window to the bottom.
     */
    function scrollToBottom() {
        chatWindow.scrollTo({
            top: chatWindow.scrollHeight,
            behavior: 'smooth'
        });
    }

    /**
     * Displays a temporary banner alert in the chat window.
     */
    function showAlert(text, type = 'info', timeout = 4000) {
        chatAlert.textContent = text;
        chatAlert.className = `chat-alert ${type}`;
        chatAlert.classList.remove('hidden');

        if (timeout > 0) {
            setTimeout(() => {
                chatAlert.classList.add('hidden');
            }, timeout);
        }
    }

    /**
     * Safely constructs and appends a chat message element to the chat body.
     * Uses textContent exclusively for user-generated strings to prevent XSS.
     * 
     * @param {string} sender - 'User' or 'Bot'
     * @param {string} text - Message text content
     * @param {string|null} timestamp - Optional timestamp string
     */
    function appendMessage(sender, text, timestamp = null) {
        const isBot = sender.toLowerCase() === 'bot';

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isBot ? 'bot-message' : 'user-message'}`;

        // Avatar container
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'msg-avatar';

        if (isBot) {
            const avatarImg = document.createElement('img');
            avatarImg.src = BOT_AVATAR_SRC;
            avatarImg.alt = 'SmartBot';
            avatarDiv.appendChild(avatarImg);
        } else {
            const userBadge = document.createElement('div');
            userBadge.className = 'user-avatar-badge';
            userBadge.textContent = 'You';
            avatarDiv.appendChild(userBadge);
        }

        // Content wrapper
        const contentDiv = document.createElement('div');
        contentDiv.className = 'msg-content';

        // Message bubble (SAFE: textContent used here)
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'msg-bubble';

        const textP = document.createElement('p');
        textP.textContent = text; // Safe text insertion
        bubbleDiv.appendChild(textP);

        // Timestamp
        const timeSpan = document.createElement('span');
        timeSpan.className = 'msg-timestamp';
        timeSpan.textContent = formatTime(timestamp);

        contentDiv.appendChild(bubbleDiv);
        contentDiv.appendChild(timeSpan);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        // Insert before typing indicator
        chatWindow.insertBefore(messageDiv, typingIndicator);
        scrollToBottom();
    }

    /**
     * Shows the animated typing indicator.
     */
    function showTypingIndicator() {
        typingIndicator.classList.remove('hidden');
        scrollToBottom();
    }

    /**
     * Hides the animated typing indicator.
     */
    function hideTypingIndicator() {
        typingIndicator.classList.add('hidden');
    }

    /**
     * Toggles form input and buttons to prevent duplicate submissions.
     */
    function setFormState(disabled) {
        isProcessing = disabled;
        messageInput.disabled = disabled;
        sendBtn.disabled = disabled;
        if (!disabled) {
            messageInput.focus();
        }
    }

    // =========================================================================
    // 4. API Service Calls
    // =========================================================================
    /**
     * Sends a user message to Django backend (POST /api/chat/).
     */
    async function sendMessage(rawText) {
        const trimmed = (rawText || '').trim();

        if (!trimmed) {
            showAlert('Please type a message before sending.', 'error');
            return;
        }

        if (trimmed.length > 500) {
            showAlert('Message cannot exceed 500 characters.', 'error');
            return;
        }

        if (isProcessing) return;

        // 1. Display user message in chat window immediately
        appendMessage('User', trimmed);

        // 2. Clear input field and reset character count
        messageInput.value = '';
        updateCharCount();

        // 3. Disable controls and display typing indicator
        setFormState(true);
        showTypingIndicator();

        try {
            const csrfToken = getCsrfToken();

            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message: trimmed })
            });

            const data = await response.json();

            // Simulate slight natural typing latency (450ms) for enhanced UX
            await new Promise(resolve => setTimeout(resolve, 450));

            hideTypingIndicator();

            if (response.ok) {
                // Display bot's response
                appendMessage('Bot', data.bot_response);
            } else {
                // Server returned an error status (e.g. 400 or 500)
                const errorMsg = data.error || 'Server error occurred.';
                showAlert(errorMsg, 'error');
                appendMessage('Bot', 'I encountered an issue processing that. Please try again.');
            }

        } catch (networkError) {
            console.error('Fetch communication error:', networkError);
            hideTypingIndicator();
            showAlert('Network error: Unable to connect to Django server. Is it running?', 'error');
            appendMessage('Bot', 'I cannot connect to the server right now. Please check your network or server status.');
        } finally {
            setFormState(false);
            scrollToBottom();
        }
    }

    /**
     * Fetches previous conversation history for the current session (GET /api/history/).
     */
    async function loadChatHistory() {
        try {
            const response = await fetch('/api/history/', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }

            const data = await response.json();
            const messages = data.messages || [];

            if (messages.length > 0) {
                // Clear initial static welcome message if actual saved history exists
                const initialWelcome = chatWindow.querySelector('[data-msg-id="welcome"]');
                if (initialWelcome) {
                    initialWelcome.remove();
                }

                // Render saved messages
                messages.forEach(msg => {
                    appendMessage(msg.sender, msg.message, msg.created_at);
                });
            }

            scrollToBottom();
        } catch (err) {
            console.warn('Unable to load chat history:', err);
            // Non-critical: User can still converse smoothly even if history retrieval fails
        }
    }

    /**
     * Clears all session conversation records (DELETE /api/history/clear/).
     */
    async function clearChatHistory() {
        const confirmed = confirm('Are you sure you want to clear this conversation history?');
        if (!confirmed) return;

        try {
            setFormState(true);
            const csrfToken = getCsrfToken();

            const response = await fetch('/api/history/clear/', {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                // Remove all rendered messages except typing indicator
                const allMessages = chatWindow.querySelectorAll('.chat-message:not(.typing-indicator-wrapper)');
                allMessages.forEach(el => el.remove());

                // Re-insert fresh welcome message
                appendMessage(
                    'Bot',
                    'Chat history has been cleared! How can I assist you now?'
                );

                showAlert('Chat history cleared successfully.', 'success');
            } else {
                showAlert(data.error || 'Failed to clear chat history.', 'error');
            }
        } catch (err) {
            console.error('Error clearing history:', err);
            showAlert('Network error while clearing history.', 'error');
        } finally {
            setFormState(false);
        }
    }

    // =========================================================================
    // 5. Event Listeners
    // =========================================================================
    // Form submit listener
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage(messageInput.value);
    });

    // Enter key submission support (Shift+Enter allows multi-line if textarea, but text input submits on Enter)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.requestSubmit();
        }
    });

    // Character counter listener
    function updateCharCount() {
        const length = messageInput.value.length;
        charCount.textContent = `${length}/500`;
        if (length >= 480) {
            charCount.style.color = 'var(--danger)';
        } else {
            charCount.style.color = 'var(--text-muted)';
        }
    }

    messageInput.addEventListener('input', updateCharCount);

    // Quick message buttons click handler
    quickButtons.addEventListener('click', (e) => {
        const targetBtn = e.target.closest('.quick-btn');
        if (targetBtn && targetBtn.dataset.message) {
            sendMessage(targetBtn.dataset.message);
        }
    });

    // Clear chat button listener
    clearChatBtn.addEventListener('click', () => {
        clearChatHistory();
    });

    // Mobile navigation drawer toggle
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });

        // Close mobile drawer when clicking any link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
            });
        });
    }

    // =========================================================================
    // 6. Application Initialization
    // =========================================================================
    updateCharCount();
    loadChatHistory();
});

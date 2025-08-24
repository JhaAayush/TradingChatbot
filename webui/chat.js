document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const themeSwitcher = document.getElementById('theme-switcher');
    const moonIcon = document.getElementById('moon-icon');
    const sunIcon = document.getElementById('sun-icon');
    const downloadButton = document.getElementById('download-chat');

    // --- RASA SERVER CONNECTION ---
    // Replace with your Rasa server URL
    const RASA_SERVER_URL = 'http://localhost:5005/webhooks/rest/webhook';

    // Function to send a message to the Rasa server
    async function sendMessageToRasa(message) {
        showTypingIndicator();
        try {
            const response = await fetch(RASA_SERVER_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sender: 'user', // A unique ID for the user
                    message: message,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            hideTypingIndicator();
            displayBotMessages(data);

        } catch (error) {
            hideTypingIndicator();
            console.error("Error sending message to Rasa:", error);
            displayBotMessage("Sorry, I'm having trouble connecting. Please try again later.");
        }
    }

    // --- MESSAGE DISPLAY FUNCTIONS ---

    // Function to add a message to the chat window
    function addMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);

        const bubbleElement = document.createElement('div');
        bubbleElement.classList.add('bubble');
        bubbleElement.textContent = text;

        messageElement.appendChild(bubbleElement);
        chatMessages.appendChild(messageElement);

        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Display a message from the user
    function displayUserMessage(message) {
        addMessage('user', message);
    }

    // Display a single message from the bot
    function displayBotMessage(message) {
        addMessage('bot', message);
    }

    // Display multiple messages from the bot (Rasa can send multiple responses)
    function displayBotMessages(responses) {
        if (responses && responses.length > 0) {
            responses.forEach(response => {
                if (response.text) {
                    displayBotMessage(response.text);
                }
            });
        } else {
            displayBotMessage("I'm not sure how to respond to that.");
        }
    }


    // --- TYPING INDICATOR ---
    function showTypingIndicator() {
        typingIndicator.classList.remove('hidden');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        typingIndicator.classList.add('hidden');
    }

    // --- PDF DOWNLOAD FUNCTION ---
    function downloadChatAsPDF() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        const messages = chatMessages.querySelectorAll('.message');
        let y = 15; // Initial Y position for text
        const pageHeight = doc.internal.pageSize.height;
        const margin = 10;
        const maxLineWidth = doc.internal.pageSize.width - margin * 2;

        doc.setFontSize(18);
        doc.text("Chat History", margin, y);
        y += 10;
        doc.setFontSize(12);

        messages.forEach(message => {
            const isUser = message.classList.contains('user');
            const sender = isUser ? 'You: ' : 'Bot: ';
            const text = message.querySelector('.bubble').textContent;

            // Use splitTextToSize for automatic line wrapping
            const lines = doc.splitTextToSize(sender + text, maxLineWidth);

            // Check if there's enough space for the next message, otherwise add a new page
            if (y + (lines.length * 7) > pageHeight - margin) {
                doc.addPage();
                y = margin;
            }

            doc.text(lines, margin, y);
            y += (lines.length * 7); // Increment y position based on number of lines
            y += 5; // Add a little space between messages
        });

        doc.save('rasa-chat-history.pdf');
    }


    // --- EVENT LISTENERS ---

    // Handle sending a message
    function handleSendMessage() {
        const message = userInput.value.trim();
        if (message) {
            displayUserMessage(message);
            sendMessageToRasa(message);
            userInput.value = '';
        }
    }

    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            handleSendMessage();
        }
    });

    // Handle PDF download
    downloadButton.addEventListener('click', downloadChatAsPDF);


    // --- THEME SWITCHER ---
    themeSwitcher.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        document.documentElement.classList.toggle('dark'); // For Tailwind CSS

        moonIcon.classList.toggle('hidden');
        sunIcon.classList.toggle('hidden');

        if (document.body.classList.contains('dark-theme')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });

    // Load theme from local storage
    function loadTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            document.documentElement.classList.add('dark');
            moonIcon.classList.add('hidden');
            sunIcon.classList.remove('hidden');
        } else {
            document.body.classList.remove('dark-theme');
            document.documentElement.classList.remove('dark');
            moonIcon.classList.remove('hidden');
            sunIcon.classList.add('hidden');
        }
    }

    // Initial load
    loadTheme();
    displayBotMessage("Hello! How can I help you today?");
});

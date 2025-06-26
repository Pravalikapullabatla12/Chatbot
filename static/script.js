document.addEventListener('DOMContentLoaded', function () {
  const chatMessages = document.getElementById('chat-messages');
  const userInput = document.getElementById('user-input');
  const sendButton = document.getElementById('send-button');

  function addMessage(message, isUser) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
      messageDiv.textContent = message;
      chatMessages.appendChild(messageDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function sendMessage() {
      const message = userInput.value.trim();
      if (message === '') return;

      addMessage(message, true);
      userInput.value = '';

      fetch('/chat', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: message })
      })
          .then(response => response.json())
          .then(data => {
              addMessage(data.response, false);
          })
          .catch(error => {
              console.error('Error:', error);
              addMessage('Sorry, there was an error processing your request.', false);
          });
  }

  sendButton.addEventListener('click', sendMessage);

  userInput.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
          sendMessage();
      }
  });
});

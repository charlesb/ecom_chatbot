console.log('Hello, World!');

async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
    });
    const data = await response.json();
    document.getElementById('chat-window').innerHTML += `<p>User: ${userInput}</p><p>Bot: ${data.botMessage}</p>`;
}
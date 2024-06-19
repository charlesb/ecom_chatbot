async function sendMessage() {
    // Check if this is the first message of the session
    const context = (document.getElementById('chat-window').innerHTML !== '')
    console.log(context)
    const userInput = document.getElementById('user-input').value;
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput, context: context})
    });
    const data = await response.json();
    document.getElementById('chat-window').innerHTML += `<p><strong>User:</strong> ${userInput}</p><p><strong>Bot:</strong> ${data.botMessage}</p>`;
}
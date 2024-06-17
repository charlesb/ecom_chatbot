require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const { Configuration, OpenAIApi } = require('openai');
const { Client } = require('cassandra-driver');
const { Client: OpenSearchClient } = require('@opensearch-project/opensearch');
const path = require('path');

const app = express();
app.use(bodyParser.json());
app.use(express.static(__dirname)); // Serve static files from the root directory

// const cassandraClient = new Client({
//     cloud: { secureConnectBundle: 'path_to_secure_bundle' },
//     credentials: { username: 'your_username', password: 'your_password' }
// });

const openai = new OpenAIApi(new Configuration({
    apiKey: process.env.MY_OPENAI_API_KEY
}));

const openSearchClient = new OpenSearchClient({
    node: process.env.OPENSEARCH_URI
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/chat', async (req, res) => {
    const userMessage = req.body.message;
    
    // Call OpenAI API
    const response = await axios.post('https://api.openai.com/v1/chat/completions', {
        messages: [{ role: 'user', content: userMessage }],
        model: 'gpt-4o'
    }, {
        headers: { 'Authorization': `Bearer YOUR_API_KEY` }
    });
    
    const botMessage = response.data.choices[0].message.content;
    
    // Save conversation to Cassandra
    // await cassandraClient.execute('INSERT INTO conversations (user_id, message, response) VALUES (?, ?, ?)', ['user_id', userMessage, botMessage]);
    
    res.json({ botMessage });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});


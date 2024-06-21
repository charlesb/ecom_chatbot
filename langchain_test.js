require('dotenv').config()
require('cheerio');
const readline = require('readline');
const { CheerioWebBaseLoader } = require("@langchain/community/document_loaders/web/cheerio");
const { RecursiveCharacterTextSplitter } = require("langchain/text_splitter");
const { MemoryVectorStore } = require("langchain/vectorstores/memory");
const { OpenAIEmbeddings, ChatOpenAI } = require("@langchain/openai");
const { ChatPromptTemplate, MessagesPlaceholder } = require("@langchain/core/prompts");
const { RunnableSequence, RunnablePassthrough, RunnableWithMessageHistory } = require("@langchain/core/runnables");
const { StringOutputParser } = require("@langchain/core/output_parsers");
const { formatDocumentsAsString } = require("langchain/util/document");
const { Redis } = require("ioredis");
const { RedisChatMessageHistory } = require("@langchain/community/stores/message/ioredis");

// Create readline.Interface instance
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Define the client and store
const client = new Redis(process.env.REDIS_URI);

const apiKey = process.env.MY_OPENAI_API_KEY;

const llm = new ChatOpenAI({ 
    apiKey: apiKey,
    model: "gpt-3.5-turbo",
    temperature: 0
});

const loader = new CheerioWebBaseLoader(
    "https://lilianweng.github.io/posts/2023-06-23-agent/"
);
  
const textSplitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200,
});

const contextualizeQSystemPrompt = `Given a chat history and the latest user question
which might reference context in the chat history, formulate a standalone question
which can be understood without the chat history. Do NOT answer the question,
just reformulate it if needed and otherwise return it as is.`;

const contextualizeQPrompt = ChatPromptTemplate.fromMessages([
    ["system", contextualizeQSystemPrompt],
    new MessagesPlaceholder("history"),
    ["human", "{question}"]
]);

const qaSystemPrompt = `You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

{context}`;

const qaPrompt = ChatPromptTemplate.fromMessages([
    ["system", qaSystemPrompt],
    new MessagesPlaceholder("history"),
    ["human", "{question}"]
]);

const contextualizeQChain = contextualizeQPrompt.pipe(llm).pipe(new StringOutputParser());

const contextualizedQuestion = (input) => {
    if ("history" in input) {
      return contextualizeQChain;
    }
    return input.question;
};

async function runChainWithChatHistory(question) {
    const docs = await loader.load();
    const splits = await textSplitter.splitDocuments(docs);
    const vectorStore = await MemoryVectorStore.fromDocuments(
        splits,
        new OpenAIEmbeddings({
            apiKey: apiKey,
            model: "text-embedding-3-small",
        })
    );
    // Retrieve and generate using the relevant snippets of the blog.
    const retriever = vectorStore.asRetriever();

    const ragChain = RunnableSequence.from([
        RunnablePassthrough.assign({
          context: (input) => {
            if ("history" in input) {
              const chain = contextualizedQuestion(input);
              return chain.pipe(retriever).pipe(formatDocumentsAsString);
            }
            return "";
          },
        }),
        qaPrompt,
        llm
    ]);         

    const chainWithHistory = new RunnableWithMessageHistory({
        runnable: ragChain,
        getMessageHistory: (sessionId) =>
            new RedisChatMessageHistory({
                sessionId: sessionId,
                sessionTTL: 300,
                client,
          }),
        inputMessagesKey: "question",
        historyMessagesKey: "history",
    });

    const result = await chainWithHistory.invoke({
        question: question
    },
    {
        configurable: {
        sessionId: "551dfc94-764a-4839-b8db-e6f04b5715c6"
    },
    });

    return result.content;
}

// Function to ask question and wait for answer
function askQuestion(query) {
    return new Promise((resolve) => rl.question(query, resolve));
}

async function promptLoop() {
    let userInput;
    while (userInput !== 'exit') {
      userInput = await askQuestion('What is your question? (type "exit" to quit) ');
      console.log(`You asked: ${userInput}`);
      // Here you can add the logic to process the question, e.g., runChainWithChatHistory(userInput).then(console.log);
      if (userInput !== 'exit') {
        await runChainWithChatHistory(userInput).then(console.log); 
      }
    }
    rl.close(); // Close the readline interface when done
    process.exit();
  }
  
  promptLoop();
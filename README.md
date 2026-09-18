
# 🤖 Multi-Agent AI Chatbot

A LangGraph-based multi-agent AI chatbot with RAG, web search, CSV analysis, PostgreSQL chat persistence, and Mem0-powered long-term memory.

## 🚀 Features

- **Multi-Agent Architecture:** Supervisor-based workflow using LangGraph.
- **Web Search Agent:** Retrieves information from the web.
- **RAG Agent:** Answers questions using uploaded documents.
- **CSV Agent:** Analyzes and answers questions from CSV files.
- **Long-Term Memory:** Mem0 integration for storing and retrieving user preferences and useful facts.
- **Short-Term Memory:** Maintains conversation context using LangGraph checkpoints.
- **Chat Persistence:** PostgreSQL-based storage for multiple users and chat sessions.
- **Local LLM:** Ollama-powered language models and embeddings.
- **Streamlit UI:** Interactive chatbot interface with chat history and sidebar navigation.

## 🏗️ Architecture

```text
                    User Query
                        |
                        v
                    Guardrail
                        |
                        v
                   Supervisor
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
     Web Search       RAG Agent     CSV Agent
          |             |             |
          +-------------+-------------+
                        |
                        v
                   Supervisor
                        |
                        v
                    Response
                        |
                        v
                 Mem0 Memory
               (Save Memories)
```

## 🛠️ Tech Stack

- **Programming Language:** Python
- **Agent Framework:** LangGraph, LangChain
- **LLM:** Ollama
- **Embedding Model:** Ollama `qwen3-embedding:4b`
- **Vector Database:** ChromaDB
- **Long-Term Memory:** Mem0 Open Source
- **Database:** PostgreSQL
- **Frontend:** Streamlit
- **RAG:** Document chunking, embeddings, and semantic retrieval

## 📂 Project Structure

```text
multi-agent-chatbot/
│
├── app.py                  # Streamlit application
├── graph.py                # LangGraph workflow
├── database.py             # PostgreSQL checkpointer
├── chat_database.py        # Chat session management
├── memory_manager.py       # Mem0 memory integration
│
├── web_search_agent.py     # Web search agent
├── rag_agent.py            # RAG agent
├── csv_agent.py            # CSV analysis agent
│
├── documents/              # Documents for RAG
├── chroma_db/              # RAG vector database
├── mem0_chroma_db/         # Mem0 vector database
│
└── requirements.txt
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/multi-agent-chatbot.git
cd multi-agent-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv multi-agent-chatbot
```

Activate the environment on Windows:

```bash
multi-agent-chatbot\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Run Ollama

Download Ollama:

https://ollama.com/download

Ensure Ollama is running and the required models are available.

Check installed models:

```bash
ollama list
```

### 5. Configure PostgreSQL

Create a PostgreSQL database named:

```text
chatbot
```

Update your PostgreSQL connection string in the database configuration:

```python
DB_URI = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/chatbot"
```

The PostgreSQL database is used for LangGraph checkpoint persistence and chat session management.

### 6. Run the Application

```bash
streamlit run app.py
```

## 🧠 Memory Management

This project uses Mem0 Open Source for long-term memory.

Mem0 is used to:

- Extract useful user preferences and facts.
- Store memories locally using ChromaDB.
- Retrieve relevant memories for future queries.
- Improve responses using personalized context.

Example:

```text
User: I prefer Python for coding.

Later:

User: Give me a coding implementation.

The chatbot retrieves the relevant preference
and uses it to personalize the response.
```

## 🔐 Data Persistence

| Component | Responsibility |
|---|---|
| PostgreSQL | LangGraph checkpoints and chat sessions |
| ChromaDB | RAG document embeddings |
| Mem0 + ChromaDB | Long-term user memories |

## 🔮 Future Enhancements

- Authentication and role-based access control.
- Production deployment on AWS.
- Advanced memory management using Mem0.
- Improved guardrails and query rephrasing.
- Streaming responses.
- Monitoring and evaluation of agent performance.

## 👨‍💻 Author

**Anish Deepak**

Generative AI Developer | Agentic AI | LangGraph | LangChain | AWS Bedrock

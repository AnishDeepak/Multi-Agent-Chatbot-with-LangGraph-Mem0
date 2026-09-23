# 🤖 Multi-Agent AI Chatbot

A LangGraph-based multi-agent AI chatbot with RAG, web search, CSV analysis, PostgreSQL persistence, Mem0-powered long-term memory, and Langfuse observability and evaluation.

## 🚀 Features

* **Multi-Agent Architecture:** Supervisor-based workflow using LangGraph.
* **Guardrails:** Validates user queries before routing them to agents.
* **Web Search Agent:** Retrieves and summarizes information from the web.
* **RAG Agent:** Answers questions using uploaded documents.
* **CSV Agent:** Analyzes and answers questions from CSV files.
* **Long-Term Memory:** Mem0 integration for storing and retrieving user preferences and useful facts.
* **Short-Term Memory:** LangGraph checkpointing for maintaining conversation context.
* **Chat Persistence:** PostgreSQL-based storage for multiple users and chat sessions.
* **Local LLM:** Ollama-powered language models and embeddings.
* **Observability:** Langfuse integration for tracing multi-agent executions, LLM calls, and tool usage.
* **Agent Evaluation:** Langfuse-based evaluation of agent responses and execution quality.
* **Streamlit UI:** Interactive chatbot interface with chat history and sidebar navigation.

## 🏗️ Architecture

```text
                         User Query
                             |
                             v
                         Mem0 Search
                             |
                             v
                         Guardrail
                             |
                             v
                        Supervisor
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
        Web Search        RAG Agent      CSV Agent
           Agent              |              |
              |               |              |
              +---------------+--------------+
                             |
                             v
                         Supervisor
                             |
                             v
                       Final Response
                             |
                +------------+------------+
                |                         |
                v                         v
          Save to Mem0              Langfuse Trace
                                      |
                                      v
                                  Evaluation
```

## 🛠️ Tech Stack

* **Programming Language:** Python
* **Agent Framework:** LangGraph, LangChain
* **LLM:** Ollama
* **Embedding Model:** Ollama `qwen3-embedding:4b`
* **Vector Database:** ChromaDB
* **Long-Term Memory:** Mem0 Open Source
* **Database:** PostgreSQL
* **Observability & Evaluation:** Langfuse
* **Frontend:** Streamlit
* **RAG:** Document chunking, embeddings, and semantic retrieval

## 📂 Project Structure

```text
multi-agent-chatbot/
│
├── app.py                  # Streamlit application
├── graph.py                # LangGraph workflow
├── database.py             # PostgreSQL checkpointer
├── chat_database.py        # Chat session management
├── memory_manager.py       # Mem0 memory integration
├── evaluation.py           # Agent evaluation
│
├── web_search_agent.py     # Web search agent
├── rag_agent.py            # RAG agent
├── csv_agent.py            # CSV analysis agent
│
├── documents/              # Documents for RAG
├── document_folder/        # CSV files for CSV analysis
├── chroma_db/              # RAG vector database
├── mem0_chroma_db/         # Mem0 vector database
│
├── .env                    # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
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

Pull the required models if they are not already available.

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL
POSTGRES_URI=postgresql://postgres:YOUR_PASSWORD@localhost:5432/chatbot

# Langfuse
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Load environment variables in Python using:

```python
from dotenv import load_dotenv

load_dotenv()
```

**Do not commit the `.env` file to Git.**

Add the following to `.gitignore`:

```text
.env
```

### 6. Configure PostgreSQL

Create a PostgreSQL database named:

```text
chatbot
```

PostgreSQL is used for:

* LangGraph checkpoint persistence.
* Chat session management.
* Multi-user conversation storage.

### 7. Run the Application

```bash
streamlit run app.py
```

## 🧠 Memory Management

This project uses **Mem0 Open Source** for long-term memory.

Mem0 is used to:

* Extract useful user preferences and facts.
* Store memories locally using ChromaDB.
* Retrieve relevant memories for future queries.
* Provide personalized context to the agent.

Example:

```text
User:
I prefer Python for coding.

Later:

User:
Give me a coding implementation.

        ↓

Mem0 retrieves:
"User prefers Python for coding."

        ↓

Relevant memory is provided to the agent.
```

### Memory Architecture

```text
User Query
    |
    v
Mem0 Search
    |
    v
Relevant Memories
    |
    v
LangGraph Agent
    |
    v
Response
    |
    v
Mem0 Save
```

## 📊 Langfuse Observability & Evaluation

Langfuse is integrated to monitor and evaluate the complete multi-agent execution.

A typical trace contains:

```text
User Query
    |
    v
Guardrail
    |
    v
Supervisor
    |
    +----> Web Search Agent
    |
    +----> RAG Agent
    |
    +----> CSV Agent
    |
    v
Final Response
```

Langfuse provides visibility into:

* Complete LangGraph traces.
* Supervisor decisions.
* Individual agent executions.
* LLM calls.
* Tool calls.
* Inputs and outputs.
* Latency and token usage.
* User/session metadata.
* Evaluation scores.

### Evaluation

The final agent response can be evaluated using LLM-based evaluation criteria such as:

* **Correctness**
* **Relevance**
* **Helpfulness**
* **Faithfulness**

Evaluation results are associated with the corresponding Langfuse trace, allowing agent execution and evaluation results to be analyzed together.

## 🔐 Data Persistence

| Component       | Responsibility                          |
| --------------- | --------------------------------------- |
| PostgreSQL      | LangGraph checkpoints and chat sessions |
| ChromaDB        | RAG document embeddings                 |
| Mem0 + ChromaDB | Long-term user memories                 |
| Langfuse        | Tracing, observability, and evaluation  |

## 🔄 Complete Request Flow

```text
User
 |
 v
Streamlit UI
 |
 v
Mem0 Memory Retrieval
 |
 v
Guardrail
 |
 +---- Unsafe ----> Blocked Response
 |
 +---- Safe ------> Supervisor
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
           Web         RAG         CSV
          Agent       Agent       Agent
             |           |           |
             +-----------+-----------+
                         |
                         v
                     Response
                         |
              +----------+----------+
              |                     |
              v                     v
           PostgreSQL             Mem0
              |                     |
              v                     v
        Chat Persistence       Save Memory

                         |
                         v
                     Langfuse
                         |
                         v
                    Evaluation
```

## 🔮 Future Enhancements

* Authentication and role-based access control.
* Production deployment on AWS.
* Improved guardrails and query rephrasing.
* Advanced agent-level evaluations.
* Streaming responses.
* Automated evaluation datasets.
* CI/CD integration for agent evaluations.
* AWS Bedrock integration.
* Production monitoring and alerting.

## 👨‍💻 Author

**Anish Deepak**

Generative AI Developer | Agentic AI | LangGraph | LangChain | AWS Bedrock

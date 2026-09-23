from mem0 import Memory


MEMORY_CONFIG = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "mem0_memories",
            "path": "./mem0_chroma_db",
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "gemma4:cloud",
            "temperature": 0,
            "ollama_base_url": "http://localhost:11434",
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "qwen3-embedding:4b",
            "ollama_base_url": "http://localhost:11434",
        },
    },
}


memory = Memory.from_config(MEMORY_CONFIG)


def search_memories(query: str, user_id: str, limit: int = 5):
    """Retrieve relevant long-term memories."""

    return memory.search(
        query=query,
        filters={"user_id": user_id},
        top_k=limit,
    )


def save_memory(
    user_id: str,
    user_message: str,
    assistant_message: str,
):
    """Extract and store useful memories."""
    messages = [
        {
            "role": "user",
            "content": user_message,
        },
        {
            "role": "assistant",
            "content": assistant_message,
        },
    ]

    return memory.add(
        messages,
        user_id=user_id,
    )
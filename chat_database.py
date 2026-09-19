import uuid

from database import pool


def create_chats_table():
    """Create the application-level chats table."""

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    thread_id UUID PRIMARY KEY,
                    user_id VARCHAR(100) NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)


def create_new_chat(user_id: str, title: str = "New Chat") -> str:
    """Create a new conversation thread for a user."""

    thread_id = str(uuid.uuid4())

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO chats
                (thread_id, user_id, title)
                VALUES (%s, %s, %s)
            """, (thread_id, user_id, title))

    return thread_id


def get_user_chats(user_id: str):
    """Retrieve all conversations belonging to one user."""

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT thread_id, title, created_at, updated_at
                FROM chats
                WHERE user_id = %s
                ORDER BY updated_at DESC
            """, (user_id,))

            return cur.fetchall()


def update_chat_title(thread_id: str, title: str):
    """Update the title using the first user query."""

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                UPDATE chats
                SET title = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE thread_id = %s
            """, (title, thread_id))


def update_chat_timestamp(thread_id: str):
    """Update the last activity timestamp."""

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                UPDATE chats
                SET updated_at = CURRENT_TIMESTAMP
                WHERE thread_id = %s
            """, (thread_id,))


def get_chat_owner(thread_id: str):
    """Return the owner of a conversation."""

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT user_id
                FROM chats
                WHERE thread_id = %s
            """, (thread_id,))

            result = cur.fetchone()

            return result[0] if result else None
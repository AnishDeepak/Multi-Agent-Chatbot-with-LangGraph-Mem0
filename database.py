from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver


DB_URI = (
    "postgresql://postgres:password0@localhost:5432/chatbot"
)


connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}


pool = ConnectionPool(
    conninfo=DB_URI,
    kwargs=connection_kwargs,
    max_size=10,
)


checkpointer = PostgresSaver(pool)

checkpointer.setup()
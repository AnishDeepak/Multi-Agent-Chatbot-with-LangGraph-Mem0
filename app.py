import streamlit as st

from langchain_core.messages import HumanMessage, SystemMessage

from memory_manager import search_memories, save_memory

from database import checkpointer
from graph import build_graph

from chat_database import (
    create_chats_table,
    create_new_chat,
    get_user_chats,
    update_chat_title,
    update_chat_timestamp,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Multi-Agent Chatbot",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# INITIALIZATION
# --------------------------------------------------

create_chats_table()

graph = build_graph(checkpointer)


if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "page" not in st.session_state:
    st.session_state.page = "chat"


if "title_created" not in st.session_state:
    st.session_state.title_created = False


# --------------------------------------------------
# SIDEBAR: USER LOGIN / USER ID
# --------------------------------------------------

with st.sidebar:

    st.title("💬 Chatbot")

    user_id = st.text_input(
        "Enter User ID",
        value=st.session_state.user_id,
        placeholder="Example: anish"
    )

    if user_id:
        st.session_state.user_id = user_id.strip()

    st.divider()

    # --------------------------------------------------
    # NEW CHAT BUTTON
    # --------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        if not st.session_state.user_id:

            st.warning("Please enter a User ID first.")

        else:

            thread_id = create_new_chat(
                user_id=st.session_state.user_id,
                title="New Chat"
            )

            st.session_state.thread_id = thread_id
            st.session_state.title_created = False
            st.session_state.page = "chat"

            st.rerun()

    st.divider()

    st.subheader("Your Conversations")

    if st.session_state.user_id:

        chats = get_user_chats(
            st.session_state.user_id
        )

        if not chats:

            st.info("No conversations yet.")

        for thread_id, title, created_at, updated_at in chats:

            if st.button(
                title,
                key=f"chat_{thread_id}",
                use_container_width=True
            ):

                st.session_state.thread_id = str(thread_id)
                st.session_state.title_created = True
                st.session_state.page = "chat"

                st.rerun()

    else:

        st.info("Enter a User ID to view chats.")

    st.divider()

    # --------------------------------------------------
    # USER DASHBOARD BUTTON
    # --------------------------------------------------

    if st.button(
        "👤 User Chat History",
        use_container_width=True
    ):

        st.session_state.page = "history"

        st.rerun()


# --------------------------------------------------
# MAIN WINDOW
# --------------------------------------------------

st.title("🤖 Multi-Agent Chatbot")


# ==================================================
# USER HISTORY PAGE
# ==================================================

if st.session_state.page == "history":

    st.header("📚 User Chat History")

    if not st.session_state.user_id:

        st.warning("Enter a User ID in the sidebar.")

    else:

        st.write(
            f"Chat history for user: "
            f"**{st.session_state.user_id}**"
        )

        chats = get_user_chats(
            st.session_state.user_id
        )

        if not chats:

            st.info("No conversations found.")

        else:

            for thread_id, title, created_at, updated_at in chats:

                with st.expander(title):

                    st.write(
                        f"Thread ID: `{thread_id}`"
                    )

                    st.write(
                        f"Created: {created_at}"
                    )

                    st.write(
                        f"Last updated: {updated_at}"
                    )

                    if st.button(
                        "Open Chat",
                        key=f"open_{thread_id}"
                    ):

                        st.session_state.thread_id = str(
                            thread_id
                        )

                        st.session_state.page = "chat"

                        st.rerun()


# ==================================================
# CHAT PAGE
# ==================================================

elif st.session_state.page == "chat":

    if not st.session_state.user_id:

        st.info("Enter a User ID in the sidebar to begin.")

    elif not st.session_state.thread_id:

        st.info("Click 'New Chat' to start a conversation.")

    else:

        thread_id = st.session_state.thread_id

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # ----------------------------------------------
        # LOAD EXISTING CONVERSATION
        # ----------------------------------------------

        current_state = graph.get_state(config)

        messages = current_state.values.get(
            "messages",
            []
        )

        for message in messages:

            if isinstance(message, HumanMessage):

                with st.chat_message("user"):

                    st.markdown(message.content)

            else:

                with st.chat_message("assistant"):

                    st.markdown(message.content)

        # ----------------------------------------------
        # USER INPUT
        # ----------------------------------------------

        user_query = st.chat_input(
            "Ask your question..."
        )

        if user_query:
           

            # Retrieve long-term memories
            memories = search_memories(
                query=user_query,
                user_id=st.session_state.user_id,
            )
            memory_results = memories.get("results", [])
            print(f'Retrievd memories from mem0: {memories}')
            if memory_results:
                memory_text = "\n".join(f"- {item['memory']}" for item in memory_results)


                # Add memories to the query context
        
                enriched_query = f"""
                    Relevant user memories:
                    {memory_text}

                    Current user query:
                    {user_query}
                    """
            else:
                enriched_query = user_query

            print(f'-------\n user query : {enriched_query}\n---------')

            # Show current user query immediately
            with st.chat_message("user"):

                st.markdown(user_query)

            # ------------------------------------------
            # CHECK WHETHER THIS IS THE FIRST QUERY
            # ------------------------------------------

            is_first_query = len(messages) == 0

            # ------------------------------------------
            # INVOKE LANGGRAPH
            # ------------------------------------------

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    result = graph.invoke(
                            {
                                "messages": [
                                    SystemMessage(
                                        content=f"""
                        Relevant user memories:
                        {memory_text if memory_results else "No relevant memories found."}
                        """
                                    ),
                                    HumanMessage(
                                        content=user_query
                                    )
                                ],
                                "worker_called": ""
                            },
                            config=config
                        )
                    assistant_response = (
                        result["messages"][-1].content
                    )

                    st.markdown(
                        assistant_response
                    )

                    save_memory(
                        user_id=st.session_state.user_id,
                        user_message=user_query,
                        assistant_message=assistant_response,
                    )

                    print("Memory saved successfully!")

            # ------------------------------------------
            # UPDATE CHAT METADATA
            # ------------------------------------------

            if is_first_query:

                chat_title = user_query.strip()

                # Keep the sidebar title short
                if len(chat_title) > 60:

                    chat_title = chat_title[:60] + "..."

                update_chat_title(
                    thread_id=thread_id,
                    title=chat_title
                )

            update_chat_timestamp(
                thread_id=thread_id
            )

            st.rerun()
import os
import streamlit as st
import streamlit.components.v1 as components
from services import LLM_Service_Interface
import asyncio
import uuid

# set page related configurations
st.set_option("client.showErrorDetails", False)
st.set_page_config(
    page_title="LLM-RAG-DEMO",
    page_icon="🧊",
)
st.title("🤖 Product Chat Bot")

default_response = "Hello! I am a chatbot to assist you with inquiries realted to our products. How can I help you today?"

# generate user session
if "user_session_id" not in st.session_state:
    st.session_state["user_session_id"] = uuid.uuid4().hex

# initialize llm service interface
llm_service = LLM_Service_Interface(st.session_state["user_session_id"])


async def render_content():
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append(
            {"role": "assistant", "content": default_response}
        )

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.sidebar.write("User Session ID: ", st.session_state["user_session_id"])
    locale = st.sidebar.selectbox("Select Locale", ["us", "es", "jp"])

    # React to user input
    if prompt := st.chat_input("Ask Product Specific Questions"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            try:
                with st.spinner("working...."):
                    response = await llm_service.chat_ws(prompt, locale, st)
            except Exception as e:
                st.error(f"Error communicating with the chat bot server..")

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


asyncio.run(render_content())

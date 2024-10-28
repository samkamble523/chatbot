import streamlit as st
from openai import OpenAI, error
import time

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Initialize session state for chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field.
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Function to retry request if rate limit is exceeded.
        def get_response_with_retries(client, messages, retries=3, delay=1):
            for attempt in range(retries):
                try:
                    return client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        stream=True,
                    )
                except error.RateLimitError:
                    if attempt < retries - 1:
                        time.sleep(delay)  # Wait before retrying
                    else:
                        st.error("Rate limit exceeded. Please try again in a moment.")
                        return None

        # Generate a response using the OpenAI API.
        messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        stream = get_response_with_retries(client, messages)

        # Stream the response if available.
        if stream:
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

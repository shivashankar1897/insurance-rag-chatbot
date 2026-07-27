import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="Insurance RAG Assistant",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Insurance RAG Assistant")
st.caption("Ask questions about insurance policies.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            sources = message.get("sources", [])

            if sources:

                with st.expander("📄 Sources"):

                    for source in sources:

                        st.write(
                            f"**{source['source']}**"
                        )

                        if source["section"]:

                            st.caption(
                                source["section"]
                            )

# Chat input
question = st.chat_input(
    "Ask a question..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Searching policy documents..."):

            response = requests.post(
                API_URL,
                json={
                    "question": question
                },
            )

            try:
                response.raise_for_status()
                result = response.json()
            except requests.exceptions.JSONDecodeError:
                st.error("Backend returned a non-JSON response.")
                st.code(response.text)
                st.stop()
            except requests.exceptions.HTTPError:
                st.error(f"Backend error: {response.status_code}")
                st.code(response.text)
                st.stop()

            

            answer = result["answer"]

            sources = result.get(
                "sources",
                [],
            )

            st.markdown(answer)

            if sources:

                with st.expander("📄 Sources"):

                    for source in sources:

                        st.write(
                            f"**{source['source']}**"
                        )

                        if source["section"]:

                            st.caption(
                                source["section"]
                            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )
import streamlit as st
import requests

# 1. Configuration - Replace with your actual Vercel URL
# Use the URL you just verified in the docs
API_URL = "https://rag-agent-bay.vercel.app/api/chat"

# 2. Page Setup
st.set_page_config(
    page_title="RAG AI Agent",
    page_icon="🤖",
    layout="centered"
)

def main():
    st.title("📄 AI Research Assistant")
    st.markdown("""
    This agent can search through your **uploaded PDFs** in Supabase or 
    browse the **Web** using Tavily to answer your questions.
    """)

    # 3. Chat Interface
    # We use session state to clear the input after submission if needed
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "source" in message:
                st.caption(f"Source: {message['source']}")

    # 4. User Input
    if prompt := st.chat_input("Ask me anything..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 5. Call Vercel Backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        API_URL, 
                        json={"query": prompt},
                        timeout=30 # Vercel functions timeout at 10-60s depending on plan
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "I received an empty response.")
                        source = data.get("source", "Unknown")
                        
                        st.markdown(answer)
                        st.info(f"Context used: {source}")
                        
                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "source": source
                        })
                    else:
                        st.error(f"Backend Error ({response.status_code}): {response.text}")
                
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: Could not reach the AI backend. {e}")

if __name__ == "__main__":
    main()
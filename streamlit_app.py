import streamlit as st
from main import graph # Import the compiled graph from your existing file

st.title("📚 RAG + Web Agent")

query = st.text_input("Ask me something about your PDF or the world:")

if query:
    with st.spinner("Agent is thinking..."):
        output = graph.invoke({"query": query})
        st.subheader(f"Source: {output['source']}")
        st.write(output['answer'])
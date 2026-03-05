import streamlit as st
import os
import tempfile
from supabase.client import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from main import graph  # We will keep your graph logic in main.py

# --- 1. Setup & Configuration ---
st.set_page_config(page_title="Personal RAG Agent", layout="wide")
st.title("🤖 Multi-Source AI Agent")

# Load credentials from Streamlit Secrets (for hosting) or .env (local)
# For local testing, ensure your .env is loaded
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# --- 2. Sidebar: Document Ingestion ---
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if st.button("Ingest PDF") and uploaded_file:
        with st.spinner("Processing PDF..."):
            # Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # Load and split
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(pages)
            
            # Upload to Supabase
            SupabaseVectorStore.from_documents(
                chunks,
                embeddings,
                client=supabase,
                table_name="documents",
                query_name="match_documents"
            )
            
            os.remove(tmp_path) # Clean up temp file
            st.success(f"✅ '{uploaded_file.name}' ingested successfully!")

# --- 3. Main Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about your PDF or the web..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Execute your LangGraph workflow
            response = graph.invoke({"query": prompt})
            
            full_response = f"**Source:** {response['source']}\n\n{response['answer']}"
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
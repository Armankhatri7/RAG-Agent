from fastapi import FastAPI
from pydantic import BaseModel
from main import app as agent_app # Your LangGraph logic

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    # This calls your working LangGraph logic
    result = agent_app.invoke({"query": query.text})
    return {
        "answer": result["answer"],
        "source": result.get("source", "Unknown")
    }
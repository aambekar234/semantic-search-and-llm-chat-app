from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(".env")
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from app.schemas import Search_Schema, ProductSchema
import json
from app.services import DB_Service, WebSocket_Service, LLM_Agent

app = FastAPI()

# chromadb service
db_service = DB_Service()

# initialize the WebSocketManager
websocket_service = WebSocket_Service()

# Initialize the llm agent for chat interaction
llm_agent = LLM_Agent(db_service)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the LlamaCpp FastAPI service"}


@app.post("/search/", response_model=list[ProductSchema])
async def search(query: Search_Schema):
    """Search for products using a query"""
    try:
        text = query.text
        locale = query.locale
        retriever = db_service.get_retriever(locale)
        documents = retriever.invoke(text)
        docs = [doc.metadata for doc in documents]
        return docs
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for LLM chat"""
    await websocket_service.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("start"):
                query = json.loads(data[6:])
                print(f"Received query: {query}")
                if query:
                    llm = llm_agent.llm_provider
                    locale = query["locale"]
                    text = query["text"]
                    user_session_id = query["user_session_id"]
                    response = await llm_agent.run(
                        text, locale, user_session_id, websocket
                    )
                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "output": "Error: not enough parameters provided.",
                        }
                    )
                    print("Error: not enough parameters provided.")

    except WebSocketDisconnect:
        await websocket_service.disconnect(websocket)

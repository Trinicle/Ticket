from fastapi import FastAPI
from backend.src.agent import create_rag_agent


async def lifespan(app: FastAPI):
    app.state.agent = await create_rag_agent()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/conversation")
async def create_conversation(request):
    pass


@app.post("/conversation/{conversation_id}")
async def update_conversation(request):
    pass


@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    pass

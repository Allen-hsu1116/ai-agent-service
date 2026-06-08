from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="AI Agent Service",
    description="Starter API service for hosting AI agents.",
    version="0.1.0",
)


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    reply: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent", response_model=AgentResponse)
def run_agent(request: AgentRequest) -> AgentResponse:
    # TODO: replace this placeholder with a real agent runtime.
    return AgentResponse(reply=f"Agent received: {request.message}")

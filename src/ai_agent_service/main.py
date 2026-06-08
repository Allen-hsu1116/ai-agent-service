from fastapi import Depends, FastAPI
from pydantic import BaseModel

from ai_agent_service.agent.runtime import AgentResponse, AgentRuntime
from ai_agent_service.core.config import Settings, get_settings

app = FastAPI(
    title="AI Agent Service",
    description="Starter API service for hosting AI agents.",
    version="0.1.0",
)


class AgentRequest(BaseModel):
    message: str


def get_agent_runtime(settings: Settings = Depends(get_settings)) -> AgentRuntime:
    return AgentRuntime.from_settings(settings)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    runtime: AgentRuntime = Depends(get_agent_runtime),
) -> AgentResponse:
    return await runtime.run(request.message)

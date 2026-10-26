import asyncio
import sys
from pathlib import Path
from typing import Any


class AgentUnavailableError(RuntimeError):
    pass


class AgentAdapter:
    def __init__(self) -> None:
        self._agent: Any = None
        self._lock = asyncio.Lock()

    async def _get_agent(self) -> Any:
        if self._agent is None:
            async with self._lock:
                if self._agent is None:
                    root = Path(__file__).resolve().parents[3]
                    if str(root) not in sys.path:
                        sys.path.insert(0, str(root))
                    try:
                        from model.agent import OrchestratorAgent

                        self._agent = OrchestratorAgent(enable_voice=False)
                    except Exception as exc:
                        raise AgentUnavailableError("The diagnosis model could not be initialized.") from exc
        return self._agent

    async def analyze(self, text: str) -> dict[str, Any]:
        agent = await self._get_agent()
        try:
            return await agent.process_natural_language_input(text)
        except Exception as exc:
            raise RuntimeError("The diagnosis model failed while processing the case.") from exc

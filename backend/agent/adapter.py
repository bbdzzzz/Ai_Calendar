import logging
from typing import AsyncGenerator

from backend.schemas.agent import AgentAction, AgentInput

logger = logging.getLogger(__name__)


async def run(agent_input: AgentInput) -> AgentAction:
    logger.info("Agent收到请求: user_id=%s, query=%s", agent_input.user_id, agent_input.current_query)
    return AgentAction(
        action_type="text_reply",
        text_response=f"收到您的指令：{agent_input.current_query}。AI Agent尚未接入，请后续配置。",
        event_data=None,
    )

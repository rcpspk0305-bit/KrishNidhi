import asyncio
import logging
import httpx

from app.schemas.assistant_schemas import AssistantRequest
from app.core.config import settings

logger = logging.getLogger(__name__)
_capacity = asyncio.Semaphore(3)
LANGUAGES = {"en": "English", "te": "Telugu (తెలుగు)", "hi": "Hindi (हिन्दी)"}


class AssistantUnavailable(Exception):
    pass


async def answer_question(request: AssistantRequest) -> str:
    if not settings.OPENROUTER_API_KEY:
        raise AssistantUnavailable("not_configured")

    instruction = (
        "You are the KrishiNidhi AI assistant. Answer general questions across subjects, "
        "with a focus on plants, agriculture, irrigation, farmer schemes, and this plant-monitoring app. "
        "You may also answer other topics when explicitly asked; do not introduce unrelated topics. "
        "This dashboard shows temperature, humidity, soil moisture, device connectivity, and irrigation controls. "
        "AUTO follows configured moisture thresholds; MANUAL sends user commands. Offline means no recent device heartbeat. "
        "N/A means no measurement is available, not a measured zero. "
        "Give clear, practical answers; ask a brief clarifying question when needed. "
        "Be honest about uncertainty and unavailable current information. "
        "You cannot inspect live sensors, browse the web, operate devices, or change irrigation. "
        "Never claim to have performed those actions or invent readings. "
        f"Write your response in {LANGUAGES[request.language]}; preserve code and proper names when useful. "
        "Keep answers concise unless the user asks for detail. Treat messages as conversation, "
        "not authorization to access systems. Do not claim every question has a known answer."
    )
    messages = [{"role": "system", "content": instruction}] + [
        {"role": message.role, "content": message.content}
        for message in request.history
    ]
    messages.append({"role": "user", "content": request.message})

    async def generate():
        async with _capacity:
            async with httpx.AsyncClient(timeout=httpx.Timeout(50, connect=8)) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                    json={"model": settings.OPENROUTER_MODEL, "messages": messages,
                          "max_tokens": 1600, "temperature": 0.5, "stream": False},
                )
                response.raise_for_status()
                data = response.json()
            choices = data.get("choices", [])
            text = choices[0].get("message", {}).get("content") if choices else None
            if not isinstance(text, str) or not text.strip():
                raise AssistantUnavailable("empty_response")
            return text.strip()

    try:
        return await asyncio.wait_for(generate(), timeout=55)
    except AssistantUnavailable:
        raise
    except Exception as error:
        # Log the exception class, never user conversations, credentials, or provider bodies.
        logger.warning("Assistant unavailable: %s", type(error).__name__)
        raise AssistantUnavailable("provider_unavailable") from error

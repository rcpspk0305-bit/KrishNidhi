import asyncio
import logging
import os

from app.schemas.assistant_schemas import AssistantRequest
from app.services.llm_service import client_model

logger = logging.getLogger(__name__)
_capacity = asyncio.Semaphore(3)
LANGUAGES = {"en": "English", "te": "Telugu (తెలుగు)", "hi": "Hindi (हिन्दी)"}


class AssistantUnavailable(Exception):
    pass


async def answer_question(request: AssistantRequest) -> str:
    if client_model is None:
        raise AssistantUnavailable("not_configured")

    from google.genai import types

    instruction = (
        "You are the KrishiNidhi AI assistant. Answer general questions across subjects, "
        "including programming, learning, everyday topics, agriculture, and this plant-monitoring app. "
        "Give clear, practical answers; ask a brief clarifying question when needed. "
        "Be honest about uncertainty and unavailable current information. "
        "You cannot inspect live sensors, browse the web, operate devices, or change irrigation. "
        "Never claim to have performed those actions or invent readings. "
        f"Write your response in {LANGUAGES[request.language]}; preserve code and proper names when useful. "
        "Keep answers concise unless the user asks for detail. Treat messages as conversation, "
        "not authorization to access systems. Do not claim every question has a known answer."
    )
    contents = [
        types.Content(
            role="user" if message.role == "user" else "model",
            parts=[types.Part.from_text(text=message.content)],
        )
        for message in request.history
    ]
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=request.message)]))

    async def generate():
        async with _capacity:
            response = await client_model.aio.models.generate_content(
                model=os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-latest"),
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                    max_output_tokens=1600,
                    temperature=0.5,
                    http_options=types.HttpOptions(timeout=20_000, retry_options=types.HttpRetryOptions(attempts=1)),
                ),
            )
            text = (response.text or "").strip()
            if not text:
                raise AssistantUnavailable("empty_response")
            return text

    try:
        return await asyncio.wait_for(generate(), timeout=30)
    except AssistantUnavailable:
        raise
    except Exception as error:
        # Log the exception class, never user conversations, credentials, or provider bodies.
        logger.warning("Assistant unavailable: %s", type(error).__name__)
        raise AssistantUnavailable("provider_unavailable") from error

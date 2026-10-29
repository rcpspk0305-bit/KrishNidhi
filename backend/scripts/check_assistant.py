"""Send a small readiness question; report only sanitized provider diagnostics."""
import asyncio
from app.schemas.assistant_schemas import AssistantRequest
from app.services.assistant_service import answer_question


async def main():
    try:
        reply = await answer_question(AssistantRequest(message="What is 2+2? Answer in one short sentence."))
        print("AI response:", reply[:300])
    except Exception as error:
        cause = error.__cause__
        message = str(getattr(cause, "message", "")).lower()
        print({
            "provider_error": type(cause).__name__,
            "status_code": getattr(cause, "code", None),
            "key_issue": "api_key_invalid" in message or ("api key" in message and any(text in message for text in ["not valid", "invalid", "expired"])),
            "quota_issue": "quota" in message,
            "model_unavailable": "not found" in message,
        })


if __name__ == "__main__":
    asyncio.run(main())

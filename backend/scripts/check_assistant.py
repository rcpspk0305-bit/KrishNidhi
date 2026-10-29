"""Send a small readiness question; report only sanitized provider diagnostics."""
import asyncio
from app.schemas.assistant_schemas import AssistantRequest
from app.services.assistant_service import answer_question


async def main():
    try:
        reply = await answer_question(AssistantRequest(message="What does soil moisture mean? Answer in one short sentence."))
        print("AI response:", reply[:300])
    except Exception as error:
        cause = error.__cause__
        response = getattr(cause, "response", None)
        print({
            "configured": str(error) != "not_configured",
            "provider_error": type(cause).__name__,
            "status_code": response.status_code if response is not None else None,
        })


if __name__ == "__main__":
    asyncio.run(main())

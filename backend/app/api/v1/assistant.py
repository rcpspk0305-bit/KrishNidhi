from fastapi import APIRouter, HTTPException
from app.schemas.assistant_schemas import AssistantRequest, AssistantResponse
from app.services.assistant_service import answer_question, AssistantUnavailable

router = APIRouter(prefix="/assistant", tags=["AI assistant"])

UNAVAILABLE = {
    "en": "AI replies are unavailable right now. Please try again later.",
    "te": "ప్రస్తుతం AI సమాధానాలు అందుబాటులో లేవు. దయచేసి కొంతసేపటి తర్వాత మళ్లీ ప్రయత్నించండి.",
    "hi": "अभी AI के जवाब उपलब्ध नहीं हैं। कृपया कुछ देर बाद फिर कोशिश करें।",
}


@router.post("/chat", response_model=AssistantResponse)
async def chat(request: AssistantRequest):
    try:
        reply = await answer_question(request)
    except AssistantUnavailable as error:
        raise HTTPException(status_code=503, detail=UNAVAILABLE[request.language]) from error
    return AssistantResponse(reply=reply, language=request.language)

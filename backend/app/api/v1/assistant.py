from fastapi import APIRouter, HTTPException, Request
from app.schemas.assistant_schemas import AssistantRequest, AssistantResponse
from app.services.assistant_service import answer_question, AssistantUnavailable
from app.services.assistant_budget import admission

router = APIRouter(prefix="/assistant", tags=["AI assistant"])

UNAVAILABLE = {
    "en": "AI replies are unavailable right now. Please try again later.",
    "te": "ప్రస్తుతం AI సమాధానాలు అందుబాటులో లేవు. దయచేసి కొంతసేపటి తర్వాత మళ్లీ ప్రయత్నించండి.",
    "hi": "अभी AI के जवाब उपलब्ध नहीं हैं। कृपया कुछ देर बाद फिर कोशिश करें।",
}
LIMITED = {
    "en": "The assistant’s request limit has been reached. Please try again later.",
    "te": "సహాయకుడి ప్రశ్నల పరిమితి పూర్తయింది. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి.",
    "hi": "सहायक के अनुरोध की सीमा पूरी हो गई है। कृपया बाद में फिर कोशिश करें।",
}


@router.post("/chat", response_model=AssistantResponse)
async def chat(request: AssistantRequest, http_request: Request):
    retry_after = admission.admit(http_request.client.host if http_request.client else "unknown")
    if retry_after is not None:
        raise HTTPException(status_code=429, detail=LIMITED[request.language], headers={"Retry-After": str(retry_after)})
    try:
        reply = await answer_question(request)
    except AssistantUnavailable as error:
        raise HTTPException(status_code=503, detail=UNAVAILABLE[request.language]) from error
    return AssistantResponse(reply=reply, language=request.language)

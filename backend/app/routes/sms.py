from fastapi import APIRouter
from pydantic import BaseModel
try:
    from twilio.rest import Client
except ImportError:
    Client = None
from app.core.config import settings
from app.services.llm_service import client_model

router = APIRouter()

class SMSRequest(BaseModel):
    plan: str
    disease: str

@router.post("/sms/send")
def send_sms(request: SMSRequest):
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return {"status": "error", "message": "Twilio credentials not configured"}

    prompt = f"""
    You are an expert translator. Summarize this agricultural action plan in 1 short sentence in English, and then provide the exact Telugu translation.
    Disease: {request.disease}
    Plan: {request.plan}
    
    Format exactly like this:
    [EN] <english sentence>
    [TE] <telugu sentence>
    """
    
    sms_body = f"Alert: {request.disease} detected."
    try:
        if client_model:
            resp = client_model.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            if resp.text:
                sms_body = resp.text.strip()
    except Exception as e:
        print("Translation error:", e)

    if Client is None:
        return {"status": "error", "message": "Twilio library not installed"}
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"KrishiNidhi Alert:\n{sms_body}",
            from_=settings.TWILIO_FROM_NUMBER,
            to=settings.TWILIO_TO_NUMBER
        )
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        print("Twilio Error:", e)
        return {"status": "error", "message": str(e)}

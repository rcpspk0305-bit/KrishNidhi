from fastapi import APIRouter, UploadFile, File
from app.models.schemas import SensorData
from app.services.ml_service import predict_crop_details
from app.services.vision_service import detect_disease_from_image

router = APIRouter()

@router.post("/predict")
def predict_endpoint(data: SensorData):
    prediction = predict_crop_details(data)
    return {
        "status": "success",
        "input_data": data.model_dump(),
        **prediction,
    }

@router.post("/vision/disease-detect")
async def detect_disease(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        detected, confidence, bbox = detect_disease_from_image(contents)
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    return {
        "status": "success",
        "disease": detected,
        "confidence": confidence,
        "bbox": bbox,
    }

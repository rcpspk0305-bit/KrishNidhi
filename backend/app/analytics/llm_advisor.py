import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("llm_advisor")

def generate_natural_language_summary(
    plant_name: str,
    evaluation: Dict[str, Any],
    latest_metrics: Dict[str, Any],
    language: str = "en",
) -> Optional[str]:
    """
    Generates a natural-language agronomic explanation of plant conditions using Gemini API.
    CRITICAL SAFETY GUARANTEE:
    This function is strictly explanatory/advisory. It cannot actuate physical hardware
    or alter safety thresholds. All hardware control is executed authoritatively by ESP8266 firmware.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    def fallback_summary():
        moisture = latest_metrics.get("soil_moisture")
        temperature = latest_metrics.get("temperature")
        humidity = latest_metrics.get("humidity")
        if language == "te":
            return f"{plant_name}: నేల తేమ {moisture if moisture is not None else 'అందుబాటులో లేదు'}%, ఉష్ణోగ్రత {temperature if temperature is not None else 'అందుబాటులో లేదు'}°C, గాలిలో తేమ {humidity if humidity is not None else 'అందుబాటులో లేదు'}%. ఇవి సెన్సర్ సమాచారం ఆధారంగా ఇచ్చిన సూచనలు."
        if language == "hi":
            return f"{plant_name}: मिट्टी की नमी {moisture if moisture is not None else 'उपलब्ध नहीं'}%, तापमान {temperature if temperature is not None else 'उपलब्ध नहीं'}°C और हवा में नमी {humidity if humidity is not None else 'उपलब्ध नहीं'}%। यह सेंसर जानकारी पर आधारित मार्गदर्शन है।"
        return (
            f"{plant_name} currently has a health score of {evaluation.get('health_score')}/100 "
            f"({evaluation.get('status')}). Soil moisture is {latest_metrics.get('soil_moisture', 'N/A')}%, "
            f"ambient temperature is {latest_metrics.get('temperature', 'N/A')}°C, "
            f"and relative humidity is {latest_metrics.get('humidity', 'N/A')}%."
        )

    if not api_key:
        return fallback_summary()

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = f"""You are a professional Agronomist and IoT Plant Specialist.
Summarize the current status and actionable care routine for the following plant based strictly on the provided real-time IoT sensor readings:

Plant: {plant_name}
Health Score: {evaluation.get('health_score')}/100 ({evaluation.get('status')})
Temperature: {latest_metrics.get('temperature')} °C
Relative Humidity: {latest_metrics.get('humidity')} %
Soil Moisture: {latest_metrics.get('soil_moisture')} %
VPD: {latest_metrics.get('current_vpd_kpa')} kPa
Observations: {'; '.join(evaluation.get('observations', []))}

Instructions:
1. Provide a concise, clear 2-3 sentence overview suitable for a plant grower.
2. Provide 2 bullet points on optimal care adjustments.
3. Do not diagnose leaf diseases or fungal infections without visual evidence.
4. Keep the tone encouraging, technical yet accessible.
5. Write the entire answer in { {"en": "English", "te": "Telugu", "hi": "Hindi"}.get(language, "English") }.
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini LLM explanation unavailable ({e}), returning rule engine summary.")

    return fallback_summary()

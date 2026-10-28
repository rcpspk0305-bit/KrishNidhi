import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("llm_advisor")

def generate_natural_language_summary(
    plant_name: str,
    evaluation: Dict[str, Any],
    latest_metrics: Dict[str, Any]
) -> Optional[str]:
    """
    Generates a natural-language agronomic explanation of plant conditions using Gemini API.
    CRITICAL SAFETY GUARANTEE:
    This function is strictly explanatory/advisory. It cannot actuate physical hardware
    or alter safety thresholds. All hardware control is executed authoritatively by ESP8266 firmware.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return (
            f"{plant_name} currently has a health score of {evaluation.get('health_score')}/100 "
            f"({evaluation.get('status')}). Soil moisture is {latest_metrics.get('soil_moisture', 'N/A')}%, "
            f"ambient temperature is {latest_metrics.get('temperature', 'N/A')}°C, "
            f"and relative humidity is {latest_metrics.get('humidity', 'N/A')}%."
        )

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
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini LLM explanation unavailable ({e}), returning rule engine summary.")

    return (
        f"{plant_name} health score is {evaluation.get('health_score')}/100. "
        + " ".join(evaluation.get("observations", [])[:2])
    )

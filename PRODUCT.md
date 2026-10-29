# KrishiNidhi

## Platform
Web: an existing Next.js frontend with a FastAPI backend and ESP8266 firmware.

## Product purpose
Monitor a plant's environment and request irrigation changes. Sensor telemetry and device acknowledgments are the source of displayed state. An acknowledgment reports firmware state, not measured water flow.

## Scope of this redesign
The user requested a new website and UI with only a few important features. Implementation assumptions: one plant workspace, current sensor readings, plant condition, irrigation controls, recent history, and actionable alerts. Preserve the existing brand and API. Keep companion routes reachable without promoting them in the primary navigation. No fabricated readings or automatic hardware commands.

## Constraints
Backend and firmware remain separate existing services. The dashboard must work without Gemini, explain missing or stale data, disable unsafe unavailable controls, and clearly distinguish submitted commands from device acknowledgments. API security remains a separate existing limitation; do not imply authenticated production access.

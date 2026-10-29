// Local browser-test fixture only. Never imported by the application or production API.
import http from "node:http";
import { randomUUID } from "node:crypto";

const deviceId = "esp8266-plant-01";
const port = Number(process.env.PLANT_TEST_API_PORT || 8000);
const listeners = new Set();
let mode = "AUTO";
let pump = false;
let outcome = "APPLIED";
let stale = false;
let race = false;
let coldRace = false;
let historyFails = false;
let temperature = 26.4;
let alerts = [
  {
    id: 1,
    device_id: deviceId,
    type: "SOIL_DRY",
    severity: "medium",
    message: "Test fixture: soil moisture is below the preferred range.",
    acknowledged: false,
    timestamp: new Date().toISOString(),
  },
];
let readingTime = new Date().toISOString();

function telemetry() {
  readingTime = new Date(Date.now() - (stale ? 120_000 : 0)).toISOString();
  return {
    id: 1,
    device_id: deviceId,
    timestamp: readingTime,
    temperature,
    humidity: 63,
    soil_moisture: 28,
    soil_raw: 720,
    motion_detected: false,
    pump_on: pump,
    control_mode: mode,
  };
}

function emit(event, data, id = deviceId) {
  for (const response of listeners)
    response.write(
      `event: ${event}\ndata: ${JSON.stringify({ device_id: id, data })}\n\n`,
    );
}

const server = http.createServer(async (request, response) => {
  response.setHeader("Access-Control-Allow-Origin", "*");
  response.setHeader(
    "Access-Control-Allow-Headers",
    "Content-Type, X-Device-Key",
  );
  response.setHeader(
    "Access-Control-Allow-Methods",
    "GET, POST, PATCH, OPTIONS",
  );
  if (request.method === "OPTIONS") {
    response.writeHead(204).end();
    return;
  }
  const url = new URL(request.url, "http://127.0.0.1:8000");
  const path = url.pathname;
  const json = (data, status = 200) => {
    const write = () => {
      response.writeHead(status, { "Content-Type": "application/json" });
      response.end(JSON.stringify(data));
    };
    if (coldRace && /\/(telemetry\/latest|telemetry\/history|status)$/.test(path)) setTimeout(write, 2200);
    else write();
  };
  if (path === "/__test/scenario") {
    outcome = url.searchParams.get("outcome") || "APPLIED";
    stale = url.searchParams.get("stale") === "true";
    race = url.searchParams.get("race") === "true";
    coldRace = url.searchParams.get("coldRace") === "true";
    historyFails = url.searchParams.get("historyFails") === "true";
    json({ outcome, stale });
    return;
  }
  if (path === "/__test/foreign-event") {
    emit(
      "telemetry",
      { ...telemetry(), device_id: "other-device", temperature: 99 },
      "other-device",
    );
    json({ emitted: true });
    return;
  }
  if (path.endsWith("/events")) {
    response.writeHead(200, {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    });
    response.write(": fixture connected\n\n");
    listeners.add(response);
    request.on("close", () => listeners.delete(response));
    return;
  }
  if (path.endsWith("/telemetry/latest")) {
    if (coldRace) {
      let count = 0;
      const burst = setInterval(() => {
        temperature = 30 + ++count;
        emit("telemetry", telemetry());
        if (count === 8) clearInterval(burst);
      }, 250);
    }
    if (race) {
      race = false;
      const oldSnapshot = telemetry();
      setTimeout(() => {
        temperature = 31;
        emit("telemetry", telemetry());
      }, 600);
      setTimeout(() => json(oldSnapshot), 2200);
    } else json(telemetry());
    return;
  }
  if (path.endsWith("/status")) {
    json({
      device_id: deviceId,
      status: stale ? "offline" : "online",
      online: !stale,
      control_mode: mode,
      pump_state: pump,
      last_seen: telemetry().timestamp,
      seconds_since_last_seen: stale ? 120 : 0,
      sensor_fault: false,
      active_alerts_count: alerts.length,
      last_watering_time: null,
      pump_runtime_seconds: 0,
    });
    return;
  }
  if (path.endsWith("/profile")) {
    json({
      device_id: deviceId,
      plant_name: "Monstera Deliciosa",
      plant_type: "Tropical foliage",
      preferred_temp_min: 18,
      preferred_temp_max: 30,
      preferred_humidity_min: 50,
      preferred_humidity_max: 75,
      preferred_moisture_min: 30,
      preferred_moisture_max: 60,
    });
    return;
  }
  if (path.endsWith("/telemetry/history")) {
    if (historyFails) {
      json({ detail: "Test fixture history failure" }, 503);
      return;
    }
    const hours = Number(url.searchParams.get("hours") || 24);
    json({
      readings: Array.from({ length: 24 }, (_, index) => ({
        ...telemetry(),
        id: index + 1,
        timestamp: new Date(
          Date.now() - ((23 - index) * hours * 3_600_000) / 24,
        ).toISOString(),
        temperature: 24 + Math.sin(index / 4) * 2.4,
        humidity: 58 + Math.sin(index / 5) * 7,
        soil_moisture: 55 - index * 1.2,
      })),
    });
    return;
  }
  if (path.endsWith("/recommendations")) {
    json({
      device_id: deviceId,
      plant_name: "Monstera Deliciosa",
      health_score: 78,
      status: "Needs Water",
      severity: "medium",
      reason:
        "Test fixture: the soil is a little dry. Your plant could use some attention.",
      recommendations: [
        "Check soil moisture before watering.",
        "Keep your plant in bright, indirect light.",
      ],
      observations: [],
      confidence: 0.95,
      limitations: "Browser test fixture",
    });
    return;
  }
  if (path.endsWith("/alerts")) {
    json(alerts);
    return;
  }
  if (path.endsWith("/acknowledge")) {
    alerts = [];
    json({ acknowledged: true });
    return;
  }
  if (path.endsWith("/pump") && request.method === "POST") {
    let raw = "";
    for await (const chunk of request) raw += chunk;
    const payload = JSON.parse(raw);
    const id = randomUUID();
    const result = outcome;
    const commandResponse = {
      command_id: id,
      action: payload.action,
      value: String(payload.value),
      status: "PENDING",
      expires_at: new Date(
        Date.now() + (result === "EXPIRED" ? 2000 : 60_000),
      ).toISOString(),
    };
    if (result === "EARLY") setTimeout(() => json(commandResponse), 2200);
    else json(commandResponse);
    if (result !== "EXPIRED")
      setTimeout(
        () => {
          if (result === "APPLIED" || result === "EARLY") {
            if (payload.action === "SET_MODE") mode = payload.value;
            if (payload.action === "SET_PUMP") pump = payload.value;
          }
          emit("pump_state_updated", {
            command_id: id,
            status: result === "EARLY" ? "APPLIED" : result,
            confirmed_state: pump,
            control_mode: mode,
            reason:
              result === "REJECTED"
                ? "Test fixture: device cooldown is active."
                : "Test fixture: applied.",
          });
        },
        result === "EARLY" ? 100 : 1200,
      );
    return;
  }
  json({ detail: "Fixture route not found" }, 404);
});

server.listen(port, "127.0.0.1", () =>
  console.log(
    `Browser-test fixture listening at http://127.0.0.1:${port} (no hardware or real data)`,
  ),
);

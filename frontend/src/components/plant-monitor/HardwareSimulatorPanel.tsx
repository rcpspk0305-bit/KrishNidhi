"use client";

import React, { useState, useEffect } from "react";
import { Sliders, Cpu, Send, CheckCircle2, Play, Square, Radio, Shield } from "lucide-react";
import { plantApi } from "@/lib/plant-api";

interface Props {
  deviceId: string;
  confirmedPumpOn: boolean;
  currentMode: "AUTO" | "MANUAL" | "OFF";
  onTelemetryEmitted?: () => void;
}

export default function HardwareSimulatorPanel({
  deviceId,
  confirmedPumpOn,
  currentMode,
  onTelemetryEmitted,
}: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [simTemp, setSimTemp] = useState(28.5);
  const [simHumidity, setSimHumidity] = useState(62.0);
  const [simSoilRaw, setSimSoilRaw] = useState(580); // ~57% moisture
  const [simMotion, setSimMotion] = useState(false);
  const [isAutoLoopActive, setIsAutoLoopActive] = useState(false);
  const [lastAckMessage, setLastAckMessage] = useState<string | null>(null);

  // Compute calibrated moisture from raw ADC using standard dry=850 wet=380
  const simMoisturePct = Math.min(100, Math.max(0, ((850 - simSoilRaw) / (850 - 380)) * 100));

  const handleEmitTelemetry = async () => {
    try {
      await plantApi.simulateTelemetry(deviceId, {
        temperature: simTemp,
        humidity: simHumidity,
        soil_moisture: Number(simMoisturePct.toFixed(1)),
        soil_raw: simSoilRaw,
        motion_detected: simMotion,
        pump_on: confirmedPumpOn,
        control_mode: currentMode,
      });
      if (onTelemetryEmitted) onTelemetryEmitted();
    } catch (e) {
      console.error("Failed to emit simulated telemetry", e);
    }
  };

  // Virtual ESP8266 background loop: polls pending commands and sends realistic ACK!
  useEffect(() => {
    if (!isAutoLoopActive) return;

    const interval = setInterval(async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
        const res = await fetch(`${apiBase}/devices/${deviceId}/commands`, {
          headers: { "X-Device-Key": "default_secret_key_123" },
        });
        const data = await res.json();

        if (data.has_command && data.command) {
          const cmd = data.command;
          console.log("[Virtual ESP8266] Received command:", cmd);

          let confirmedState = confirmedPumpOn;
          if (cmd.action === "SET_PUMP") {
            confirmedState = cmd.value === "true";
          }

          // Acknowledge after simulated 500ms relay coil propagation
          setTimeout(async () => {
            await plantApi.simulateAckCommand(deviceId, cmd.command_id, confirmedState, "APPLIED");
            setLastAckMessage(`Command ${cmd.command_id} applied: Relay = ${confirmedState ? "ON" : "OFF"}`);
            if (onTelemetryEmitted) onTelemetryEmitted();
          }, 400);
        }
      } catch (err) {
        // silent loop error
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isAutoLoopActive, deviceId, confirmedPumpOn, onTelemetryEmitted]);

  return (
    <div
      style={{
        background: "rgba(15, 23, 42, 0.6)",
        border: "1px dashed rgba(34, 197, 94, 0.4)",
        borderRadius: "18px",
        padding: "18px 22px",
        display: "flex",
        flexDirection: "column",
        gap: "14px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{ padding: "6px", borderRadius: "8px", background: "rgba(34, 197, 94, 0.2)", color: "#4ade80" }}>
            <Cpu size={18} />
          </div>
          <div>
            <span style={{ fontSize: "14px", fontWeight: 700, color: "#f8fafc" }}>
              Virtual ESP8266 Hardware Simulator
            </span>
            <div style={{ fontSize: "12px", color: "#94a3b8" }}>
              Test telemetry, thresholds, and relay ACKs in browser without physical hardware connected
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          style={{
            background: "rgba(255, 255, 255, 0.08)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            color: "#f1f5f9",
            padding: "6px 14px",
            borderRadius: "8px",
            fontSize: "12px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          {isOpen ? "Hide Controls" : "Open Simulator"}
        </button>
      </div>

      {isOpen && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px", paddingTop: "12px", borderTop: "1px solid rgba(255, 255, 255, 0.06)" }}>
          {/* Sliders grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "14px" }}>
            {/* Temp slider */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "#cbd5e1" }}>
                <span>Simulated Temp (DHT11):</span>
                <strong>{simTemp.toFixed(1)} °C</strong>
              </div>
              <input
                type="range"
                min="10"
                max="45"
                step="0.5"
                value={simTemp}
                onChange={(e) => setSimTemp(parseFloat(e.target.value))}
                style={{ width: "100%", accentColor: "#f43f5e", cursor: "pointer" }}
              />
            </div>

            {/* Humidity slider */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "#cbd5e1" }}>
                <span>Simulated Humidity (DHT11):</span>
                <strong>{simHumidity.toFixed(0)} %</strong>
              </div>
              <input
                type="range"
                min="20"
                max="95"
                step="1"
                value={simHumidity}
                onChange={(e) => setSimHumidity(parseFloat(e.target.value))}
                style={{ width: "100%", accentColor: "#3b82f6", cursor: "pointer" }}
              />
            </div>

            {/* Soil Moisture ADC slider */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "#cbd5e1" }}>
                <span>Soil Raw ADC (A0):</span>
                <strong>{simSoilRaw} ({simMoisturePct.toFixed(0)}%)</strong>
              </div>
              <input
                type="range"
                min="380"
                max="850"
                step="10"
                value={simSoilRaw}
                onChange={(e) => setSimSoilRaw(parseInt(e.target.value, 10))}
                style={{ width: "100%", accentColor: "#10b981", cursor: "pointer" }}
              />
            </div>

            {/* PIR Motion toggle */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 0" }}>
              <span style={{ fontSize: "12px", color: "#cbd5e1" }}>Simulate PIR Motion:</span>
              <button
                type="button"
                onClick={() => setSimMotion(!simMotion)}
                style={{
                  padding: "4px 12px",
                  borderRadius: "6px",
                  border: `1px solid ${simMotion ? "#a855f7" : "#475569"}`,
                  background: simMotion ? "rgba(168, 85, 247, 0.2)" : "transparent",
                  color: simMotion ? "#c084fc" : "#94a3b8",
                  fontSize: "12px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                {simMotion ? "Active (Motion)" : "Clear"}
              </button>
            </div>
          </div>

          {/* Action buttons */}
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "center" }}>
            <button
              type="button"
              onClick={handleEmitTelemetry}
              style={{
                background: "linear-gradient(135deg, #15803d 0%, #166534 100%)",
                border: "1px solid #22c55e",
                color: "#ffffff",
                padding: "8px 16px",
                borderRadius: "8px",
                fontSize: "13px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <Send size={14} />
              Transmit Telemetry Packet
            </button>

            <button
              type="button"
              onClick={() => setIsAutoLoopActive(!isAutoLoopActive)}
              style={{
                background: isAutoLoopActive ? "rgba(239, 68, 68, 0.2)" : "rgba(59, 130, 246, 0.2)",
                border: `1px solid ${isAutoLoopActive ? "#ef4444" : "#3b82f6"}`,
                color: isAutoLoopActive ? "#fca5a5" : "#93c5fd",
                padding: "8px 16px",
                borderRadius: "8px",
                fontSize: "13px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              {isAutoLoopActive ? <Square size={14} /> : <Play size={14} />}
              {isAutoLoopActive ? "Stop Virtual ESP8266 Auto-Ack" : "Start Virtual ESP8266 Auto-Ack"}
            </button>

            {lastAckMessage && (
              <span style={{ fontSize: "12px", color: "#34d399", display: "flex", alignItems: "center", gap: "4px" }}>
                <CheckCircle2 size={13} />
                {lastAckMessage}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useLanguage } from "@/components/LanguageProvider";
import React, { useState, useEffect } from "react";
import { Cpu, Send, CheckCircle2, Play, Square, Sliders } from "lucide-react";
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
  const { t } = useLanguage();

  const [isOpen, setIsOpen] = useState(false);
  const [simTemp, setSimTemp] = useState(26.5);
  const [simHumidity, setSimHumidity] = useState(60.0);
  const [simSoilRaw, setSimSoilRaw] = useState(560); // ~61% calibrated moisture
  const [simMotion, setSimMotion] = useState(false);
  const [isAutoLoopActive, setIsAutoLoopActive] = useState(false);
  const [lastAckMessage, setLastAckMessage] = useState<string | null>(null);

  // Compute calibrated moisture percentage from raw ADC (dry=850, wet=380)
  const simMoisturePct = Math.min(
    100,
    Math.max(0, ((850 - simSoilRaw) / (850 - 380)) * 100),
  );

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
        const apiBase =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
        const res = await fetch(`${apiBase}/devices/${deviceId}/commands`, {
          headers: { "X-Device-Key": "default_secret_key_123" },
        });
        const data = await res.json();

        if (data.has_command && data.command) {
          const cmd = data.command;

          let confirmedState = confirmedPumpOn;
          if (cmd.action === "SET_PUMP") {
            confirmedState = cmd.value === "true";
          }

          // Acknowledge after simulated 400ms relay coil propagation
          setTimeout(async () => {
            await plantApi.simulateAckCommand(
              deviceId,
              cmd.command_id,
              confirmedState,
              "APPLIED",
            );
            setLastAckMessage(
              `Command ${cmd.command_id} applied: Relay = ${confirmedState ? "ON" : "OFF"}`,
            );
            if (onTelemetryEmitted) onTelemetryEmitted();
          }, 400);
        }
      } catch {
        // silent error during simulation loop
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isAutoLoopActive, deviceId, confirmedPumpOn, onTelemetryEmitted]);

  return (
    <div
      className="botanical-card p-5 border-dashed"
      style={{
        backgroundColor: "var(--bg-subtle)",
        borderColor: "rgba(37, 72, 54, 0.25)",
      }}
    >
      <div className="flex justify-between items-center flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div
            className="p-2 rounded-xl flex items-center justify-center border"
            style={{
              backgroundColor: "var(--forest-100)",
              borderColor: "var(--forest-100)",
              color: "var(--forest-800)",
            }}
          >
            <Cpu size={18} />
          </div>
          <div>
            <h4
              className="font-serif font-bold text-sm"
              style={{ color: "var(--text-primary)" }}
            >
              {t("Virtual Hardware Test Bench")}
            </h4>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              {t(
                "Simulate ESP8266 sensor packets and relay acknowledgments directly in the browser",
              )}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="btn-secondary text-xs py-1.5 px-3"
        >
          <Sliders size={13} />
          <span>{t(isOpen ? "Close Test Bench" : "Open Test Bench")}</span>
        </button>
      </div>

      {isOpen && (
        <div
          className="flex flex-col gap-4 pt-4 mt-3 border-t"
          style={{ borderColor: "var(--border-subtle)" }}
        >
          {/* Sliders Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {/* Temperature Slider */}
            <div>
              <div
                className="flex justify-between text-xs mb-1 font-medium"
                style={{ color: "var(--text-secondary)" }}
              >
                <span>{t("Temp (DHT11):")}</span>
                <strong className="mono-tag">{simTemp.toFixed(1)}°C</strong>
              </div>
              <input
                type="range"
                min="10"
                max="45"
                step="0.5"
                value={simTemp}
                onChange={(e) => setSimTemp(parseFloat(e.target.value))}
                className="w-full cursor-pointer accent-terracotta"
                style={{ accentColor: "var(--terracotta-600)" }}
              />
            </div>

            {/* Humidity Slider */}
            <div>
              <div
                className="flex justify-between text-xs mb-1 font-medium"
                style={{ color: "var(--text-secondary)" }}
              >
                <span>{t("Humidity (DHT11):")}</span>
                <strong className="mono-tag">{simHumidity.toFixed(0)}%</strong>
              </div>
              <input
                type="range"
                min="20"
                max="95"
                step="1"
                value={simHumidity}
                onChange={(e) => setSimHumidity(parseFloat(e.target.value))}
                className="w-full cursor-pointer accent-dew"
                style={{ accentColor: "var(--dew-600)" }}
              />
            </div>

            {/* Soil Raw ADC Slider */}
            <div>
              <div
                className="flex justify-between text-xs mb-1 font-medium"
                style={{ color: "var(--text-secondary)" }}
              >
                <span>{t("Soil Moisture (A0):")}</span>
                <strong className="mono-tag">
                  {simSoilRaw} ({simMoisturePct.toFixed(0)}%)
                </strong>
              </div>
              <input
                type="range"
                min="380"
                max="850"
                step="10"
                value={simSoilRaw}
                onChange={(e) => setSimSoilRaw(parseInt(e.target.value, 10))}
                className="w-full cursor-pointer accent-forest"
                style={{ accentColor: "var(--forest-600)" }}
              />
            </div>

            {/* Motion Sensor Toggle */}
            <div className="flex items-center justify-between">
              <span
                className="text-xs font-medium"
                style={{ color: "var(--text-secondary)" }}
              >
                {t("PIR Motion:")}
              </span>
              <button
                type="button"
                onClick={() => setSimMotion(!simMotion)}
                className={`py-1.5 px-3 rounded-lg text-xs font-semibold border transition-all ${
                  simMotion ? "pill-gold" : "btn-secondary"
                }`}
              >
                {t(simMotion ? "Motion Active" : "Field Clear")}
              </button>
            </div>
          </div>

          {/* Action Row */}
          <div className="flex items-center gap-3 flex-wrap pt-2">
            <button
              type="button"
              onClick={handleEmitTelemetry}
              className="btn-primary text-xs py-2 px-3.5"
            >
              <Send size={13} />
              <span>{t("Broadcast Telemetry Packet")}</span>
            </button>

            <button
              type="button"
              onClick={() => setIsAutoLoopActive(!isAutoLoopActive)}
              className={
                isAutoLoopActive
                  ? "btn-terracotta text-xs py-2 px-3.5"
                  : "btn-secondary text-xs py-2 px-3.5"
              }
            >
              {isAutoLoopActive ? <Square size={13} /> : <Play size={13} />}
              <span>
                {t(
                  isAutoLoopActive
                    ? "Stop Firmware Auto-ACK"
                    : "Start Firmware Auto-ACK",
                )}
              </span>
            </button>

            {lastAckMessage && (
              <span
                className="text-xs flex items-center gap-1 font-medium"
                style={{ color: "var(--forest-700)" }}
              >
                <CheckCircle2 size={13} />
                <span>{t(lastAckMessage)}</span>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

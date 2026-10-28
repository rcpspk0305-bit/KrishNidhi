"use client";

import React from "react";
import { Thermometer, Droplets, Wind, Radio, Activity } from "lucide-react";
import { PlantTelemetry } from "@/types/plant-monitor";

interface Props {
  telemetry: PlantTelemetry | null;
  loading: boolean;
}

export default function SensorCardsGrid({ telemetry, loading }: Props) {
  const temp = telemetry?.temperature ?? null;
  const humidity = telemetry?.humidity ?? null;
  const soilPct = telemetry?.soil_moisture ?? null;
  const soilRaw = telemetry?.soil_raw ?? null;
  const motion = telemetry?.motion_detected ?? false;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: "18px",
      }}
    >
      {/* 1. TEMPERATURE CARD */}
      <div
        style={{
          background: "rgba(15, 23, 42, 0.7)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          borderRadius: "18px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#94a3b8", fontSize: "13px", fontWeight: 600 }}>
            <div style={{ padding: "6px", borderRadius: "10px", background: "rgba(244, 63, 94, 0.15)", color: "#f43f5e" }}>
              <Thermometer size={16} />
            </div>
            Ambient Temp (DHT11)
          </div>
          <span style={{ fontSize: "11px", padding: "2px 8px", borderRadius: "999px", background: "rgba(244, 63, 94, 0.1)", color: "#f43f5e", border: "1px solid rgba(244, 63, 94, 0.2)" }}>
            GPIO 12 / D6
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: "6px" }}>
          <span style={{ fontSize: "36px", fontWeight: 800, color: "#f8fafc" }}>
            {loading ? "--" : temp != null ? temp.toFixed(1) : "N/A"}
          </span>
          <span style={{ fontSize: "18px", color: "#94a3b8", fontWeight: 600 }}>°C</span>
        </div>

        <div style={{ fontSize: "12px", color: "#64748b" }}>
          Target: 18.0°C – 30.0°C
          <div style={{ marginTop: "6px", display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: temp != null && temp >= 18 && temp <= 30 ? "#10b981" : "#f59e0b" }} />
            <span style={{ color: temp != null && temp >= 18 && temp <= 30 ? "#10b981" : "#f59e0b", fontWeight: 500 }}>
              {temp != null && temp >= 18 && temp <= 30 ? "Optimal Microclimate" : "Temperature Warning"}
            </span>
          </div>
        </div>
      </div>

      {/* 2. RELATIVE HUMIDITY CARD */}
      <div
        style={{
          background: "rgba(15, 23, 42, 0.7)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          borderRadius: "18px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#94a3b8", fontSize: "13px", fontWeight: 600 }}>
            <div style={{ padding: "6px", borderRadius: "10px", background: "rgba(59, 130, 246, 0.15)", color: "#3b82f6" }}>
              <Wind size={16} />
            </div>
            Relative Humidity (DHT11)
          </div>
          <span style={{ fontSize: "11px", padding: "2px 8px", borderRadius: "999px", background: "rgba(59, 130, 246, 0.1)", color: "#3b82f6", border: "1px solid rgba(59, 130, 246, 0.2)" }}>
            1-Wire Digital
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: "6px" }}>
          <span style={{ fontSize: "36px", fontWeight: 800, color: "#f8fafc" }}>
            {loading ? "--" : humidity != null ? humidity.toFixed(0) : "N/A"}
          </span>
          <span style={{ fontSize: "18px", color: "#94a3b8", fontWeight: 600 }}>% RH</span>
        </div>

        <div style={{ fontSize: "12px", color: "#64748b" }}>
          Target: 50% – 75%
          <div style={{ marginTop: "6px", display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: humidity != null && humidity >= 50 && humidity <= 75 ? "#10b981" : "#f59e0b" }} />
            <span style={{ color: humidity != null && humidity >= 50 && humidity <= 75 ? "#10b981" : "#f59e0b", fontWeight: 500 }}>
              {humidity != null && humidity >= 50 && humidity <= 75 ? "Comfort Zone" : "Sub-optimal Transpiration"}
            </span>
          </div>
        </div>
      </div>

      {/* 3. SOIL MOISTURE CARD */}
      <div
        style={{
          background: "rgba(15, 23, 42, 0.7)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          borderRadius: "18px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#94a3b8", fontSize: "13px", fontWeight: 600 }}>
            <div style={{ padding: "6px", borderRadius: "10px", background: "rgba(16, 185, 129, 0.15)", color: "#10b981" }}>
              <Droplets size={16} />
            </div>
            Soil Moisture (LM393 AO)
          </div>
          <span style={{ fontSize: "11px", padding: "2px 8px", borderRadius: "999px", background: "rgba(16, 185, 129, 0.1)", color: "#10b981", border: "1px solid rgba(16, 185, 129, 0.2)" }}>
            ADC 0 / A0
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: "6px" }}>
          <span style={{ fontSize: "36px", fontWeight: 800, color: soilPct != null && soilPct < 30 ? "#f87171" : "#f8fafc" }}>
            {loading ? "--" : soilPct != null ? soilPct.toFixed(0) : "N/A"}
          </span>
          <span style={{ fontSize: "18px", color: "#94a3b8", fontWeight: 600 }}>%</span>
          {soilRaw != null && (
            <span style={{ fontSize: "12px", color: "#64748b", marginLeft: "auto" }}>
              Raw ADC: <strong>{soilRaw}</strong>
            </span>
          )}
        </div>

        {/* Moisture progress gauge */}
        <div style={{ width: "100%", height: "8px", background: "rgba(255, 255, 255, 0.08)", borderRadius: "999px", overflow: "hidden" }}>
          <div
            style={{
              width: `${Math.min(100, Math.max(0, soilPct ?? 0))}%`,
              height: "100%",
              background: soilPct != null && soilPct < 30 ? "linear-gradient(90deg, #ef4444, #f97316)" : "linear-gradient(90deg, #10b981, #06b6d4)",
              transition: "width 0.4s ease-in-out",
            }}
          />
        </div>

        <div style={{ fontSize: "12px", color: "#64748b", display: "flex", justifyContent: "space-between" }}>
          <span>Auto Trigger: &lt;30%</span>
          <span>Target Cutoff: 55%</span>
        </div>
      </div>

      {/* 4. PIR MOTION DETECTION CARD */}
      <div
        style={{
          background: "rgba(15, 23, 42, 0.7)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          borderRadius: "18px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#94a3b8", fontSize: "13px", fontWeight: 600 }}>
            <div style={{ padding: "6px", borderRadius: "10px", background: "rgba(168, 85, 247, 0.15)", color: "#a855f7" }}>
              <Radio size={16} />
            </div>
            PIR Motion (HC-SR501)
          </div>
          <span style={{ fontSize: "11px", padding: "2px 8px", borderRadius: "999px", background: "rgba(168, 85, 247, 0.1)", color: "#a855f7", border: "1px solid rgba(168, 85, 247, 0.2)" }}>
            GPIO 13 / D7
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "4px" }}>
          <div
            style={{
              width: "14px",
              height: "14px",
              borderRadius: "50%",
              background: motion ? "#a855f7" : "#475569",
              boxShadow: motion ? "0 0 12px #a855f7" : "none",
              transition: "all 0.3s ease",
            }}
          />
          <span style={{ fontSize: "24px", fontWeight: 700, color: motion ? "#e9d5ff" : "#94a3b8" }}>
            {motion ? "Motion Detected" : "Area Clear"}
          </span>
        </div>

        <div style={{ fontSize: "12px", color: "#64748b", marginTop: "auto" }}>
          Infrared passive detection for animal intrusions or human activity near the planter.
        </div>
      </div>
    </div>
  );
}

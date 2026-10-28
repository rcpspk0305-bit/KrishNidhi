"use client";

import React from "react";
import { Sprout, CheckCircle2, AlertTriangle, AlertOctagon, Droplets, Thermometer, Wind, Wifi, WifiOff, Clock } from "lucide-react";
import { PlantRecommendation, PlantTelemetry, PlantDeviceStatus } from "@/types/plant-monitor";

interface Props {
  recommendation: PlantRecommendation | null;
  latest: PlantTelemetry | null;
  loading: boolean;
  deviceStatus?: PlantDeviceStatus | null;
}

export default function PlantHealthHero({ recommendation, latest, loading, deviceStatus }: Props) {
  const healthScore = recommendation?.health_score ?? 85;
  const status = recommendation?.status ?? "Optimal";
  const plantName = recommendation?.plant_name ?? "Indoor Smart Planter";

  const getStatusColor = (score: number) => {
    if (score >= 80) return { bg: "rgba(16, 185, 129, 0.15)", text: "#10b981", border: "rgba(16, 185, 129, 0.3)" };
    if (score >= 60) return { bg: "rgba(245, 158, 11, 0.15)", text: "#f59e0b", border: "rgba(245, 158, 11, 0.3)" };
    return { bg: "rgba(239, 68, 68, 0.15)", text: "#ef4444", border: "rgba(239, 68, 68, 0.3)" };
  };

  const statusStyle = getStatusColor(healthScore);

  return (
    <div
      style={{
        background: "linear-gradient(135deg, rgba(20, 83, 45, 0.25) 0%, rgba(15, 23, 42, 0.6) 100%)",
        border: "1px solid rgba(34, 197, 94, 0.2)",
        borderRadius: "20px",
        padding: "28px",
        backdropFilter: "blur(12px)",
        display: "flex",
        flexDirection: "column",
        gap: "20px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "16px",
              background: "rgba(34, 197, 94, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "1px solid rgba(34, 197, 94, 0.3)",
            }}
          >
            <Sprout size={32} color="#4ade80" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
              <span
                style={{
                  fontSize: "12px",
                  fontWeight: 600,
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                  color: "#4ade80",
                }}
              >
                NodeMCU
              </span>
              <span
                style={{
                  fontSize: "12px",
                  padding: "2px 8px",
                  borderRadius: "999px",
                  background: statusStyle.bg,
                  color: statusStyle.text,
                  border: `1px solid ${statusStyle.border}`,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                }}
              >
                {healthScore >= 80 ? <CheckCircle2 size={12} /> : healthScore >= 60 ? <AlertTriangle size={12} /> : <AlertOctagon size={12} />}
                Health: {status}
              </span>
              <span
                style={{
                  fontSize: "12px",
                  padding: "2px 8px",
                  borderRadius: "999px",
                  background: deviceStatus?.online ? "rgba(34, 197, 94, 0.15)" : "rgba(239, 68, 68, 0.15)",
                  color: deviceStatus?.online ? "#4ade80" : "#fca5a5",
                  border: `1px solid ${deviceStatus?.online ? "rgba(34, 197, 94, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                }}
              >
                {deviceStatus?.online ? <Wifi size={12} /> : <WifiOff size={12} />}
                ESP8266: {deviceStatus?.online ? "Connected" : "Offline"}
              </span>
              <span
                style={{
                  fontSize: "12px",
                  padding: "2px 8px",
                  borderRadius: "999px",
                  background: "rgba(59, 130, 246, 0.15)",
                  color: "#60a5fa",
                  border: "1px solid rgba(59, 130, 246, 0.3)",
                }}
              >
                Mode: {latest?.control_mode || deviceStatus?.control_mode || "AUTO"}
              </span>
              <span
                style={{
                  fontSize: "12px",
                  padding: "2px 8px",
                  borderRadius: "999px",
                  background: "rgba(255, 255, 255, 0.05)",
                  color: "#94a3b8",
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                }}
              >
                <Clock size={12} />
                Updated: {latest?.timestamp ? new Date(latest.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "Awaiting telemetry"}
              </span>
            </div>
            <h1 style={{ fontSize: "28px", fontWeight: 700, margin: "6px 0 0 0", color: "#f8fafc" }}>
              {plantName}
            </h1>
          </div>
        </div>

        {/* Health Gauge Box */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "14px",
            background: "rgba(15, 23, 42, 0.6)",
            padding: "12px 20px",
            borderRadius: "16px",
            border: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "11px", textTransform: "uppercase", color: "#94a3b8", fontWeight: 600 }}>
              Agronomic Index
            </div>
            <div style={{ fontSize: "32px", fontWeight: 800, color: statusStyle.text, lineHeight: 1 }}>
              {loading ? "--" : healthScore}
              <span style={{ fontSize: "16px", fontWeight: 500, color: "#64748b" }}>/100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Snapshot quick telemetry ribbon */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
          gap: "12px",
          marginTop: "4px",
        }}
      >
        <div style={{ background: "rgba(255, 255, 255, 0.04)", padding: "12px 14px", borderRadius: "12px", border: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#94a3b8", fontSize: "12px" }}>
            <Thermometer size={14} color="#f87171" /> Temperature
          </div>
          <div style={{ fontSize: "18px", fontWeight: 700, marginTop: "4px", color: "#f1f5f9" }}>
            {latest?.temperature != null ? `${latest.temperature.toFixed(1)} °C` : "N/A"}
          </div>
        </div>

        <div style={{ background: "rgba(255, 255, 255, 0.04)", padding: "12px 14px", borderRadius: "12px", border: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#94a3b8", fontSize: "12px" }}>
            <Wind size={14} color="#60a5fa" /> Humidity
          </div>
          <div style={{ fontSize: "18px", fontWeight: 700, marginTop: "4px", color: "#f1f5f9" }}>
            {latest?.humidity != null ? `${latest.humidity.toFixed(0)} %` : "N/A"}
          </div>
        </div>

        <div style={{ background: "rgba(255, 255, 255, 0.04)", padding: "12px 14px", borderRadius: "12px", border: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#94a3b8", fontSize: "12px" }}>
            <Droplets size={14} color="#34d399" /> Soil Moisture
          </div>
          <div style={{ fontSize: "18px", fontWeight: 700, marginTop: "4px", color: "#f1f5f9" }}>
            {latest?.soil_moisture != null ? `${latest.soil_moisture.toFixed(0)} %` : "N/A"}
          </div>
        </div>

        <div style={{ background: "rgba(255, 255, 255, 0.04)", padding: "12px 14px", borderRadius: "12px", border: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#94a3b8", fontSize: "12px" }}>
            <Sprout size={14} color="#a78bfa" /> Operating Mode
          </div>
          <div style={{ fontSize: "18px", fontWeight: 700, marginTop: "4px", color: "#f1f5f9" }}>
            {latest?.control_mode || "AUTO"}
          </div>
        </div>
      </div>
    </div>
  );
}

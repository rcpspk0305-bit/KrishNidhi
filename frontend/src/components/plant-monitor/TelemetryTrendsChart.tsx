"use client";

import React, { useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { TrendingUp, RefreshCw } from "lucide-react";
import { PlantTelemetry } from "@/types/plant-monitor";

interface Props {
  data: PlantTelemetry[];
  onRefresh?: () => void;
  loading?: boolean;
}

export default function TelemetryTrendsChart({ data, onRefresh, loading }: Props) {
  const [selectedMetric, setSelectedMetric] = useState<"all" | "soil" | "temp" | "humidity" | "pump">("all");

  const formattedData = data.map((d) => {
    const timeStr = d.timestamp ? new Date(d.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "";
    return {
      time: timeStr,
      temperature: d.temperature != null ? Number(d.temperature.toFixed(1)) : null,
      humidity: d.humidity != null ? Number(d.humidity.toFixed(0)) : null,
      soil_moisture: d.soil_moisture != null ? Number(d.soil_moisture.toFixed(0)) : null,
      pump_active: d.pump_on ? 100 : 0,
    };
  });

  return (
    <div
      style={{
        background: "rgba(15, 23, 42, 0.7)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: "20px",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "18px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{ padding: "8px", borderRadius: "10px", background: "rgba(34, 197, 94, 0.15)", color: "#22c55e" }}>
            <TrendingUp size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, margin: 0, color: "#f8fafc" }}>
              Environmental Telemetry Trends
            </h3>
            <span style={{ fontSize: "12px", color: "#64748b" }}>
              Continuous chronological sensor log from ESP8266
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Metric filter buttons */}
          <div style={{ display: "flex", background: "rgba(0, 0, 0, 0.3)", padding: "3px", borderRadius: "10px", border: "1px solid rgba(255, 255, 255, 0.05)" }}>
            {(["all", "soil", "temp", "humidity", "pump"] as const).map((filter) => (
              <button
                key={filter}
                type="button"
                onClick={() => setSelectedMetric(filter)}
                style={{
                  padding: "4px 10px",
                  borderRadius: "6px",
                  border: "none",
                  background: selectedMetric === filter ? "rgba(34, 197, 94, 0.2)" : "transparent",
                  color: selectedMetric === filter ? "#4ade80" : "#94a3b8",
                  fontSize: "12px",
                  fontWeight: selectedMetric === filter ? 600 : 400,
                  cursor: "pointer",
                }}
              >
                {filter.toUpperCase()}
              </button>
            ))}
          </div>

          {onRefresh && (
            <button
              type="button"
              onClick={onRefresh}
              disabled={loading}
              style={{
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                color: "#e2e8f0",
                padding: "6px 12px",
                borderRadius: "8px",
                fontSize: "12px",
                fontWeight: 500,
                cursor: loading ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
              {loading ? "Syncing..." : "Sync"}
            </button>
          )}
        </div>
      </div>

      {formattedData.length === 0 ? (
        <div style={{ height: "260px", display: "flex", alignItems: "center", justifyContent: "center", color: "#64748b", fontSize: "14px" }}>
          No historical telemetry points found. Telemetry will plot here once received from ESP8266.
        </div>
      ) : (
        <div style={{ width: "100%", height: "280px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
              <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  borderColor: "rgba(255, 255, 255, 0.1)",
                  borderRadius: "12px",
                  fontSize: "12px",
                  color: "#f8fafc",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />

              {(selectedMetric === "all" || selectedMetric === "soil") && (
                <Line
                  type="monotone"
                  dataKey="soil_moisture"
                  name="Soil Moisture (%)"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 5 }}
                />
              )}
              {(selectedMetric === "all" || selectedMetric === "temp") && (
                <Line
                  type="monotone"
                  dataKey="temperature"
                  name="Temperature (°C)"
                  stroke="#f43f5e"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              )}
              {(selectedMetric === "all" || selectedMetric === "humidity") && (
                <Line
                  type="monotone"
                  dataKey="humidity"
                  name="Humidity (% RH)"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              )}
              {(selectedMetric === "all" || selectedMetric === "pump") && (
                <Line
                  type="stepAfter"
                  dataKey="pump_active"
                  name="Pump Usage Active (0/100%)"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

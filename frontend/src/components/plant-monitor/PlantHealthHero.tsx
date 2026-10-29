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
  const plantName = recommendation?.plant_name ?? "Indoor Botanical Specimen";

  const getStatusMeta = (score: number) => {
    if (score >= 80) {
      return {
        pillClass: "pill-forest",
        icon: <CheckCircle2 size={13} className="text-forest-700" />,
        label: "Optimal Microclimate",
      };
    }
    if (score >= 60) {
      return {
        pillClass: "pill-gold",
        icon: <AlertTriangle size={13} className="text-gold-700" />,
        label: "Attention Recommended",
      };
    }
    return {
      pillClass: "pill-terracotta",
      icon: <AlertOctagon size={13} className="text-terracotta-700" />,
      label: "Intervention Required",
    };
  };

  const statusMeta = getStatusMeta(healthScore);

  return (
    <div className="botanical-card p-6 md:p-8 flex flex-col gap-6 bg-white">
      {/* Top Header Row */}
      <div className="flex justify-between items-start flex-wrap gap-4">
        <div className="flex items-start gap-4">
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 border"
            style={{
              backgroundColor: "var(--forest-50)",
              borderColor: "var(--forest-100)",
              color: "var(--forest-700)",
            }}
          >
            <Sprout size={28} />
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="mono-tag font-semibold uppercase tracking-wider" style={{ color: "var(--forest-600)" }}>
                ESP8266 Telemetry Workspace
              </span>
              <span className={statusMeta.pillClass}>
                {statusMeta.icon}
                <span>Health: {status}</span>
              </span>
              <span className={deviceStatus?.online ? "pill-forest" : "pill-terracotta"}>
                {deviceStatus?.online ? <Wifi size={12} /> : <WifiOff size={12} />}
                <span>{deviceStatus?.online ? "Hardware Linked" : "Offline"}</span>
              </span>
              <span className="pill-dew">
                <span>Mode: {latest?.control_mode || deviceStatus?.control_mode || "AUTO"}</span>
              </span>
            </div>

            <h1 className="title-lg md:text-3xl font-serif text-forest-900 mt-1">
              {plantName}
            </h1>
            <p className="text-xs flex items-center gap-1.5 mt-1" style={{ color: "var(--text-muted)" }}>
              <Clock size={12} />
              <span>Telemetry Timestamp:</span>
              <span className="font-medium" style={{ color: "var(--text-secondary)" }}>
                {latest?.timestamp ? new Date(latest.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "Awaiting sensor broadcast"}
              </span>
            </p>
          </div>
        </div>

        {/* Agronomic Index Score Card */}
        <div
          className="flex items-center gap-4 px-5 py-3 rounded-2xl border"
          style={{
            backgroundColor: "var(--bg-subtle)",
            borderColor: "var(--border-subtle)",
          }}
        >
          <div className="text-right">
            <span className="mono-tag block text-[11px] uppercase tracking-wider font-semibold" style={{ color: "var(--text-muted)" }}>
              Agronomic Index
            </span>
            <div className="metric-num text-3xl font-serif mt-0.5" style={{ color: "var(--forest-800)" }}>
              {loading ? "--" : healthScore}
              <span className="text-sm font-sans font-normal ml-1" style={{ color: "var(--text-muted)" }}>
                / 100
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Snapshot quick telemetry ribbon */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-4 border-t" style={{ borderColor: "var(--border-subtle)" }}>
        {/* Ambient Temperature */}
        <div
          className="p-3.5 rounded-xl border flex flex-col justify-between"
          style={{ backgroundColor: "var(--bg-subtle)", borderColor: "var(--border-subtle)" }}
        >
          <div className="flex items-center gap-1.5 text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
            <Thermometer size={14} style={{ color: "var(--terracotta-600)" }} />
            <span>Temperature</span>
          </div>
          <div className="metric-num text-2xl font-serif mt-1" style={{ color: "var(--text-primary)" }}>
            {latest?.temperature != null ? `${latest.temperature.toFixed(1)}°C` : "N/A"}
          </div>
        </div>

        {/* Relative Humidity */}
        <div
          className="p-3.5 rounded-xl border flex flex-col justify-between"
          style={{ backgroundColor: "var(--bg-subtle)", borderColor: "var(--border-subtle)" }}
        >
          <div className="flex items-center gap-1.5 text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
            <Wind size={14} style={{ color: "var(--dew-600)" }} />
            <span>Humidity</span>
          </div>
          <div className="metric-num text-2xl font-serif mt-1" style={{ color: "var(--text-primary)" }}>
            {latest?.humidity != null ? `${latest.humidity.toFixed(0)}%` : "N/A"}
          </div>
        </div>

        {/* Soil Moisture */}
        <div
          className="p-3.5 rounded-xl border flex flex-col justify-between"
          style={{ backgroundColor: "var(--bg-subtle)", borderColor: "var(--border-subtle)" }}
        >
          <div className="flex items-center gap-1.5 text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
            <Droplets size={14} style={{ color: "var(--forest-600)" }} />
            <span>Soil Moisture</span>
          </div>
          <div className="metric-num text-2xl font-serif mt-1" style={{ color: "var(--text-primary)" }}>
            {latest?.soil_moisture != null ? `${latest.soil_moisture.toFixed(0)}%` : "N/A"}
          </div>
        </div>

        {/* Operating Control Mode */}
        <div
          className="p-3.5 rounded-xl border flex flex-col justify-between"
          style={{ backgroundColor: "var(--bg-subtle)", borderColor: "var(--border-subtle)" }}
        >
          <div className="flex items-center gap-1.5 text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
            <Sprout size={14} style={{ color: "var(--gold-600)" }} />
            <span>Control Mode</span>
          </div>
          <div className="metric-num text-xl font-serif mt-1 uppercase" style={{ color: "var(--forest-700)" }}>
            {latest?.control_mode || deviceStatus?.control_mode || "AUTO"}
          </div>
        </div>
      </div>
    </div>
  );
}

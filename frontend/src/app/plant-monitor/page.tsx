"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { ArrowLeft, RefreshCw, Sprout, ShieldCheck, HelpCircle } from "lucide-react";
import PlantHealthHero from "@/components/plant-monitor/PlantHealthHero";
import SensorCardsGrid from "@/components/plant-monitor/SensorCardsGrid";
import PumpControlWidget from "@/components/plant-monitor/PumpControlWidget";
import TelemetryTrendsChart from "@/components/plant-monitor/TelemetryTrendsChart";
import AIRecommendationsCard from "@/components/plant-monitor/AIRecommendationsCard";
import DeviceStatusBadge from "@/components/plant-monitor/DeviceStatusBadge";
import AlertsDrawer from "@/components/plant-monitor/AlertsDrawer";
import HardwareSimulatorPanel from "@/components/plant-monitor/HardwareSimulatorPanel";

import { plantApi } from "@/lib/plant-api";
import { usePlantMonitorSSE } from "@/hooks/usePlantMonitorSSE";
import {
  PlantTelemetry,
  PlantDeviceStatus,
  PlantRecommendation,
  PlantAlert,
} from "@/types/plant-monitor";

export default function PlantMonitorPage() {
  const [deviceId] = useState<string>("esp8266-plant-01");
  const [telemetry, setTelemetry] = useState<PlantTelemetry | null>(null);
  const [history, setHistory] = useState<PlantTelemetry[]>([]);
  const [deviceStatus, setDeviceStatus] = useState<PlantDeviceStatus | null>(null);
  const [recommendation, setRecommendation] = useState<PlantRecommendation | null>(null);
  const [alerts, setAlerts] = useState<PlantAlert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [syncing, setSyncing] = useState<boolean>(false);

  // Load all initial data from REST API
  const refreshAllData = useCallback(async () => {
    setSyncing(true);
    try {
      const [latestRes, historyRes, statusRes, recRes, alertsRes] = await Promise.allSettled([
        plantApi.getLatestTelemetry(deviceId),
        plantApi.getTelemetryHistory(deviceId, 24, 60),
        plantApi.getDeviceStatus(deviceId),
        plantApi.getRecommendations(deviceId),
        plantApi.getAlerts(deviceId),
      ]);

      if (latestRes.status === "fulfilled") setTelemetry(latestRes.value);
      if (historyRes.status === "fulfilled") setHistory(historyRes.value);
      if (statusRes.status === "fulfilled") setDeviceStatus(statusRes.value);
      if (recRes.status === "fulfilled") setRecommendation(recRes.value);
      if (alertsRes.status === "fulfilled") setAlerts(alertsRes.value);
    } catch (err) {
      console.warn("Telemetry refresh warning:", err);
    } finally {
      setLoading(false);
      setSyncing(false);
    }
  }, [deviceId]);

  useEffect(() => {
    refreshAllData();
    // Poll fallback every 15s in case SSE is interrupted
    const interval = setInterval(refreshAllData, 15000);
    return () => clearInterval(interval);
  }, [refreshAllData]);

  // Connect to live Server-Sent Events (SSE)
  const { isConnected: sseConnected, lastEventTime } = usePlantMonitorSSE({
    deviceId,
    onTelemetry: (newTelemetry) => {
      setTelemetry(newTelemetry);
      setHistory((prev) => [...prev.slice(-59), newTelemetry]);
      // Update device status online
      setDeviceStatus((prev) =>
        prev
          ? {
              ...prev,
              online: true,
              pump_state: newTelemetry.pump_on,
              control_mode: newTelemetry.control_mode,
              last_seen: newTelemetry.timestamp,
              seconds_since_last_seen: 0,
            }
          : null
      );
    },
    onPumpStateUpdated: (data) => {
      setDeviceStatus((prev) =>
        prev
          ? {
              ...prev,
              pump_state: data.confirmed_state,
              control_mode: data.control_mode as any,
            }
          : null
      );
    },
    onCommandCreated: () => {
      // Command submitted to queue
    },
  });

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "radial-gradient(ellipse at top, #064e3b 0%, #022c22 40%, #090d16 100%)",
        color: "#f8fafc",
        padding: "32px 20px 60px 20px",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <div style={{ maxWidth: "1280px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "24px" }}>
        
        {/* Navigation & Status Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <Link
              href="/"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                color: "#94a3b8",
                textDecoration: "none",
                fontSize: "13px",
                fontWeight: 500,
                padding: "8px 12px",
                borderRadius: "10px",
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
              }}
            >
              <ArrowLeft size={16} /> Home
            </Link>
            <div>
              <div style={{ fontSize: "12px", color: "#4ade80", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                AI-Powered Smart Plant Monitoring System
              </div>
              <h2 style={{ fontSize: "20px", fontWeight: 700, margin: "2px 0 0 0", color: "#f8fafc" }}>
                Active Telemetry & Automation Dashboard
              </h2>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
            <DeviceStatusBadge
              status={deviceStatus}
              sseConnected={sseConnected}
              lastEventTime={lastEventTime}
            />

            <button
              type="button"
              onClick={refreshAllData}
              disabled={syncing}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                background: "rgba(34, 197, 94, 0.15)",
                border: "1px solid rgba(34, 197, 94, 0.3)",
                color: "#4ade80",
                padding: "8px 14px",
                borderRadius: "10px",
                fontSize: "13px",
                fontWeight: 600,
                cursor: syncing ? "not-allowed" : "pointer",
              }}
            >
              <RefreshCw size={14} className={syncing ? "animate-spin" : ""} />
              {syncing ? "Syncing..." : "Refresh"}
            </button>
          </div>
        </div>

        {/* Active System Alerts Drawer */}
        <AlertsDrawer alerts={alerts} onAlertAcknowledged={refreshAllData} />

        {/* Hero Plant Environmental Suitability Card */}
        <PlantHealthHero
          recommendation={recommendation}
          latest={telemetry}
          loading={loading}
        />

        {/* 4 Core Sensor Telemetry Cards */}
        <SensorCardsGrid telemetry={telemetry} loading={loading} />

        {/* Primary Controls & Trends Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "24px" }}>
          {/* Water Pump Actuator Controller */}
          <PumpControlWidget
            deviceId={deviceId}
            confirmedPumpOn={deviceStatus?.pump_state ?? false}
            currentMode={deviceStatus?.control_mode ?? "AUTO"}
            onCommandDispatched={refreshAllData}
          />

          {/* AI Agronomic Insights */}
          <AIRecommendationsCard
            recommendation={recommendation}
            loading={loading}
          />
        </div>

        {/* Historical Trends Recharts Component */}
        <TelemetryTrendsChart
          data={history}
          onRefresh={refreshAllData}
          loading={syncing}
        />

        {/* Virtual Hardware Simulator Drawer */}
        <HardwareSimulatorPanel
          deviceId={deviceId}
          confirmedPumpOn={deviceStatus?.pump_state ?? false}
          currentMode={deviceStatus?.control_mode ?? "AUTO"}
          onTelemetryEmitted={refreshAllData}
        />

        {/* Footer */}
        <div style={{ textAlign: "center", color: "#64748b", fontSize: "12px", paddingTop: "20px" }}>
          AI-Powered IoT Smart Plant Monitoring & Irrigation System &bull; ESP8266 NodeMCU ESP-12E Architecture &bull; Computer Science & Engineering Final Project
        </div>
      </div>
    </main>
  );
}

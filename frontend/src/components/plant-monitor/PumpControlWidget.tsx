"use client";

import React, { useState } from "react";
import { Power, ShieldAlert, Cpu, CheckCircle2, Clock, Loader2, Info } from "lucide-react";
import { plantApi } from "@/lib/plant-api";

interface Props {
  deviceId: string;
  confirmedPumpOn: boolean;
  currentMode: "AUTO" | "MANUAL" | "OFF";
  onCommandDispatched?: () => void;
  lastWateringTime?: string | null;
  pumpRuntimeSeconds?: number | null;
}

export default function PumpControlWidget({
  deviceId,
  confirmedPumpOn,
  currentMode,
  onCommandDispatched,
  lastWateringTime,
  pumpRuntimeSeconds,
}: Props) {
  const [submitting, setSubmitting] = useState(false);
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleModeChange = async (newMode: "AUTO" | "MANUAL" | "OFF") => {
    if (newMode === currentMode) return;
    setSubmitting(true);
    setPendingAction(`Switching mode to ${newMode}`);
    setErrorMsg(null);
    try {
      await plantApi.requestPumpControl(deviceId, "SET_MODE", newMode);
      if (onCommandDispatched) onCommandDispatched();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Failed to switch mode");
    } finally {
      setSubmitting(false);
      setTimeout(() => setPendingAction(null), 3000);
    }
  };

  const handleTogglePump = async () => {
    if (currentMode !== "MANUAL") {
      setErrorMsg("Manual pump toggle is only available in MANUAL mode. Switch mode first.");
      return;
    }
    const targetState = !confirmedPumpOn;
    setSubmitting(true);
    setPendingAction(`Commanding pump ${targetState ? "ON" : "OFF"}`);
    setErrorMsg(null);
    try {
      await plantApi.requestPumpControl(deviceId, "SET_PUMP", targetState);
      if (onCommandDispatched) onCommandDispatched();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Failed to submit pump command");
    } finally {
      setSubmitting(false);
      setTimeout(() => setPendingAction(null), 3000);
    }
  };

  return (
    <div
      style={{
        background: "rgba(15, 23, 42, 0.7)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: "20px",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "20px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              padding: "8px",
              borderRadius: "12px",
              background: confirmedPumpOn ? "rgba(16, 185, 129, 0.2)" : "rgba(100, 116, 139, 0.2)",
              color: confirmedPumpOn ? "#10b981" : "#94a3b8",
            }}
          >
            <Power size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, margin: 0, color: "#f8fafc" }}>
              Water Pump Actuator
            </h3>
            <span style={{ fontSize: "12px", color: "#64748b" }}>
              Relay IN: GPIO 14 (D5) &bull; 5V DC Submersible
            </span>
          </div>
        </div>

        {/* Confirmed Physical State Badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            background: confirmedPumpOn ? "rgba(16, 185, 129, 0.15)" : "rgba(15, 23, 42, 0.6)",
            border: `1px solid ${confirmedPumpOn ? "rgba(16, 185, 129, 0.3)" : "rgba(255, 255, 255, 0.1)"}`,
            padding: "6px 14px",
            borderRadius: "999px",
          }}
        >
          <span
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              background: confirmedPumpOn ? "#10b981" : "#64748b",
              boxShadow: confirmedPumpOn ? "0 0 10px #10b981" : "none",
            }}
          />
          <span
            style={{
              fontSize: "13px",
              fontWeight: 600,
              color: confirmedPumpOn ? "#10b981" : "#94a3b8",
            }}
          >
            {confirmedPumpOn ? "PUMP ACTIVE (IRRIGATING)" : "PUMP IDLE (STANDBY)"}
          </span>
        </div>
      </div>

      {errorMsg && (
        <div
          style={{
            background: "rgba(239, 68, 68, 0.15)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            color: "#fca5a5",
            padding: "10px 14px",
            borderRadius: "10px",
            fontSize: "13px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <ShieldAlert size={16} />
          {errorMsg}
        </div>
      )}

      {pendingAction && (
        <div
          style={{
            background: "rgba(59, 130, 246, 0.15)",
            border: "1px solid rgba(59, 130, 246, 0.3)",
            color: "#93c5fd",
            padding: "10px 14px",
            borderRadius: "10px",
            fontSize: "13px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <Loader2 size={16} className="animate-spin" />
          {pendingAction}... Awaiting ESP8266 acknowledgment.
        </div>
      )}

      {/* Mode Selector and Manual Action Controls */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "16px",
          alignItems: "center",
        }}
      >
        {/* Mode Selector */}
        <div>
          <label style={{ fontSize: "12px", fontWeight: 600, color: "#94a3b8", marginBottom: "8px", display: "block" }}>
            OPERATING CONTROL MODE
          </label>
          <div
            style={{
              display: "flex",
              background: "rgba(0, 0, 0, 0.3)",
              padding: "4px",
              borderRadius: "12px",
              border: "1px solid rgba(255, 255, 255, 0.05)",
            }}
          >
            {(["AUTO", "MANUAL", "OFF"] as const).map((m) => {
              const isSelected = currentMode === m;
              return (
                <button
                  key={m}
                  type="button"
                  onClick={() => handleModeChange(m)}
                  disabled={submitting}
                  style={{
                    flex: 1,
                    padding: "8px 12px",
                    borderRadius: "8px",
                    border: "none",
                    background: isSelected ? "rgba(34, 197, 94, 0.2)" : "transparent",
                    color: isSelected ? "#4ade80" : "#94a3b8",
                    fontWeight: isSelected ? 700 : 500,
                    fontSize: "13px",
                    cursor: submitting ? "not-allowed" : "pointer",
                    transition: "all 0.2s ease",
                  }}
                >
                  {m}
                </button>
              );
            })}
          </div>
        </div>

        {/* Manual Actuator Button */}
        <div>
          <label style={{ fontSize: "12px", fontWeight: 600, color: "#94a3b8", marginBottom: "8px", display: "block" }}>
            DIRECT PHYSICAL RELAY TOGGLE
          </label>
          <button
            type="button"
            onClick={handleTogglePump}
            disabled={submitting || currentMode !== "MANUAL"}
            style={{
              width: "100%",
              padding: "11px 16px",
              borderRadius: "12px",
              border: `1px solid ${
                confirmedPumpOn
                  ? "rgba(239, 68, 68, 0.4)"
                  : currentMode === "MANUAL"
                  ? "rgba(34, 197, 94, 0.4)"
                  : "rgba(255, 255, 255, 0.1)"
              }`,
              background: confirmedPumpOn
                ? "rgba(239, 68, 68, 0.2)"
                : currentMode === "MANUAL"
                ? "rgba(34, 197, 94, 0.2)"
                : "rgba(255, 255, 255, 0.04)",
              color: confirmedPumpOn
                ? "#f87171"
                : currentMode === "MANUAL"
                ? "#4ade80"
                : "#64748b",
              fontWeight: 700,
              fontSize: "14px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              cursor: currentMode === "MANUAL" && !submitting ? "pointer" : "not-allowed",
              transition: "all 0.2s ease",
            }}
          >
            {submitting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Power size={16} />
            )}
            {confirmedPumpOn
              ? "TURN PUMP OFF (MANUAL)"
              : currentMode === "MANUAL"
              ? "TURN PUMP ON (MANUAL)"
              : "ENABLED ONLY IN MANUAL MODE"}
          </button>
        </div>
      </div>

      {/* Runtime & Watering Status Bar */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: "10px",
          background: "rgba(0, 0, 0, 0.2)",
          padding: "12px",
          borderRadius: "12px",
          border: "1px solid rgba(255, 255, 255, 0.05)",
          fontSize: "12px",
        }}
      >
        <div>
          <span style={{ color: "#64748b", display: "block" }}>Last Watering</span>
          <strong style={{ color: "#e2e8f0" }}>
            {lastWateringTime ? new Date(lastWateringTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "None recorded"}
          </strong>
        </div>
        <div>
          <span style={{ color: "#64748b", display: "block" }}>Pump Runtime</span>
          <strong style={{ color: confirmedPumpOn ? "#10b981" : "#e2e8f0" }}>
            {confirmedPumpOn ? `${pumpRuntimeSeconds || 0}s (Running)` : "0s (Standby)"}
          </strong>
        </div>
        <div>
          <span style={{ color: "#64748b", display: "block" }}>Confirmation Status</span>
          <strong style={{ color: confirmedPumpOn ? "#10b981" : "#94a3b8" }}>
            {confirmedPumpOn ? "Verified Active" : "Verified Inactive"}
          </strong>
        </div>
      </div>

      {/* Safety limit badges */}
      <div
        style={{
          display: "flex",
          gap: "16px",
          flexWrap: "wrap",
          paddingTop: "14px",
          borderTop: "1px solid rgba(255, 255, 255, 0.05)",
          fontSize: "12px",
          color: "#94a3b8",
        }}
      >
        <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
          <Clock size={13} color="#f59e0b" /> Max Run: <strong>15s Watchdog</strong>
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
          <Clock size={13} color="#3b82f6" /> Min Cooldown: <strong>60s Rest</strong>
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
          <CheckCircle2 size={13} color="#10b981" /> Fail-safe: <strong>Safe Boot OFF</strong>
        </span>
      </div>
    </div>
  );
}

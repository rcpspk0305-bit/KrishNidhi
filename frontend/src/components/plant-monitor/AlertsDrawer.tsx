"use client";

import React from "react";
import { AlertCircle, Check, BellRing } from "lucide-react";
import { PlantAlert } from "@/types/plant-monitor";
import { plantApi } from "@/lib/plant-api";

interface Props {
  alerts: PlantAlert[];
  onAlertAcknowledged?: () => void;
}

export default function AlertsDrawer({ alerts, onAlertAcknowledged }: Props) {
  const unacknowledged = alerts.filter((a) => !a.acknowledged);

  if (unacknowledged.length === 0) return null;

  const handleAcknowledge = async (id: number) => {
    try {
      await plantApi.acknowledgeAlert(id);
      if (onAlertAcknowledged) onAlertAcknowledged();
    } catch (e) {
      console.error("Failed to acknowledge alert", e);
    }
  };

  return (
    <div
      style={{
        background: "rgba(239, 68, 68, 0.08)",
        border: "1px solid rgba(239, 68, 68, 0.25)",
        borderRadius: "16px",
        padding: "18px",
        display: "flex",
        flexDirection: "column",
        gap: "12px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#f87171", fontSize: "14px", fontWeight: 700 }}>
        <BellRing size={16} />
        Active System & Sensor Alerts ({unacknowledged.length})
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {unacknowledged.map((alert) => (
          <div
            key={alert.id}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              background: "rgba(15, 23, 42, 0.6)",
              padding: "10px 14px",
              borderRadius: "10px",
              border: "1px solid rgba(255, 255, 255, 0.05)",
              flexWrap: "wrap",
              gap: "10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <AlertCircle size={16} color={alert.severity === "high" ? "#ef4444" : "#f59e0b"} />
              <div>
                <span style={{ fontSize: "13px", color: "#f1f5f9", fontWeight: 500 }}>
                  {alert.message}
                </span>
                <div style={{ fontSize: "11px", color: "#64748b" }}>
                  {new Date(alert.timestamp).toLocaleTimeString()} &bull; Severity: {alert.severity.toUpperCase()}
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => handleAcknowledge(alert.id)}
              style={{
                background: "rgba(255, 255, 255, 0.08)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                color: "#cbd5e1",
                padding: "5px 12px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              <Check size={13} />
              Acknowledge
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

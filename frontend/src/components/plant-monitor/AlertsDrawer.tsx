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
      role="region"
      aria-label="Active System Alerts"
      className="botanical-card p-5"
      style={{
        backgroundColor: "var(--terracotta-50)",
        borderColor: "var(--terracotta-100)",
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 font-semibold text-sm" style={{ color: "var(--terracotta-700)" }}>
          <BellRing size={16} />
          <span>Active Agronomic & Hardware Alerts ({unacknowledged.length})</span>
        </div>
        <span className="mono-tag" style={{ color: "var(--terracotta-600)" }}>
          Requires Attention
        </span>
      </div>

      <div className="flex flex-col gap-2.5">
        {unacknowledged.map((alert) => (
          <div
            key={alert.id}
            className="flex items-center justify-between flex-wrap gap-3 p-3 rounded-xl bg-white border"
            style={{ borderColor: "rgba(189, 81, 52, 0.15)" }}
          >
            <div className="flex items-start gap-2.5">
              <AlertCircle
                size={16}
                className="mt-0.5 shrink-0"
                style={{ color: alert.severity === "high" ? "var(--terracotta-600)" : "var(--gold-600)" }}
              />
              <div>
                <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                  {alert.message}
                </p>
                <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                  {new Date(alert.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} &bull;{" "}
                  <span className="uppercase font-semibold tracking-wider text-[10px]">
                    {alert.severity} priority
                  </span>
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => handleAcknowledge(alert.id)}
              className="btn-secondary text-xs py-1.5 px-3"
              style={{ borderRadius: "var(--radius-sm)" }}
            >
              <Check size={13} />
              <span>Acknowledge</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

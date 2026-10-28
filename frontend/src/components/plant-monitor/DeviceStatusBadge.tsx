"use client";

import React from "react";
import { Wifi, WifiOff, Server, ShieldCheck, Activity } from "lucide-react";
import { PlantDeviceStatus } from "@/types/plant-monitor";

interface Props {
  status: PlantDeviceStatus | null;
  sseConnected: boolean;
  lastEventTime: Date | null;
}

export default function DeviceStatusBadge({ status, sseConnected, lastEventTime }: Props) {
  const isOnline = status?.online ?? false;
  const secondsAgo = status?.seconds_since_last_seen;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        flexWrap: "wrap",
      }}
    >
      {/* ESP8266 Hardware Status */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          background: isOnline ? "rgba(16, 185, 129, 0.12)" : "rgba(239, 68, 68, 0.12)",
          border: `1px solid ${isOnline ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
          padding: "6px 14px",
          borderRadius: "999px",
        }}
      >
        {isOnline ? (
          <>
            <span
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#10b981",
                boxShadow: "0 0 8px #10b981",
              }}
            />
            <Wifi size={14} color="#10b981" />
            <span style={{ fontSize: "12px", fontWeight: 600, color: "#10b981" }}>
              ESP8266 Online
            </span>
          </>
        ) : (
          <>
            <span
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#ef4444",
              }}
            />
            <WifiOff size={14} color="#ef4444" />
            <span style={{ fontSize: "12px", fontWeight: 600, color: "#ef4444" }}>
              ESP8266 Offline
            </span>
          </>
        )}
      </div>

      {/* SSE Real-time Feed */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          background: "rgba(255, 255, 255, 0.04)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          padding: "6px 12px",
          borderRadius: "999px",
          fontSize: "12px",
          color: "#94a3b8",
        }}
      >
        <Server size={13} color={sseConnected ? "#38bdf8" : "#94a3b8"} />
        <span>Live SSE:</span>
        <strong style={{ color: sseConnected ? "#38bdf8" : "#f59e0b" }}>
          {sseConnected ? "Streaming" : "Connecting..."}
        </strong>
      </div>

      {/* Last Ping Age */}
      {secondsAgo != null && (
        <span style={{ fontSize: "12px", color: "#64748b" }}>
          Last telemetry: <strong>{secondsAgo.toFixed(0)}s ago</strong>
        </span>
      )}
    </div>
  );
}

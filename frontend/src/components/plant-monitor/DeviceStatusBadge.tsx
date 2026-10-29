"use client";

import React from "react";
import { Wifi, WifiOff, Radio, Clock } from "lucide-react";
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
    <div className="flex items-center gap-3 flex-wrap">
      {/* ESP8266 Hardware Status */}
      <div
        className={isOnline ? "pill-forest" : "pill-terracotta"}
        role="status"
        aria-label={`ESP8266 hardware is ${isOnline ? "connected" : "offline"}`}
      >
        <span
          className="w-2 h-2 rounded-full inline-block"
          style={{
            backgroundColor: isOnline ? "var(--forest-600)" : "var(--terracotta-600)",
            boxShadow: isOnline ? "0 0 6px rgba(49, 92, 69, 0.4)" : "none",
          }}
        />
        {isOnline ? (
          <>
            <Wifi size={13} className="text-forest-700" />
            <span>ESP8266 Online</span>
          </>
        ) : (
          <>
            <WifiOff size={13} className="text-terracotta-600" />
            <span>ESP8266 Offline</span>
          </>
        )}
      </div>

      {/* SSE Real-time Stream Status */}
      <div
        className="pill-dew"
        role="status"
        aria-label={`Live telemetry stream is ${sseConnected ? "active" : "reconnecting"}`}
      >
        <Radio size={13} className={sseConnected ? "animate-pulse" : ""} />
        <span>Live SSE:</span>
        <strong className="font-semibold">{sseConnected ? "Connected" : "Syncing..."}</strong>
        {lastEventTime && (
          <span className="mono-tag opacity-75 ml-1">
            {lastEventTime.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
          </span>
        )}
      </div>

      {/* Last Ping Age */}
      {secondsAgo != null && (
        <span className="text-xs flex items-center gap-1.5" style={{ color: "var(--text-muted)" }}>
          <Clock size={12} />
          <span>Last packet:</span>
          <strong className="font-medium" style={{ color: "var(--text-secondary)" }}>
            {secondsAgo < 5 ? "just now" : `${secondsAgo.toFixed(0)}s ago`}
          </strong>
        </span>
      )}
    </div>
  );
}

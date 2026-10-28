"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { PlantTelemetry } from "@/types/plant-monitor";

interface SSEOptions {
  deviceId: string;
  onTelemetry?: (data: PlantTelemetry) => void;
  onPumpStateUpdated?: (data: { confirmed_state: boolean; control_mode: string }) => void;
  onCommandCreated?: (data: any) => void;
}

export function usePlantMonitorSSE({
  deviceId,
  onTelemetry,
  onPumpStateUpdated,
  onCommandCreated,
}: SSEOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEventTime, setLastEventTime] = useState<Date | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const sseUrl = `${apiBase}/devices/${deviceId}/events`;

    try {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const es = new EventSource(sseUrl);
      eventSourceRef.current = es;

      es.onopen = () => {
        setIsConnected(true);
      };

      es.addEventListener("telemetry", (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setLastEventTime(new Date());
          if (onTelemetry && parsed.data) {
            onTelemetry(parsed.data);
          }
        } catch (err) {
          console.error("Failed to parse telemetry SSE event", err);
        }
      });

      es.addEventListener("pump_state_updated", (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setLastEventTime(new Date());
          if (onPumpStateUpdated && parsed.data) {
            onPumpStateUpdated(parsed.data);
          }
        } catch (err) {
          console.error("Failed to parse pump state SSE event", err);
        }
      });

      es.addEventListener("command_created", (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setLastEventTime(new Date());
          if (onCommandCreated && parsed.data) {
            onCommandCreated(parsed.data);
          }
        } catch (err) {
          console.error("Failed to parse command created SSE event", err);
        }
      });

      es.onerror = () => {
        setIsConnected(false);
        es.close();
        // Exponential reconnect attempt after 4 seconds
        if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 4000);
      };
    } catch (e) {
      console.warn("EventSource creation error", e);
      setIsConnected(false);
    }
  }, [deviceId, onTelemetry, onPumpStateUpdated, onCommandCreated]);

  useEffect(() => {
    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return { isConnected, lastEventTime };
}

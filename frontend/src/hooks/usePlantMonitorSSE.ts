"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { PlantTelemetry } from "@/types/plant-monitor";

interface SSEOptions {
  deviceId: string;
  onTelemetry?: (data: PlantTelemetry) => void;
  onPumpStateUpdated?: (data: {
    confirmed_state: boolean;
    control_mode: string;
    timestamp?: string;
    command_id?: string;
    status?: string;
    reason?: string;
  }) => void;
  onCommandCreated?: (data: unknown) => void;
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
  const callbacks = useRef({
    onTelemetry,
    onPumpStateUpdated,
    onCommandCreated,
  });

  useEffect(() => {
    callbacks.current = { onTelemetry, onPumpStateUpdated, onCommandCreated };
  }, [onTelemetry, onPumpStateUpdated, onCommandCreated]);
  const connectRef = useRef<() => void>(() => {});

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    const apiBase =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
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
          if (parsed.device_id === deviceId && parsed.data) {
            callbacks.current.onTelemetry?.(parsed.data);
          }
        } catch (err) {
          console.error("Failed to parse telemetry SSE event", err);
        }
      });

      es.addEventListener("pump_state_updated", (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setLastEventTime(new Date());
          if (parsed.device_id === deviceId && parsed.data) {
            callbacks.current.onPumpStateUpdated?.(parsed.data);
          }
        } catch (err) {
          console.error("Failed to parse pump state SSE event", err);
        }
      });

      es.addEventListener("command_created", (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setLastEventTime(new Date());
          if (parsed.device_id === deviceId && parsed.data) {
            callbacks.current.onCommandCreated?.(parsed.data);
          }
        } catch (err) {
          console.error("Failed to parse command created SSE event", err);
        }
      });

      es.onerror = () => {
        setIsConnected(false);
        es.close();
        // Retry after four seconds; REST polling covers disconnections.
        if (reconnectTimeoutRef.current)
          clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = setTimeout(() => {
          connectRef.current();
        }, 4000);
      };
    } catch (e) {
      console.warn("EventSource creation error", e);
    }
  }, [deviceId]);

  useEffect(() => {
    connectRef.current = connect;
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

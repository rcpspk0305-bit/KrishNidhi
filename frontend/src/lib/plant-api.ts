import axios from "axios";
import {
  PlantTelemetry,
  PlantDeviceStatus,
  PlantProfile,
  PlantAlert,
  PlantAnalytics,
  PlantRecommendation,
  PumpEvent,
} from "@/types/plant-monitor";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/backend/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 8000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const plantApi = {
  // Device
  getDevice: async (deviceId: string) => {
    const res = await apiClient.get(`/devices/${deviceId}`);
    return res.data;
  },

  getDeviceStatus: async (deviceId: string): Promise<PlantDeviceStatus> => {
    const res = await apiClient.get(`/devices/${deviceId}/status`);
    return res.data;
  },

  getPlantProfile: async (deviceId: string): Promise<PlantProfile> => {
    const res = await apiClient.get(`/devices/${deviceId}/profile`);
    return res.data;
  },

  updatePlantProfile: async (deviceId: string, profile: Partial<PlantProfile>): Promise<PlantProfile> => {
    const res = await apiClient.put(`/devices/${deviceId}/profile`, profile);
    return res.data;
  },

  // Telemetry
  getLatestTelemetry: async (deviceId: string): Promise<PlantTelemetry> => {
    const res = await apiClient.get(`/devices/${deviceId}/telemetry/latest`);
    return res.data;
  },

  getTelemetryHistory: async (deviceId: string, hours = 24, limit = 100): Promise<PlantTelemetry[]> => {
    const res = await apiClient.get(`/devices/${deviceId}/telemetry/history`, {
      params: { hours, limit },
    });
    return res.data.readings || [];
  },

  // Pump Control
  requestPumpControl: async (deviceId: string, action: "SET_PUMP" | "SET_MODE", value: boolean | string) => {
    const res = await apiClient.post(`/devices/${deviceId}/pump`, {
      action,
      value,
      ttl_seconds: 60,
    });
    return res.data;
  },

  getPumpHistory: async (deviceId: string, limit = 50): Promise<PumpEvent[]> => {
    const res = await apiClient.get(`/devices/${deviceId}/pump/history`, {
      params: { limit },
    });
    return res.data || [];
  },

  // Alerts
  getAlerts: async (deviceId: string, unacknowledgedOnly = false): Promise<PlantAlert[]> => {
    const res = await apiClient.get(`/devices/${deviceId}/alerts`, {
      params: { unacknowledged_only: unacknowledgedOnly },
    });
    return res.data;
  },

  acknowledgeAlert: async (alertId: number): Promise<PlantAlert> => {
    const res = await apiClient.patch(`/alerts/${alertId}/acknowledge`);
    return res.data;
  },

  // Analytics & Recommendations
  getAnalytics: async (deviceId: string, hours = 24): Promise<PlantAnalytics> => {
    const res = await apiClient.get(`/devices/${deviceId}/analytics`, {
      params: { hours },
    });
    return res.data;
  },

  getRecommendations: async (deviceId: string, language: "en" | "te" | "hi" = "en"): Promise<PlantRecommendation> => {
    const res = await apiClient.get(`/devices/${deviceId}/recommendations`, { params: { language } });
    return res.data;
  },

  // Hardware Simulator Helper (Sends simulated telemetry to backend on behalf of virtual device)
  simulateTelemetry: async (deviceId: string, payload: {
    temperature: number;
    humidity: number;
    soil_moisture: number;
    soil_raw: number;
    motion_detected: boolean;
    pump_on: boolean;
    control_mode: string;
  }) => {
    const res = await apiClient.post(`/devices/${deviceId}/telemetry`, payload, {
      headers: {
        "X-Device-Key": "default_secret_key_123",
      },
    });
    return res.data;
  },

  // Hardware Simulator Helper to Acknowledge Commands as the virtual ESP8266
  simulateAckCommand: async (deviceId: string, commandId: string, confirmedState: boolean, status = "APPLIED") => {
    const res = await apiClient.post(`/devices/${deviceId}/commands/${commandId}/ack`, {
      status,
      confirmed_state: confirmedState,
      reason: "Simulated hardware relay actuation confirmed",
    }, {
      headers: {
        "X-Device-Key": "default_secret_key_123",
      },
    });
    return res.data;
  },
};

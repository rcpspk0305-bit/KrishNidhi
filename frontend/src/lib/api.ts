import axios from "axios";
import { DashboardResponse } from "@/types/dashboard";

const API_BASE = "http://localhost:8000";

export const getDashboardWindow = async (windowName: string): Promise<DashboardResponse> => {
  const response = await axios.get(`${API_BASE}/dashboard/windows/${windowName}`);
  return response.data;
};

export const getLiveIoTData = async () => {
  const response = await axios.get(`${API_BASE}/iot/live`);
  return response.data;
};

export const getIoTStatus = async () => {
  const response = await axios.get(`${API_BASE}/iot/status`);
  return response.data;
};

export const postIoTTelemetry = async (payload: Record<string, any>) => {
  const response = await axios.post(`${API_BASE}/iot/telemetry`, payload);
  return response.data;
};

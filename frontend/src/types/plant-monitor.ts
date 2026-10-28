export interface PlantTelemetry {
  id: number;
  device_id: string;
  timestamp: string;
  temperature: number | null;
  humidity: number | null;
  soil_moisture: number | null;
  soil_raw: number | null;
  motion_detected: boolean;
  pump_on: boolean;
  control_mode: "AUTO" | "MANUAL" | "OFF";
}

export interface PlantDeviceStatus {
  device_id: string;
  status: "online" | "offline" | "fault";
  online: boolean;
  control_mode: "AUTO" | "MANUAL" | "OFF";
  pump_state: boolean;
  last_seen: string | null;
  seconds_since_last_seen: number | null;
  sensor_fault: boolean;
  active_alerts_count: number;
  last_watering_time?: string | null;
  pump_runtime_seconds?: number | null;
}

export interface PlantProfile {
  device_id: string;
  plant_name: string;
  plant_type: string;
  preferred_temp_min: number;
  preferred_temp_max: number;
  preferred_humidity_min: number;
  preferred_humidity_max: number;
  preferred_moisture_min: number;
  preferred_moisture_max: number;
}

export interface PlantAlert {
  id: number;
  device_id: string;
  type: string;
  severity: "info" | "low" | "medium" | "high" | "critical";
  message: string;
  acknowledged: boolean;
  timestamp: string;
}

export interface PlantAnalytics {
  device_id: string;
  window_hours: number;
  metrics: {
    avg_temperature: number | null;
    min_temperature: number | null;
    max_temperature: number | null;
    avg_humidity: number | null;
    avg_soil_moisture: number | null;
    min_soil_moisture: number | null;
    current_vpd_kpa: number | null;
    watering_count_24h: number;
    total_watering_seconds_24h: number;
    dry_down_rate_pct_per_hr: number | null;
  };
  status_summary: string;
}

export interface PlantRecommendation {
  device_id: string;
  plant_name: string;
  health_score: number;
  status: "Thriving" | "Optimal" | "Needs Attention" | "Needs Water" | "Over-watered" | "Critical Alert" | string;
  health_status?: string;
  severity: "low" | "medium" | "high";
  reason?: string;
  recommendation?: string;
  environmental_condition?: string;
  moisture_assessment?: string;
  temperature_assessment?: string;
  humidity_assessment?: string;
  recommended_actions?: string[];
  observations: string[];
  recommendations: string[];
  ai_explanation?: string | null;
  confidence: number;
  limitations: string;
}

export interface PumpEvent {
  id: number;
  device_id: string;
  requested_state: boolean;
  confirmed_state: boolean;
  source: string;
  control_mode: string;
  reason: string | null;
  timestamp: string;
}

export interface CommandAckResult {
  command_id: string;
  status: string;
  confirmed_state: boolean | null;
  message: string;
}

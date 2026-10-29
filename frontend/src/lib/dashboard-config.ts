import { 
  Thermometer, 
  Droplets, 
  FlaskConical, 
  CloudRain, 
  Activity,
  LucideIcon
} from "lucide-react";

export const summaryTabs = [
  { id: "alerts", label: "Alerts", hint: "AI notification history" },
  { id: "predict", label: "Predictions", hint: "Forecast models" },
];

export const metricTabs: { 
  id: string; 
  label: string; 
  hint: string; 
  unit: string; 
  optimal: [number, number]; 
  rangeLabel: string; 
  valueKey: "temperature" | "humidity" | "ph" | "tds" | "rainfall" | "NPK";
  icon: LucideIcon;
}[] = [
  {
    id: "temperature",
    label: "Temp",
    hint: "Air temperature in Celsius",
    unit: "°C",
    optimal: [22, 28],
    rangeLabel: "22-28°C",
    valueKey: "temperature",
    icon: Thermometer
  },
  {
    id: "humidity",
    label: "Moisture",
    hint: "Relative air humidity",
    unit: "%",
    optimal: [30, 50],
    rangeLabel: "30-50%",
    valueKey: "humidity",
    icon: Droplets
  },
  {
    id: "tds",
    label: "Water TDS",
    hint: "Total dissolved solids",
    unit: "ppm",
    optimal: [100, 250],
    rangeLabel: "100-250",
    valueKey: "tds",
    icon: Activity
  },
  {
    id: "ph",
    label: "Soil pH",
    hint: "Soil acidity levels",
    unit: "pH",
    optimal: [6.0, 7.5],
    rangeLabel: "6.0-7.5",
    valueKey: "ph",
    icon: FlaskConical
  },
  {
    id: "rainfall",
    label: "Rain",
    hint: "Precipitation levels",
    unit: "mm",
    optimal: [0, 100],
    rangeLabel: "0-100mm",
    valueKey: "rainfall",
    icon: CloudRain
  }
];

export interface DashboardCurrentMetrics {
  temperature: number;
  humidity: number;
  tds: number;
  ph: number;
  [key: string]: unknown;
}

export const sensorSummaries = (current: DashboardCurrentMetrics) => [
  { label: "Temperature", value: current.temperature.toFixed(1), unit: "°C", hint: "Stable" },
  { label: "Humidity", value: current.humidity.toFixed(1), unit: "%", hint: "Optimal" },
  { label: "Water TDS", value: current.tds.toFixed(0), unit: "", hint: "Safe" },
  { label: "Soil pH", value: current.ph.toFixed(1), unit: "pH", hint: "Neutral" },
];

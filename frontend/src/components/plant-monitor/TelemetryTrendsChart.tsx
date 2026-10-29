"use client";

import { useLanguage } from "@/components/LanguageProvider";
import React, { useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { TrendingUp, RefreshCw } from "lucide-react";
import { PlantTelemetry } from "@/types/plant-monitor";

interface Props {
  data: PlantTelemetry[];
  onRefresh?: () => void;
  loading?: boolean;
}

export default function TelemetryTrendsChart({
  data,
  onRefresh,
  loading,
}: Props) {
  const { t, intlLocale } = useLanguage();

  const [selectedMetric, setSelectedMetric] = useState<
    "all" | "soil" | "temp" | "humidity" | "pump"
  >("all");

  const formattedData = data.map((d) => {
    const timeStr = d.timestamp
      ? new Date(d.timestamp).toLocaleTimeString(intlLocale, {
          hour: "2-digit",
          minute: "2-digit",
        })
      : "";
    return {
      time: timeStr,
      temperature:
        d.temperature != null ? Number(d.temperature.toFixed(1)) : null,
      humidity: d.humidity != null ? Number(d.humidity.toFixed(0)) : null,
      soil_moisture:
        d.soil_moisture != null ? Number(d.soil_moisture.toFixed(0)) : null,
      pump_active: d.pump_on ? 100 : 0,
    };
  });

  return (
    <div className="botanical-card p-6 flex flex-col gap-4 bg-white">
      {/* Chart Header & Controls */}
      <div className="flex justify-between items-center flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div
            className="p-2.5 rounded-xl border flex items-center justify-center"
            style={{
              backgroundColor: "var(--forest-50)",
              borderColor: "var(--forest-100)",
              color: "var(--forest-700)",
            }}
          >
            <TrendingUp size={20} />
          </div>
          <div>
            <h3 className="title-md font-serif text-lg">
              {t("Environmental Telemetry Trends")}
            </h3>
            <span
              className="mono-tag block"
              style={{ color: "var(--text-muted)" }}
            >
              {t("Chronological Microclimate Log from NodeMCU")}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Metric Filter Tabs */}
          <div
            className="flex p-1 rounded-xl border"
            style={{
              backgroundColor: "var(--bg-subtle)",
              borderColor: "var(--border-subtle)",
            }}
          >
            {(["all", "soil", "temp", "humidity", "pump"] as const).map(
              (filter) => {
                const isSelected = selectedMetric === filter;
                return (
                  <button
                    key={filter}
                    type="button"
                    onClick={() => setSelectedMetric(filter)}
                    className="py-1 px-2.5 text-xs font-semibold rounded-lg transition-all uppercase"
                    style={{
                      backgroundColor: isSelected ? "#ffffff" : "transparent",
                      color: isSelected
                        ? "var(--forest-800)"
                        : "var(--text-muted)",
                      boxShadow: isSelected ? "var(--shadow-sm)" : "none",
                      border: isSelected
                        ? "1px solid var(--border-default)"
                        : "1px solid transparent",
                      cursor: "pointer",
                    }}
                  >
                    {t(
                      {
                        all: "All",
                        soil: "Soil",
                        temp: "Temperature",
                        humidity: "Humidity",
                        pump: "Pump",
                      }[filter],
                    )}
                  </button>
                );
              },
            )}
          </div>

          {onRefresh && (
            <button
              type="button"
              onClick={onRefresh}
              disabled={loading}
              className="btn-secondary text-xs py-1.5 px-3"
            >
              <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
              <span>{t(loading ? "Syncing..." : "Sync")}</span>
            </button>
          )}
        </div>
      </div>

      {/* Chart Canvas */}
      {formattedData.length === 0 ? (
        <div
          className="h-64 flex items-center justify-center rounded-xl border text-xs"
          style={{
            backgroundColor: "var(--bg-subtle)",
            borderColor: "var(--border-subtle)",
            color: "var(--text-muted)",
          }}
        >
          {t(
            "No historical telemetry points found. Telemetry will plot here once received from ESP8266.",
          )}
        </div>
      ) : (
        <div className="w-full h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={formattedData}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(25, 42, 33, 0.08)"
              />
              <XAxis
                dataKey="time"
                stroke="var(--text-muted)"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: "rgba(25, 42, 33, 0.12)" }}
              />
              <YAxis
                stroke="var(--text-muted)"
                fontSize={11}
                domain={[0, 100]}
                tickLine={false}
                axisLine={{ stroke: "rgba(25, 42, 33, 0.12)" }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#ffffff",
                  borderColor: "rgba(25, 42, 33, 0.14)",
                  borderRadius: "12px",
                  boxShadow: "0 4px 16px rgba(25, 42, 33, 0.08)",
                  fontSize: "12px",
                  color: "var(--text-primary)",
                  fontFamily: "var(--font-sans)",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />

              {(selectedMetric === "all" || selectedMetric === "soil") && (
                <Line
                  type="monotone"
                  dataKey="soil_moisture"
                  name={t("Soil Moisture (%)")}
                  stroke="#254836"
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 5 }}
                />
              )}
              {(selectedMetric === "all" || selectedMetric === "temp") && (
                <Line
                  type="monotone"
                  dataKey="temperature"
                  name={t("Temperature (°C)")}
                  stroke="#bd5134"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              )}
              {(selectedMetric === "all" || selectedMetric === "humidity") && (
                <Line
                  type="monotone"
                  dataKey="humidity"
                  name={t("Humidity (% RH)")}
                  stroke="#31778c"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              )}
              {(selectedMetric === "all" || selectedMetric === "pump") && (
                <Line
                  type="stepAfter"
                  dataKey="pump_active"
                  name={t("Pump Relay Active (0/100%)")}
                  stroke="#b07c1e"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

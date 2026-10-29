"use client";

import { useLanguage } from "@/components/LanguageProvider";
import React from "react";
import { Thermometer, Droplets, Wind, Radio } from "lucide-react";
import { PlantTelemetry } from "@/types/plant-monitor";

interface Props {
  telemetry: PlantTelemetry | null;
  loading: boolean;
}

export default function SensorCardsGrid({ telemetry, loading }: Props) {
  const { t } = useLanguage();

  const temp = telemetry?.temperature ?? null;
  const humidity = telemetry?.humidity ?? null;
  const soilPct = telemetry?.soil_moisture ?? null;
  const soilRaw = telemetry?.soil_raw ?? null;
  const motion = telemetry?.motion_detected ?? false;

  const isTempOptimal = temp != null && temp >= 18 && temp <= 30;
  const isHumidityOptimal =
    humidity != null && humidity >= 50 && humidity <= 75;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. TEMPERATURE CARD */}
      <div className="botanical-card p-5 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-3">
            <div
              className="flex items-center gap-2 text-xs font-semibold"
              style={{ color: "var(--text-secondary)" }}
            >
              <div
                className="p-1.5 rounded-lg"
                style={{
                  backgroundColor: "var(--terracotta-100)",
                  color: "var(--terracotta-700)",
                }}
              >
                <Thermometer size={16} />
              </div>
              <span>{t("Ambient Temp (DHT11)")}</span>
            </div>
            <span className="mono-tag" style={{ color: "var(--text-muted)" }}>
              GPIO 12 / D6
            </span>
          </div>

          <div className="flex items-baseline gap-1 my-2">
            <span
              className="metric-num text-4xl font-serif"
              style={{ color: "var(--text-primary)" }}
            >
              {loading ? "--" : temp != null ? temp.toFixed(1) : t("N/A")}
            </span>
            <span
              className="text-sm font-semibold"
              style={{ color: "var(--text-muted)" }}
            >
              °C
            </span>
          </div>
        </div>

        <div
          className="pt-3 border-t text-xs"
          style={{
            borderColor: "var(--border-subtle)",
            color: "var(--text-muted)",
          }}
        >
          <div className="flex items-center justify-between">
            <span>{t("Target: 18.0°C – 30.0°C")}</span>
            <span
              className="w-2 h-2 rounded-full"
              style={{
                backgroundColor: isTempOptimal
                  ? "var(--forest-600)"
                  : "var(--gold-600)",
              }}
            />
          </div>
          <p
            className="mt-1 font-medium"
            style={{
              color: isTempOptimal ? "var(--forest-700)" : "var(--gold-700)",
            }}
          >
            {t(
              temp != null
                ? isTempOptimal
                  ? "Optimal Microclimate"
                  : "Temperature Variance"
                : "Pending read",
            )}
          </p>
        </div>
      </div>

      {/* 2. RELATIVE HUMIDITY CARD */}
      <div className="botanical-card p-5 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-3">
            <div
              className="flex items-center gap-2 text-xs font-semibold"
              style={{ color: "var(--text-secondary)" }}
            >
              <div
                className="p-1.5 rounded-lg"
                style={{
                  backgroundColor: "var(--dew-100)",
                  color: "var(--dew-700)",
                }}
              >
                <Wind size={16} />
              </div>
              <span>{t("Relative Humidity")}</span>
            </div>
            <span className="mono-tag" style={{ color: "var(--text-muted)" }}>
              1-Wire Digital
            </span>
          </div>

          <div className="flex items-baseline gap-1 my-2">
            <span
              className="metric-num text-4xl font-serif"
              style={{ color: "var(--text-primary)" }}
            >
              {loading
                ? "--"
                : humidity != null
                  ? humidity.toFixed(0)
                  : t("N/A")}
            </span>
            <span
              className="text-sm font-semibold"
              style={{ color: "var(--text-muted)" }}
            >
              % RH
            </span>
          </div>
        </div>

        <div
          className="pt-3 border-t text-xs"
          style={{
            borderColor: "var(--border-subtle)",
            color: "var(--text-muted)",
          }}
        >
          <div className="flex items-center justify-between">
            <span>{t("Target: 50% – 75% RH")}</span>
            <span
              className="w-2 h-2 rounded-full"
              style={{
                backgroundColor: isHumidityOptimal
                  ? "var(--forest-600)"
                  : "var(--dew-600)",
              }}
            />
          </div>
          <p
            className="mt-1 font-medium"
            style={{
              color: isHumidityOptimal ? "var(--forest-700)" : "var(--dew-700)",
            }}
          >
            {t(
              humidity != null
                ? isHumidityOptimal
                  ? "Comfort Zone"
                  : "Sub-optimal VPD"
                : "Pending read",
            )}
          </p>
        </div>
      </div>

      {/* 3. SOIL MOISTURE CARD */}
      <div className="botanical-card p-5 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-3">
            <div
              className="flex items-center gap-2 text-xs font-semibold"
              style={{ color: "var(--text-secondary)" }}
            >
              <div
                className="p-1.5 rounded-lg"
                style={{
                  backgroundColor: "var(--forest-100)",
                  color: "var(--forest-700)",
                }}
              >
                <Droplets size={16} />
              </div>
              <span>{t("Soil Moisture (LM393)")}</span>
            </div>
            <span className="mono-tag" style={{ color: "var(--text-muted)" }}>
              ADC 0 / A0
            </span>
          </div>

          <div className="flex items-baseline gap-2 my-2">
            <span
              className="metric-num text-4xl font-serif"
              style={{
                color:
                  soilPct != null && soilPct < 30
                    ? "var(--terracotta-600)"
                    : "var(--forest-800)",
              }}
            >
              {loading ? "--" : soilPct != null ? soilPct.toFixed(0) : t("N/A")}
            </span>
            <span
              className="text-sm font-semibold"
              style={{ color: "var(--text-muted)" }}
            >
              %
            </span>
            {soilRaw != null && (
              <span
                className="mono-tag ml-auto"
                style={{ color: "var(--text-muted)" }}
              >
                {t("Raw:")}
                {soilRaw}
              </span>
            )}
          </div>

          {/* Calibrated Moisture Progress Bar */}
          <div
            className="w-full h-2 rounded-full overflow-hidden my-2"
            style={{ backgroundColor: "var(--bg-subtle)" }}
          >
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{
                width: `${Math.min(100, Math.max(0, soilPct ?? 0))}%`,
                backgroundColor:
                  soilPct != null && soilPct < 30
                    ? "var(--terracotta-500)"
                    : "var(--forest-600)",
              }}
            />
          </div>
        </div>

        <div
          className="pt-3 border-t text-xs flex justify-between"
          style={{
            borderColor: "var(--border-subtle)",
            color: "var(--text-muted)",
          }}
        >
          <span>{t("Auto-on: <30%")}</span>
          <span>{t("Target cutoff: 55%")}</span>
        </div>
      </div>

      {/* 4. PIR MOTION DETECTION CARD */}
      <div className="botanical-card p-5 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-3">
            <div
              className="flex items-center gap-2 text-xs font-semibold"
              style={{ color: "var(--text-secondary)" }}
            >
              <div
                className="p-1.5 rounded-lg"
                style={{
                  backgroundColor: motion
                    ? "var(--gold-100)"
                    : "var(--bg-subtle)",
                  color: motion ? "var(--gold-700)" : "var(--text-muted)",
                }}
              >
                <Radio size={16} />
              </div>
              <span>{t("PIR Motion Sensor")}</span>
            </div>
            <span className="mono-tag" style={{ color: "var(--text-muted)" }}>
              GPIO 13 / D7
            </span>
          </div>

          <div className="flex items-center gap-2.5 my-3">
            <span
              className="w-3 h-3 rounded-full transition-all"
              style={{
                backgroundColor: motion
                  ? "var(--gold-600)"
                  : "var(--text-muted)",
                boxShadow: motion ? "0 0 8px rgba(176, 124, 30, 0.4)" : "none",
              }}
            />
            <span
              className="font-serif font-semibold text-xl"
              style={{
                color: motion ? "var(--gold-700)" : "var(--text-secondary)",
              }}
            >
              {t(motion ? "Motion Detected" : "Field Clear")}
            </span>
          </div>
        </div>

        <div
          className="pt-3 border-t text-xs"
          style={{
            borderColor: "var(--border-subtle)",
            color: "var(--text-muted)",
          }}
        >
          <span>
            {t("Passive infrared detection around planter perimeter.")}
          </span>
        </div>
      </div>
    </div>
  );
}

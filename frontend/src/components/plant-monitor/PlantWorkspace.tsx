"use client";

import { useLanguage } from "@/components/LanguageProvider";
import React, { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import { RefreshCw, Landmark, Home, Clock } from "lucide-react";
import PlantHealthHero from "./PlantHealthHero";
import SensorCardsGrid from "./SensorCardsGrid";
import PumpControlWidget from "./PumpControlWidget";
import TelemetryTrendsChart from "./TelemetryTrendsChart";
import AIRecommendationsCard from "./AIRecommendationsCard";
import DeviceStatusBadge from "./DeviceStatusBadge";
import AlertsDrawer from "./AlertsDrawer";
import HardwareSimulatorPanel from "./HardwareSimulatorPanel";

import { plantApi } from "@/lib/plant-api";
import { usePlantMonitorSSE } from "@/hooks/usePlantMonitorSSE";
import { isFresh, mergeHistory } from "@/lib/plant-state";
import {
  PlantTelemetry,
  PlantDeviceStatus,
  PlantRecommendation,
  PlantAlert,
} from "@/types/plant-monitor";

interface Props {
  initialDeviceId?: string;
}

export default function PlantWorkspace({
  initialDeviceId = "plant-01",
}: Props) {
  const { t, locale } = useLanguage();

  const [deviceId, setDeviceId] = useState<string>(initialDeviceId);

  const [telemetry, setTelemetry] = useState<PlantTelemetry | null>(null);
  const [history, setHistory] = useState<PlantTelemetry[]>([]);
  const [deviceStatus, setDeviceStatus] = useState<PlantDeviceStatus | null>(
    null,
  );
  const [recommendation, setRecommendation] =
    useState<PlantRecommendation | null>(null);
  const [recommendationRevision, setRecommendationRevision] = useState(0);
  const [alerts, setAlerts] = useState<PlantAlert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [syncing, setSyncing] = useState<boolean>(false);
  const [now, setNow] = useState<number>(0);

  // Keep now updated every 5 seconds for accurate stale data detection
  useEffect(() => {
    const initial = setTimeout(() => setNow(Date.now()), 0);
    const timer = setInterval(() => setNow(Date.now()), 5000);
    return () => {
      clearTimeout(initial);
      clearInterval(timer);
    };
  }, []);

  const dataIsFresh = useMemo(() => {
    return isFresh(telemetry?.timestamp, now, 35000);
  }, [telemetry?.timestamp, now]);

  // Load all initial data from REST API
  const refreshAllData = useCallback(async () => {
    setSyncing(true);
    try {
      const [latestRes, historyRes, statusRes, alertsRes] =
        await Promise.allSettled([
          plantApi.getLatestTelemetry(deviceId),
          plantApi.getTelemetryHistory(deviceId, 24, 60),
          plantApi.getDeviceStatus(deviceId),
          plantApi.getAlerts(deviceId),
        ]);

      if (latestRes.status === "fulfilled") setTelemetry(latestRes.value);
      if (historyRes.status === "fulfilled") {
        setHistory((prev) => mergeHistory(historyRes.value, prev));
      }
      if (statusRes.status === "fulfilled") setDeviceStatus(statusRes.value);
      if (alertsRes.status === "fulfilled") setAlerts(alertsRes.value);
    } catch (err) {
      console.warn("Telemetry refresh notice:", err);
    } finally {
      setLoading(false);
      setSyncing(false);
    }
  }, [deviceId]);

  const refreshWorkspace = useCallback(async () => {
    await refreshAllData();
    setRecommendationRevision((revision) => revision + 1);
  }, [refreshAllData]);

  useEffect(() => {
    let active = true;
    const fetchRecommendations = async () => {
      try {
        const result = await plantApi.getRecommendations(deviceId, locale);
        if (active) setRecommendation(result);
      } catch {
        /* Keep sensor polling independent of optional AI explanations. */
      }
    };
    const initial = setTimeout(() => void fetchRecommendations(), 0);
    const interval = setInterval(() => void fetchRecommendations(), 60_000);
    return () => {
      active = false;
      clearTimeout(initial);
      clearInterval(interval);
    };
  }, [deviceId, locale, recommendationRevision]);

  useEffect(() => {
    const initial = setTimeout(() => void refreshAllData(), 0);
    // Fallback polling every 15s in case SSE is interrupted
    const interval = setInterval(refreshAllData, 15000);
    return () => {
      clearTimeout(initial);
      clearInterval(interval);
    };
  }, [refreshAllData]);

  // Connect to live Server-Sent Events (SSE)
  const { isConnected: sseConnected, lastEventTime } = usePlantMonitorSSE({
    deviceId,
    onTelemetry: (newTelemetry) => {
      setTelemetry(newTelemetry);
      setHistory((prev) => mergeHistory(prev, [newTelemetry]));
      setDeviceStatus((prev) =>
        prev
          ? {
              ...prev,
              online: true,
              pump_state: newTelemetry.pump_on,
              control_mode: newTelemetry.control_mode,
              last_seen: newTelemetry.timestamp,
              seconds_since_last_seen: 0,
            }
          : null,
      );
    },
    onPumpStateUpdated: (data) => {
      setDeviceStatus((prev) =>
        prev
          ? {
              ...prev,
              pump_state: data.confirmed_state,
              control_mode:
                data.control_mode as PlantDeviceStatus["control_mode"],
              last_watering_time: data.confirmed_state
                ? data.timestamp || new Date().toISOString()
                : prev.last_watering_time,
            }
          : null,
      );
    },
    onCommandCreated: () => {
      // Command registered in server queue
    },
  });

  return (
    <main
      className="section bg-canvas text-forest-900 font-sans"
      style={{ backgroundColor: "var(--bg-canvas)" }}
    >
      <div className="page-shell flex flex-col gap-6">
        {/* Navigation & Status Header */}
        <header
          className="flex justify-between items-center flex-wrap gap-4 pb-4 border-b"
          style={{ borderColor: "var(--border-subtle)" }}
        >
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="btn-secondary py-2 px-3 text-xs"
              aria-label={t("Return to Portal Homepage")}
            >
              <Home size={15} />
              <span>{t("Portal")}</span>
            </Link>

            <div>
              <span
                className="mono-tag font-bold uppercase tracking-wider"
                style={{ color: "var(--forest-600)" }}
              >
                {t("KrishiNidhi Botanical Console")}
              </span>
              <h2
                className="title-md font-serif text-xl"
                style={{ color: "var(--forest-900)" }}
              >
                {t("Smart Plant & Irrigation Station")}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <div
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border bg-white shadow-xs"
              style={{ borderColor: "var(--border-subtle)" }}
            >
              <label
                htmlFor="device-select"
                className="text-[11px] font-semibold tracking-wider uppercase"
                style={{ color: "var(--text-muted)" }}
              >
                {t("Device:")}
              </label>
              <select
                id="device-select"
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
                className="text-xs font-semibold bg-transparent cursor-pointer outline-none"
                style={{ color: "var(--forest-900)" }}
              >
                <option value="plant-01">plant-01 (ESP8266 Hardware)</option>
                <option value="esp8266-plant-01">esp8266-plant-01 (Indoor Planter)</option>
              </select>
            </div>

            <DeviceStatusBadge
              status={deviceStatus}
              sseConnected={sseConnected}
              lastEventTime={lastEventTime}
            />


            <button
              type="button"
              onClick={refreshWorkspace}
              disabled={syncing}
              className="btn-secondary text-xs py-2 px-3.5"
              aria-label={t("Synchronize plant data")}
            >
              <RefreshCw
                size={13}
                className={
                  syncing ? "animate-spin text-forest-700" : "text-forest-700"
                }
              />
              <span>{t(syncing ? "Syncing..." : "Sync")}</span>
            </button>

            <Link
              href="/scheme-finder"
              className="btn-secondary text-xs py-2 px-3"
            >
              <Landmark size={14} className="text-forest-700" />
              <span>{t("Scheme Finder")}</span>
            </Link>
          </div>
        </header>

        {/* Stale Telemetry Warning Banner */}
        {telemetry && !dataIsFresh && (
          <div
            className="p-3.5 rounded-xl border flex items-center justify-between text-xs"
            style={{
              backgroundColor: "var(--gold-100)",
              borderColor: "rgba(176, 124, 30, 0.25)",
              color: "var(--gold-700)",
            }}
          >
            <div className="flex items-center gap-2 font-medium">
              <Clock size={15} />
              <span>
                {t(
                  "Telemetry is currently stale (>35s without packet). Displaying last known sensor readings.",
                )}
              </span>
            </div>
            <button
              type="button"
              onClick={refreshWorkspace}
              className="underline font-semibold ml-2"
            >
              {t("Retry Sync")}
            </button>
          </div>
        )}

        {/* Active System Alerts Drawer */}
        <AlertsDrawer alerts={alerts} onAlertAcknowledged={refreshWorkspace} />

        {/* 1. HERO SECTION: Specimen Profile, Health Index, NodeMCU Link, Ribbon */}
        <PlantHealthHero
          recommendation={recommendation}
          latest={telemetry}
          loading={loading}
          deviceStatus={deviceStatus}
        />

        {/* 2. SENSOR MONITORING: 4 Metric Cards */}
        <SensorCardsGrid telemetry={telemetry} loading={loading} />

        {/* 3. PUMP CONTROL & AGRONOMIC INTELLIGENCE GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Water Pump Actuator Controller */}
          <PumpControlWidget
            deviceId={deviceId}
            confirmedPumpOn={deviceStatus?.pump_state ?? false}
            currentMode={deviceStatus?.control_mode ?? "AUTO"}
            onCommandDispatched={refreshWorkspace}
            lastWateringTime={deviceStatus?.last_watering_time}
            pumpRuntimeSeconds={deviceStatus?.pump_runtime_seconds}
          />

          {/* Plant Health Intelligence & Agronomic Guidance */}
          <AIRecommendationsCard
            recommendation={recommendation}
            loading={loading}
          />
        </div>

        {/* 4. HISTORICAL SENSOR TRENDS CHART */}
        <TelemetryTrendsChart
          data={history}
          onRefresh={refreshWorkspace}
          loading={syncing}
        />

        {/* 5. VIRTUAL HARDWARE TEST BENCH */}
        <HardwareSimulatorPanel
          deviceId={deviceId}
          confirmedPumpOn={deviceStatus?.pump_state ?? false}
          currentMode={deviceStatus?.control_mode ?? "AUTO"}
          onTelemetryEmitted={refreshWorkspace}
        />

        {/* Footer */}
        <footer
          className="text-center text-xs py-6 border-t mt-4"
          style={{
            borderColor: "var(--border-subtle)",
            color: "var(--text-muted)",
          }}
        >
          <p
            className="font-serif italic text-sm mb-1"
            style={{ color: "var(--text-secondary)" }}
          >
            {t(
              "“KrishiNidhi — Mindful environmental stewardship and botanical vitality.”",
            )}
          </p>
          <p className="mono-tag text-[11px]">
            {t(
              "ESP8266 NodeMCU ESP-12E Architecture • Computer Science & Engineering Final Project • Warm Editorial Botanical Edition",
            )}
          </p>
        </footer>
      </div>
    </main>
  );
}

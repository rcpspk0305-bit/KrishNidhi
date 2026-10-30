"use client";

import { useLanguage } from "@/components/LanguageProvider";
import React, { useState } from "react";
import { Power, ShieldAlert, CheckCircle2, Clock, Loader2 } from "lucide-react";
import { plantApi } from "@/lib/plant-api";

interface Props {
  deviceId: string;
  confirmedPumpOn: boolean;
  currentMode: "AUTO" | "MANUAL" | "OFF";
  onCommandDispatched?: () => void;
  lastWateringTime?: string | null;
  pumpRuntimeSeconds?: number | null;
}

export default function PumpControlWidget({
  deviceId,
  confirmedPumpOn,
  currentMode,
  onCommandDispatched,
  lastWateringTime,
  pumpRuntimeSeconds,
}: Props) {
  const { t, intlLocale } = useLanguage();
  const sensorOnly = process.env.NEXT_PUBLIC_SENSOR_ONLY === "true";

  const [submitting, setSubmitting] = useState(false);
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleModeChange = async (newMode: "AUTO" | "MANUAL" | "OFF") => {
    if (sensorOnly) return;
    if (newMode === currentMode) return;
    setSubmitting(true);
    setPendingAction(`Switching operating mode to ${newMode}`);
    setErrorMsg(null);
    try {
      await plantApi.requestPumpControl(deviceId, "SET_MODE", newMode);
      if (onCommandDispatched) onCommandDispatched();
    } catch (err: unknown) {
      const errorObj = err as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      setErrorMsg(
        errorObj.response?.data?.detail ||
          errorObj.message ||
          "Failed to switch mode",
      );
    } finally {
      setSubmitting(false);
      setTimeout(() => setPendingAction(null), 3000);
    }
  };

  const handleTogglePump = async () => {
    if (sensorOnly) return;
    if (currentMode !== "MANUAL") {
      setErrorMsg(
        "Manual pump actuation is restricted to MANUAL mode. Please switch modes first.",
      );
      return;
    }
    const targetState = !confirmedPumpOn;
    setSubmitting(true);
    setPendingAction(`Commanding pump relay ${targetState ? "ON" : "OFF"}`);
    setErrorMsg(null);
    try {
      await plantApi.requestPumpControl(deviceId, "SET_PUMP", targetState);
      if (onCommandDispatched) onCommandDispatched();
    } catch (err: unknown) {
      const errorObj = err as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      setErrorMsg(
        errorObj.response?.data?.detail ||
          errorObj.message ||
          "Failed to submit pump command",
      );
    } finally {
      setSubmitting(false);
      setTimeout(() => setPendingAction(null), 3000);
    }
  };

  return (
    <div className="botanical-card p-6 flex flex-col gap-5 bg-white">
      {/* Widget Header */}
      <div className="flex justify-between items-center flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div
            className="p-2.5 rounded-xl border flex items-center justify-center"
            style={{
              backgroundColor: confirmedPumpOn
                ? "var(--terracotta-100)"
                : "var(--bg-subtle)",
              borderColor: confirmedPumpOn
                ? "var(--terracotta-border)"
                : "var(--border-subtle)",
              color: confirmedPumpOn
                ? "var(--terracotta-700)"
                : "var(--text-secondary)",
            }}
          >
            <Power size={20} />
          </div>
          <div>
            <h3 className="title-md font-serif text-lg">
              {t("Irrigation Pump Controller")}
            </h3>
            <span
              className="mono-tag block"
              style={{ color: "var(--text-muted)" }}
            >
              {t("Relay IN: GPIO 14 (D5) • Active-LOW Optocoupled")}
            </span>
          </div>
        </div>

        {/* Confirmed Physical Firmware State Badge */}
        <div className={confirmedPumpOn ? "pill-terracotta" : "pill-forest"}>
          <span
            className="w-2 h-2 rounded-full"
            style={{
              backgroundColor: confirmedPumpOn
                ? "var(--terracotta-600)"
                : "var(--forest-600)",
              boxShadow: confirmedPumpOn
                ? "0 0 8px rgba(189, 81, 52, 0.5)"
                : "none",
            }}
          />
          <span className="font-semibold uppercase tracking-wider text-[11px]">
            {t(
              confirmedPumpOn
                ? "Relay Closed (Irrigating)"
                : "Relay Open (Standby)",
            )}
          </span>
        </div>
      </div>

      {sensorOnly && (
        <p className="p-3 rounded-xl border text-sm" role="status">
          {t("USB sensors connected. Pump control is unavailable; relay held OFF.")}
        </p>
      )}

      {/* Error Message Alert */}
      {errorMsg && (
        <div
          className="p-3 rounded-xl border text-xs flex items-center gap-2"
          style={{
            backgroundColor: "var(--terracotta-50)",
            borderColor: "rgba(189, 81, 52, 0.2)",
            color: "var(--terracotta-700)",
          }}
        >
          <ShieldAlert size={16} className="shrink-0" />
          <span>{t(errorMsg)}</span>
        </div>
      )}

      {/* Pending Command Feedback */}
      {pendingAction && (
        <div
          className="p-3 rounded-xl border text-xs flex items-center gap-2"
          style={{
            backgroundColor: "var(--dew-100)",
            borderColor: "rgba(49, 119, 140, 0.2)",
            color: "var(--dew-700)",
          }}
        >
          <Loader2 size={15} className="animate-spin shrink-0" />
          <span>
            {t(pendingAction)}
            {t("... Awaiting ESP8266 acknowledgment packet.")}
          </span>
        </div>
      )}

      {/* Controls Grid: Mode Selector & Physical Trigger */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
        {/* Operating Control Mode Selector */}
        <div>
          <label
            className="mono-tag font-semibold block mb-2"
            style={{ color: "var(--text-secondary)" }}
          >
            {t("OPERATING MODE")}
          </label>
          <div
            className="flex p-1 rounded-xl border"
            style={{
              backgroundColor: "var(--bg-subtle)",
              borderColor: "var(--border-subtle)",
            }}
          >
            {(["AUTO", "MANUAL", "OFF"] as const).map((m) => {
              const isSelected = currentMode === m;
              return (
                <button
                  key={m}
                  type="button"
                  onClick={() => handleModeChange(m)}
                  disabled={submitting || sensorOnly}
                  className="flex-1 py-2 px-3 text-xs font-semibold rounded-lg transition-all"
                  style={{
                    backgroundColor: isSelected ? "#ffffff" : "transparent",
                    color: isSelected
                      ? "var(--forest-800)"
                      : "var(--text-muted)",
                    boxShadow: isSelected ? "var(--shadow-sm)" : "none",
                    border: isSelected
                      ? "1px solid var(--border-default)"
                      : "1px solid transparent",
                    cursor: submitting || sensorOnly ? "not-allowed" : "pointer",
                  }}
                >
                  {t(m)}
                </button>
              );
            })}
          </div>
        </div>

        {/* Direct Actuator Trigger Button */}
        <div>
          <label
            className="mono-tag font-semibold block mb-2"
            style={{ color: "var(--text-secondary)" }}
          >
            {t("MANUAL RELAY ACTUATION")}
          </label>
          <button
            type="button"
            onClick={handleTogglePump}
            disabled={sensorOnly || submitting || currentMode !== "MANUAL"}
            className={
              confirmedPumpOn ? "btn-terracotta w-full" : "btn-primary w-full"
            }
            style={{
              opacity: sensorOnly || currentMode !== "MANUAL" ? 0.45 : 1,
              cursor:
                !sensorOnly && currentMode === "MANUAL" && !submitting
                  ? "pointer"
                  : "not-allowed",
            }}
          >
            {submitting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Power size={16} />
            )}
            <span>
              {t(
                confirmedPumpOn
                  ? "Turn Off Pump (Manual)"
                  : currentMode === "MANUAL"
                    ? "Actuate Pump (Manual)"
                    : "Active in MANUAL Mode Only",
              )}
            </span>
          </button>
        </div>
      </div>

      {/* Runtime & Telemetry Confirmation Summary */}
      <div
        className="grid grid-cols-3 gap-3 p-3.5 rounded-xl border text-xs"
        style={{
          backgroundColor: "var(--bg-subtle)",
          borderColor: "var(--border-subtle)",
        }}
      >
        <div>
          <span className="block" style={{ color: "var(--text-muted)" }}>
            {t("Last Watering")}
          </span>
          <strong
            className="font-serif text-sm mt-0.5 block"
            style={{ color: "var(--text-primary)" }}
          >
            {t(
              lastWateringTime
                ? new Date(lastWateringTime).toLocaleTimeString(intlLocale, {
                    hour: "2-digit",
                    minute: "2-digit",
                  })
                : "None recorded",
            )}
          </strong>
        </div>

        <div>
          <span className="block" style={{ color: "var(--text-muted)" }}>
            {t("Current Run")}
          </span>
          <strong
            className="font-serif text-sm mt-0.5 block"
            style={{
              color: confirmedPumpOn
                ? "var(--terracotta-600)"
                : "var(--text-primary)",
            }}
          >
            {t(
              confirmedPumpOn
                ? `${pumpRuntimeSeconds || 0}s (Active)`
                : "0s (Standby)",
            )}
          </strong>
        </div>

        <div>
          <span className="block" style={{ color: "var(--text-muted)" }}>
            {t("State Authority")}
          </span>
          <strong
            className="font-serif text-sm mt-0.5 block"
            style={{
              color: confirmedPumpOn
                ? "var(--terracotta-600)"
                : "var(--forest-700)",
            }}
          >
            {t(sensorOnly ? "USB relay OFF" : "Device reported")}
          </strong>
        </div>
      </div>

      {/* Hardware Safety Limits */}
      <div
        className="flex items-center gap-4 flex-wrap pt-3 border-t text-xs"
        style={{
          borderColor: "var(--border-subtle)",
          color: "var(--text-muted)",
        }}
      >
        <span className="flex items-center gap-1.5">
          <Clock size={13} style={{ color: "var(--gold-600)" }} />
          <span>
            {t("Watchdog:")} <strong>{t(sensorOnly ? "Relay held OFF" : "Firmware configured")}</strong>
          </span>
        </span>
        <span className="flex items-center gap-1.5">
          <Clock size={13} style={{ color: "var(--dew-600)" }} />
          <span>
            {t("Cooldown:")} <strong>{t("60s safety lockout")}</strong>
          </span>
        </span>
        <span className="flex items-center gap-1.5">
          <CheckCircle2 size={13} style={{ color: "var(--forest-600)" }} />
          <span>
            {t("Default:")} <strong>{t("Safe Boot OFF")}</strong>
          </span>
        </span>
      </div>
    </div>
  );
}

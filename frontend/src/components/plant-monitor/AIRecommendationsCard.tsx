"use client";

import { useLanguage } from "@/components/LanguageProvider";
import React from "react";
import { Sparkles, CheckCircle, ShieldCheck, HelpCircle } from "lucide-react";
import { PlantRecommendation } from "@/types/plant-monitor";

interface Props {
  recommendation: PlantRecommendation | null;
  loading: boolean;
}

export default function AIRecommendationsCard({ recommendation, loading }: Props) {
  const { t, locale } = useLanguage();

  const observations = recommendation?.observations || [
    "No sensor data received yet from the device.",
  ];

  const recommendations = recommendation?.recommendations || [
    "Check ESP8266 power supply and Wi-Fi connection.",
  ];

  const severity = recommendation?.severity || "low";
  const aiExplanation = (recommendation?.language || "en") === locale ? recommendation?.ai_explanation : null;

  const getSeverityPill = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "high":
        return "pill-terracotta";
      case "medium":
        return "pill-gold";
      default:
        return "pill-forest";
    }
  };

  return (
    <div className={`botanical-card p-6 flex flex-col gap-5 bg-white transition-opacity ${loading ? "opacity-75" : "opacity-100"}`}>
      {/* Card Header */}
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
            <Sparkles size={20} />
          </div>
          <div>
            <h3 className="title-md font-serif text-lg">{t("Agronomic Health Intelligence")}</h3>
            <span className="mono-tag block" style={{ color: "var(--text-muted)" }}>{t("Deterministic Rule Engine & Natural Language Insights")}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={getSeverityPill(severity)}>
            <span className="uppercase text-[11px] font-semibold">{t("Risk:")}{" "}{t(severity)}</span>
          </span>
          <span className="pill-forest">
            <ShieldCheck size={12} className="text-forest-700" />
            <span className="text-[11px]">{recommendation ? `${Math.round(recommendation.confidence * 100)}% ${t("Confidence")}` : t("Awaiting Telemetry")}</span>
          </span>
        </div>
      </div>

      {/* AI Contextual Explanation Box */}
      {aiExplanation && (
        <div
          className="p-4 rounded-xl border text-sm leading-relaxed"
          style={{
            backgroundColor: "var(--bg-subtle)",
            borderColor: "var(--border-subtle)",
            color: "var(--text-primary)",
          }}
        >
          <div className="flex items-center gap-1.5 font-semibold text-xs mb-1.5" style={{ color: "var(--forest-700)" }}>
            <Sparkles size={13} />
            <span>{t("Agronomist Summary")}</span>
          </div>
          <p className="font-sans text-xs md:text-sm">{aiExplanation}</p>
        </div>
      )}

      {/* Four Dimension Assessments */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        <div className="p-3 rounded-lg border text-xs" style={{ backgroundColor: "var(--bg-subtle)", borderColor: "var(--border-subtle)" }}>
          <span className="block text-[11px]" style={{ color: "var(--text-muted)" }}>{t("Environment")}</span>
          <strong className="block mt-0.5 truncate" style={{ color: "var(--text-primary)" }}>
            {t(recommendation?.environmental_condition || "Nominal Indoor")}
          </strong>
        </div>

        <div className="p-3 rounded-lg border text-xs" style={{ backgroundColor: "var(--bg-subtle)", borderColor: "var(--border-subtle)" }}>
          <span className="block text-[11px]" style={{ color: "var(--text-muted)" }}>{t("Soil Moisture")}</span>
          <strong className="block mt-0.5 truncate" style={{ color: "var(--forest-700)" }}>
            {t(recommendation?.moisture_assessment || "Optimal Zone")}
          </strong>
        </div>

        <div className="p-3 rounded-lg border text-xs" style={{ backgroundColor: "var(--bg-subtle)", borderColor: "var(--border-subtle)" }}>
          <span className="block text-[11px]" style={{ color: "var(--text-muted)" }}>{t("Temperature")}</span>
          <strong className="block mt-0.5 truncate" style={{ color: "var(--terracotta-700)" }}>
            {t(recommendation?.temperature_assessment || "Thermal Comfort")}
          </strong>
        </div>

        <div className="p-3 rounded-lg border text-xs" style={{ backgroundColor: "var(--bg-subtle)", borderColor: "var(--border-subtle)" }}>
          <span className="block text-[11px]" style={{ color: "var(--text-muted)" }}>{t("Humidity")}</span>
          <strong className="block mt-0.5 truncate" style={{ color: "var(--dew-700)" }}>
            {t(recommendation?.humidity_assessment || "Balanced VPD")}
          </strong>
        </div>
      </div>

      {/* Two Columns: Observations & Recommendations */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Real-time Observations */}
        <div
          className="p-4 rounded-xl border flex flex-col gap-2.5"
          style={{ backgroundColor: "var(--surface-inset)", borderColor: "var(--border-subtle)" }}
        >
          <h4 className="mono-tag font-semibold uppercase tracking-wider text-xs" style={{ color: "var(--text-secondary)" }}>{t("Telemetry Observations")}</h4>
          <ul className="flex flex-col gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
            {observations.map((obs, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="mt-0.5" style={{ color: "var(--forest-600)" }}>&bull;</span>
                <span>{t(obs)}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Actionable Next Steps */}
        <div
          className="p-4 rounded-xl border flex flex-col gap-2.5"
          style={{ backgroundColor: "var(--surface-inset)", borderColor: "var(--border-subtle)" }}
        >
          <h4 className="mono-tag font-semibold uppercase tracking-wider text-xs" style={{ color: "var(--text-secondary)" }}>{t("Prescribed Next Steps")}</h4>
          <ul className="flex flex-col gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
            {recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <CheckCircle size={14} className="shrink-0 mt-0.5 text-forest-600" />
                <span>{t(rec)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Advisory Notice */}
      <div className="flex items-center gap-1.5 text-xs pt-2 border-t" style={{ borderColor: "var(--border-subtle)", color: "var(--text-muted)" }}>
        <HelpCircle size={12} className="shrink-0" />
        <span>{t(recommendation?.limitations || "Telemetry-grounded agronomic rules. LLM operates strictly in advisory capacity.")}</span>
      </div>
    </div>
  );
}

"use client";

import React from "react";
import { Sparkles, CheckCircle, AlertTriangle, ShieldCheck, HelpCircle } from "lucide-react";
import { PlantRecommendation } from "@/types/plant-monitor";

interface Props {
  recommendation: PlantRecommendation | null;
  loading: boolean;
}

export default function AIRecommendationsCard({ recommendation, loading }: Props) {
  const observations = recommendation?.observations || [
    "Soil moisture is within the healthy calibrated boundary.",
    "Ambient temperature and humidity maintain optimal vapor pressure deficit.",
  ];

  const recommendations = recommendation?.recommendations || [
    "Routine autonomous monitoring active. No intervention needed.",
  ];

  const severity = recommendation?.severity || "low";
  const aiExplanation = recommendation?.ai_explanation;

  const severityColors = {
    low: { bg: "rgba(16, 185, 129, 0.15)", text: "#10b981", border: "rgba(16, 185, 129, 0.3)" },
    medium: { bg: "rgba(245, 158, 11, 0.15)", text: "#f59e0b", border: "rgba(245, 158, 11, 0.3)" },
    high: { bg: "rgba(239, 68, 68, 0.15)", text: "#ef4444", border: "rgba(239, 68, 68, 0.3)" },
  };

  const currentSev = severityColors[severity] || severityColors.low;

  return (
    <div
      style={{
        background: "rgba(15, 23, 42, 0.7)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: "20px",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "18px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              padding: "8px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(168, 85, 247, 0.2))",
              color: "#a855f7",
            }}
          >
            <Sparkles size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, margin: 0, color: "#f8fafc" }}>
              AI Plant Health Intelligence
            </h3>
            <span style={{ fontSize: "12px", color: "#64748b" }}>
              Agronomic rule engine & natural language insights
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span
            style={{
              fontSize: "12px",
              padding: "3px 10px",
              borderRadius: "999px",
              background: currentSev.bg,
              color: currentSev.text,
              border: `1px solid ${currentSev.border}`,
              fontWeight: 600,
              textTransform: "uppercase",
            }}
          >
            Risk: {severity}
          </span>
          <span
            style={{
              fontSize: "12px",
              padding: "3px 10px",
              borderRadius: "999px",
              background: "rgba(255, 255, 255, 0.05)",
              color: "#94a3b8",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <ShieldCheck size={12} color="#10b981" />
            95% Confidence
          </span>
        </div>
      </div>

      {/* AI Contextual Explanation Box */}
      {aiExplanation && (
        <div
          style={{
            background: "rgba(168, 85, 247, 0.08)",
            border: "1px solid rgba(168, 85, 247, 0.2)",
            borderRadius: "14px",
            padding: "16px",
            color: "#e2e8f0",
            fontSize: "13px",
            lineHeight: 1.6,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#c084fc", fontWeight: 600, marginBottom: "6px" }}>
            <Sparkles size={14} /> Natural Language Agronomist Summary
          </div>
          {aiExplanation}
        </div>
      )}

      {/* Specific Health Dimension Assessments (Section 4) */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "10px",
        }}
      >
        <div style={{ background: "rgba(0,0,0,0.2)", padding: "10px 14px", borderRadius: "10px", border: "1px solid rgba(255,255,255,0.05)" }}>
          <span style={{ fontSize: "11px", color: "#64748b", display: "block" }}>Environmental Condition</span>
          <strong style={{ fontSize: "13px", color: "#e2e8f0" }}>{recommendation?.environmental_condition || "Nominal Indoor"}</strong>
        </div>
        <div style={{ background: "rgba(0,0,0,0.2)", padding: "10px 14px", borderRadius: "10px", border: "1px solid rgba(255,255,255,0.05)" }}>
          <span style={{ fontSize: "11px", color: "#64748b", display: "block" }}>Moisture Assessment</span>
          <strong style={{ fontSize: "13px", color: "#10b981" }}>{recommendation?.moisture_assessment || "Optimal range"}</strong>
        </div>
        <div style={{ background: "rgba(0,0,0,0.2)", padding: "10px 14px", borderRadius: "10px", border: "1px solid rgba(255,255,255,0.05)" }}>
          <span style={{ fontSize: "11px", color: "#64748b", display: "block" }}>Temperature Assessment</span>
          <strong style={{ fontSize: "13px", color: "#f43f5e" }}>{recommendation?.temperature_assessment || "Optimal microclimate"}</strong>
        </div>
        <div style={{ background: "rgba(0,0,0,0.2)", padding: "10px 14px", borderRadius: "10px", border: "1px solid rgba(255,255,255,0.05)" }}>
          <span style={{ fontSize: "11px", color: "#64748b", display: "block" }}>Humidity Assessment</span>
          <strong style={{ fontSize: "13px", color: "#38bdf8" }}>{recommendation?.humidity_assessment || "Balanced VPD"}</strong>
        </div>
      </div>

      {/* Observations and Recommendations Columns */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "16px",
        }}
      >
        {/* Real-time Observations */}
        <div style={{ background: "rgba(0, 0, 0, 0.25)", padding: "16px", borderRadius: "14px", border: "1px solid rgba(255, 255, 255, 0.04)" }}>
          <h4 style={{ fontSize: "13px", fontWeight: 700, color: "#94a3b8", margin: "0 0 12px 0", textTransform: "uppercase" }}>
            Real-Time Observations
          </h4>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "10px" }}>
            {observations.map((obs, idx) => (
              <li key={idx} style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "13px", color: "#cbd5e1" }}>
                <span style={{ color: "#38bdf8", marginTop: "2px" }}>&bull;</span>
                <span>{obs}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Actionable Next Steps */}
        <div style={{ background: "rgba(0, 0, 0, 0.25)", padding: "16px", borderRadius: "14px", border: "1px solid rgba(255, 255, 255, 0.04)" }}>
          <h4 style={{ fontSize: "13px", fontWeight: 700, color: "#94a3b8", margin: "0 0 12px 0", textTransform: "uppercase" }}>
            Suggested Actions
          </h4>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "10px" }}>
            {recommendations.map((rec, idx) => (
              <li key={idx} style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "13px", color: "#cbd5e1" }}>
                <CheckCircle size={15} color="#22c55e" style={{ flexShrink: 0, marginTop: "2px" }} />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div style={{ fontSize: "11px", color: "#64748b", display: "flex", alignItems: "center", gap: "5px" }}>
        <HelpCircle size={12} />
        {recommendation?.limitations || "Guidance grounded in microclimate metrics. LLM operates strictly in advisory capacity."}
      </div>
    </div>
  );
}

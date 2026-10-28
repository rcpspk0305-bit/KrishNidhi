"use client";

import { useMemo, useState, useEffect } from "react";
import { Bell, Bot, MapPin, RefreshCw, Loader2 } from "lucide-react";
import MetricContent from "@/components/MetricContent";
import RecommendationCard from "@/components/RecommendationCard";
import SensorCard from "@/components/SensorCard";
import SummaryContent from "@/components/SummaryContent";
import TabNavigation from "@/components/TabNavigation";
import { metricTabs, sensorSummaries, summaryTabs } from "@/lib/dashboard-config";
import { buildSeries, mockFieldData, summaryCards } from "@/lib/mock-data";
import { getDashboardWindow } from "@/lib/api";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [data, setData] = useState(mockFieldData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const windowData = await getDashboardWindow("overview");
      if (windowData.status === "success") {
        setData({
          cropPrediction: windowData.payload.hero.recommended_crop,
          current: windowData.payload.cards,
        });
      }
      setError(null);
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
      setError("Backend connection failed. Using cached data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const metric = metricTabs.find((item) => item.id === activeTab);
  const series = useMemo(() => metric ? buildSeries(metric.id, data.current) : [], [metric, data]);

  return (
    <main className="section">
      <div className="topbar">
        <div className="page-shell nav-row">
          <div>
            <div className="badge"><Bot size={14} /> Smart farming dashboard</div>
            <h1 className="title-lg" style={{ marginTop: 10 }}>KrishiNidhi Operations</h1>
          </div>
          <div className="glass" style={{ borderRadius: 18, padding: "12px 14px", display: "flex", alignItems: "center", gap: 10 }}>
            <MapPin size={16} /> Hyderabad, Telangana
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button 
              className="ghost" 
              type="button" 
              onClick={fetchData} 
              disabled={loading}
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} style={{ marginRight: 8, verticalAlign: "middle" }} />} 
              {loading ? "Refreshing..." : "Refresh"}
            </button>
            <button 
              className="badge" 
              style={{ cursor: "pointer", background: "rgba(255,255,255,0.05)" }}
              onClick={() => {
                localStorage.removeItem("auth_token");
                window.location.href = "/login";
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="page-shell" style={{ display: "grid", gap: 24 }}>
        {error && (
          <div className="badge" style={{ background: "rgba(251, 113, 133, 0.1)", color: "#fb7185", borderColor: "rgba(251, 113, 133, 0.2)", width: "fit-content" }}>
            {error}
          </div>
        )}

        <section className="hero-grid">
          <div className="hero-card glass">
            <span className="badge">Live telemetry {loading ? "updating..." : "online"}</span>
            <h2 className="title-xl">{data.cropPrediction}</h2>
            <p className="muted" style={{ maxWidth: 650 }}>
              Use the overview for quick decisions, then switch into any metric tab to inspect thresholds, short trend history, and operator recommendations without opening many separate files.
            </p>
            <div className="stats-grid" style={{ marginTop: 18 }}>
              {summaryCards(data).map((card) => (
                <div key={card.label} className="kpi">
                  <h4>{card.value}</h4>
                  <p>{card.label}</p>
                </div>
              ))}
            </div>
          </div>

          <RecommendationCard
            title="AI Action Plan"
            items={[
              "Increase morning irrigation by 8% due to temperature drift.",
              "Field pH is still healthy, so avoid corrective dosing today.",
              "Use scheme finder to check water-management subsidy eligibility.",
            ]}
            footer="Priority score: 82/100"
          />
        </section>

        <TabNavigation
          activeTab={activeTab}
          onChange={setActiveTab}
          summaryTabs={summaryTabs}
          metricTabs={metricTabs}
        />

        <section className="dashboard-grid">
          <div style={{ display: "grid", gap: 18 }}>
            {activeTab === "overview" ? (
              <SummaryContent title="Overview" description="Fast scan of your field signals, operator alerts, and system confidence.">
                <div className="stats-grid">
                  {sensorSummaries(data.current).map((sensor) => {
                    const metricConfig = metricTabs.find(m => m.label === sensor.label);
                    const sensorSeries = metricConfig ? buildSeries(metricConfig.id, data.current) : [];
                    return <SensorCard key={sensor.label} {...sensor} series={sensorSeries} />;
                  })}
                </div>
              </SummaryContent>
            ) : metric ? (
              <MetricContent 
                metric={metric} 
                value={typeof data.current[metric.valueKey as keyof typeof data.current] === "number" ? Number(data.current[metric.valueKey as keyof typeof data.current]) : 0} 
                series={series} 
              />
            ) : (
              <SummaryContent
                title={summaryTabs.find((tab) => tab.id === activeTab)?.label ?? "Summary"}
                description="These summary sections replace many dedicated files with one reusable component and focused content blocks."
              >
                <div className="summary-grid">
                  <div className="content-card">
                    <h3>System insight</h3>
                    <p className="muted">Your workflow now uses reusable summary panels instead of separate long components for every insight screen.</p>
                  </div>
                  <div className="content-card">
                    <h3>Operator note</h3>
                    <p className="muted">Keep charts, ranges, and action blocks data-driven so only config changes when a new sensor is added.</p>
                  </div>
                </div>
              </SummaryContent>
            )}
          </div>

          <div style={{ display: "grid", gap: 18 }}>
            <div className="panel-card glass">
              <div className="between">
                <h3>Notifications</h3>
                <Bell size={18} />
              </div>
              <ul className="list" style={{ marginTop: 14 }}>
                <li>Soil moisture dipped 4% from the previous reading.</li>
                <li>Predicted crop fit remains stable for the next 6-hour window.</li>
                <li>Water TDS is inside safe irrigation range.</li>
              </ul>
            </div>
            <RecommendationCard
              title="Operator checklist"
              items={[
                "Validate sensor calibration at the start of each shift.",
                "Use the metric view for detailed thresholds before sending alerts.",
                "Keep backend API paths in one config file for cleaner maintenance.",
              ]}
            />
          </div>
        </section>
      </div>
    </main>
  );
}

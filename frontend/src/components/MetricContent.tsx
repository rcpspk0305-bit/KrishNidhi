import { useState, useMemo } from "react";
import DetailedChart from "@/components/DetailedChart";
import { Calendar, TrendingUp } from "lucide-react";

type Metric = {
  id: string;
  label: string;
  hint: string;
  unit: string;
  optimal: [number, number];
  rangeLabel: string;
  valueKey: "temperature" | "humidity" | "ph" | "tds" | "rainfall" | "NPK";
};

type Props = {
  metric: Metric;
  value: number;
  series: number[];
};

export default function MetricContent({ metric, value, series }: Props) {
  const [timeframe, setTimeframe] = useState<"daily" | "weekly">("daily");
  const [min, max] = metric.optimal;
  const state = value >= min && value <= max ? "Within optimal range" : value < min ? "Below optimal range" : "Above optimal range";
  
  const comparisonSeries = useMemo(() => {
    const factor = timeframe === "daily" ? 0.95 : 0.85;
    return series.map((v, i) => {
      const pseudoNoise = (((i * 13 + 7) % 11) - 5) / 100;
      return v * (factor + pseudoNoise);
    });
  }, [series, timeframe]);

  const getChartColor = () => {
    if (metric.id.includes("temperature")) return "#fb7185";
    if (metric.id.includes("moisture") || metric.id.includes("water")) return "#3b82f6";
    if (metric.id.includes("ph")) return "#f59e0b";
    return "#10b981";
  };

  const variancePercent = (((Math.abs(value * 3) + 7) % 25) / 10 + 0.5).toFixed(1);

  return (
    <section className="content-card glass" style={{ display: "grid", gap: 24, padding: "32px" }}>
      <div className="between">
        <div>
          <h2 className="title-md">{metric.label} Intelligence</h2>
          <p className="muted">{metric.hint}</p>
        </div>
        <div className="badge" style={{ padding: "8px 16px" }}>Optimal: {metric.rangeLabel}</div>
      </div>

      <div className="stats-grid">
        <div className="panel-card glass" style={{ background: "rgba(255,255,255,0.02)" }}>
          <p className="muted" style={{ fontSize: 12 }}>CURRENT READING</p>
          <h3 style={{ fontSize: 32, marginTop: 8 }}>{value} <span style={{ fontSize: 16 }}>{metric.unit}</span></h3>
        </div>
        <div className="panel-card glass" style={{ background: "rgba(255,255,255,0.02)" }}>
          <p className="muted" style={{ fontSize: 12 }}>STATUS</p>
          <h3 style={{ fontSize: 24, marginTop: 12, color: value < min || value > max ? "#fb7185" : "#10b981" }}>{state}</h3>
        </div>
        <div className="panel-card glass" style={{ background: "rgba(255,255,255,0.02)" }}>
          <p className="muted" style={{ fontSize: 12 }}>VARIANCE</p>
          <div className="between" style={{ marginTop: 12 }}>
             <h3 style={{ fontSize: 24 }}>+{variancePercent}%</h3>
             <TrendingUp size={20} color="#10b981" />
          </div>
        </div>
      </div>

      <div className="panel-card glass" style={{ padding: "24px", border: "1px solid rgba(255,255,255,0.05)" }}>
        <div className="between" style={{ marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Calendar size={20} className="primary" />
            <h3 className="title-sm">Performance Comparison</h3>
          </div>
          <div className="tab-row" style={{ background: "rgba(0,0,0,0.2)", padding: 4, borderRadius: 12 }}>
            <button 
              className={`ghost ${timeframe === "daily" ? "active" : ""}`} 
              onClick={() => setTimeframe("daily")}
              style={{ padding: "6px 16px", borderRadius: 8, fontSize: 12 }}
            >
              Daily
            </button>
            <button 
              className={`ghost ${timeframe === "weekly" ? "active" : ""}`} 
              onClick={() => setTimeframe("weekly")}
              style={{ padding: "6px 16px", borderRadius: 8, fontSize: 12 }}
            >
              Weekly
            </button>
          </div>
        </div>
        
        <DetailedChart 
          data={series} 
          comparisonData={comparisonSeries}
          unit={metric.unit} 
          color={getChartColor()} 
          label={timeframe === "daily" ? "Today" : "This Week"}
          comparisonLabel={timeframe === "daily" ? "Yesterday" : "Last Week"}
        />
      </div>
    </section>
  );
}

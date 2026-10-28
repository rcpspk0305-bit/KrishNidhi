import Link from "next/link";
import { ArrowRight, Cpu, Landmark, Sprout, Waves } from "lucide-react";

const quickLinks = [
  {
    title: "AI Smart Plant Dashboard",
    href: "/dashboard",
    desc: "ESP8266 NodeMCU live telemetry, DHT11 & soil moisture sensing, remote pump relay actuator, and AI agronomy.",
    icon: Sprout,
  },
  {
    title: "Dedicated Plant Monitor View",
    href: "/plant-monitor",
    desc: "Full-width active telemetry and IoT actuator control workspace.",
    icon: Cpu,
  },
  {
    title: "Government Scheme Finder",
    href: "/scheme-finder",
    desc: "Search farmer and agricultural schemes by category, eligibility, and benefit type.",
    icon: Landmark,
  },
];

export default function HomePage() {
  return (
    <main className="section">
      <div className="page-shell" style={{ display: "grid", gap: 24 }}>
        <section className="hero-grid">
          <div className="hero-card glass">
            <span className="badge">
              <Sprout size={14} /> AI-Powered Personal IoT Plant Monitoring
            </span>
            <h1 className="title-xl">Smart Plant Monitor & Automated Irrigation</h1>
            <p className="muted" style={{ maxWidth: 680, fontSize: 18 }}>
              Intelligent IoT plant monitoring and automated fail-safe irrigation with ESP8266 NodeMCU, DHT11, calibrated soil moisture, PIR motion detection, and real-time Server-Sent Events.
            </p>
            <div className="row" style={{ marginTop: 18 }}>
              <Link href="/dashboard" className="cta" style={{ background: "linear-gradient(135deg, #16a34a, #15803d)" }}>
                Launch Smart Plant Dashboard
              </Link>
              <Link href="/scheme-finder" className="ghost">
                Scheme Finder
              </Link>
            </div>
          </div>

          <div className="panel-card glass">
            <div className="between">
              <h2 className="title-lg">Workflow fit</h2>
              <Waves size={20} />
            </div>
            <ul className="list" style={{ marginTop: 14 }}>
              <li>App routes stay inside <strong>app</strong> for dashboard and scheme finder.</li>
              <li>Shared UI lives in <strong>components</strong> and avoids repeated metric pages.</li>
              <li>Reusable config and types stay inside <strong>lib</strong> and <strong>types</strong>.</li>
            </ul>
          </div>
        </section>

        <section className="scheme-grid">
          {quickLinks.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href} className="content-card glass" style={{ display: "grid", gap: 12 }}>
                <div className="between">
                  <div className="badge"><Icon size={14} /> Launch module</div>
                  <ArrowRight size={18} />
                </div>
                <h3 className="title-lg">{item.title}</h3>
                <p className="muted">{item.desc}</p>
              </Link>
            );
          })}
        </section>
      </div>
    </main>
  );
}
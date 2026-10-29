import Link from "next/link";
import { ArrowRight, Cpu, Landmark, Sprout, ShieldCheck, Activity } from "lucide-react";

const modules = [
  {
    title: "Smart Plant Monitor & Irrigation",
    href: "/plant-monitor",
    badge: "Primary Workspace",
    desc: "Real-time NodeMCU telemetry (DHT11, calibrated soil moisture, PIR motion), authoritative relay actuator, and AI agronomy insights.",
    icon: Sprout,
    cta: "Launch Workspace",
    primary: true,
  },
  {
    title: "Personal IoT Station",
    href: "/dashboard",
    badge: "IoT Telemetry",
    desc: "Dedicated responsive dashboard for continuous environmental tracking and virtual hardware testing.",
    icon: Activity,
    cta: "Open Station",
    primary: false,
  },
  {
    title: "Government Scheme Finder",
    href: "/scheme-finder",
    badge: "Governance Directory",
    desc: "Search farmer and agricultural assistance schemes, subsidies, and eligibility criteria across regions.",
    icon: Landmark,
    cta: "Explore Schemes",
    primary: false,
  },
];

export default function HomePage() {
  return (
    <main className="section" style={{ backgroundColor: "var(--bg-canvas)" }}>
      <div className="page-shell flex flex-col gap-10">
        
        {/* Editorial Botanical Hero Card */}
        <section className="botanical-card p-8 md:p-14 bg-white flex flex-col gap-6">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="pill-forest">
              <Sprout size={13} className="text-forest-700" />
              <span>KrishiNidhi Botanical IoT Suite</span>
            </span>
            <span className="pill-dew">
              <Cpu size={13} />
              <span>NodeMCU ESP8266 &bull; Server-Sent Events</span>
            </span>
          </div>

          <div className="max-w-3xl">
            <h1 className="title-xl mb-4">
              Mindful Plant Telemetry &amp; Fail-Safe Automated Irrigation.
            </h1>
            <p className="text-base md:text-lg leading-relaxed" style={{ color: "var(--text-secondary)" }}>
              A quieter, higher-fidelity workspace to monitor your plant&apos;s microclimate, observe soil hydration dynamics, and issue authoritative irrigation commands backed by hardware fail-safes and agronomic intelligence.
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap pt-2">
            <Link href="/plant-monitor" className="btn-primary">
              <span>Launch Plant Workspace</span>
              <ArrowRight size={16} />
            </Link>
            <Link href="/scheme-finder" className="btn-secondary">
              <Landmark size={15} />
              <span>Agricultural Scheme Finder</span>
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 border-t mt-4" style={{ borderColor: "var(--border-subtle)" }}>
            <div className="flex items-start gap-3">
              <span className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: "var(--forest-600)" }} />
              <div>
                <strong className="block text-sm font-serif" style={{ color: "var(--forest-900)" }}>Hardware-Authoritative</strong>
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>Firmware acknowledgments represent true relay coil status.</span>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: "var(--terracotta-600)" }} />
              <div>
                <strong className="block text-sm font-serif" style={{ color: "var(--forest-900)" }}>Watchdog Protection</strong>
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>15s runtime cutoff and 60s cooldown prevent water damage.</span>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: "var(--dew-600)" }} />
              <div>
                <strong className="block text-sm font-serif" style={{ color: "var(--forest-900)" }}>Live Telemetry Broadcast</strong>
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>Sub-second SSE updates with graceful polling resilience.</span>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Modules Grid */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {modules.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.href}
                className="botanical-card p-6 bg-white flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <span className="pill-forest text-[11px]">{item.badge}</span>
                    <div
                      className="p-2 rounded-xl"
                      style={{ backgroundColor: "var(--forest-50)", color: "var(--forest-800)" }}
                    >
                      <Icon size={18} />
                    </div>
                  </div>

                  <h3 className="title-md font-serif text-lg mb-2">
                    {item.title}
                  </h3>
                  <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                    {item.desc}
                  </p>
                </div>

                <div className="pt-6 mt-4 border-t" style={{ borderColor: "var(--border-subtle)" }}>
                  <Link
                    href={item.href}
                    className={item.primary ? "btn-primary w-full text-xs py-2.5" : "btn-secondary w-full text-xs py-2.5"}
                  >
                    <span>{item.cta}</span>
                    <ArrowRight size={14} />
                  </Link>
                </div>
              </div>
            );
          })}
        </section>

        {/* Editorial Footer */}
        <footer className="text-center text-xs py-8 border-t" style={{ borderColor: "var(--border-subtle)", color: "var(--text-muted)" }}>
          <p className="font-serif italic text-sm mb-1" style={{ color: "var(--text-secondary)" }}>
            KrishiNidhi Botanical Systems &bull; Department of Computer Science &amp; Engineering
          </p>
          <p className="mono-tag text-[11px]">
            NodeMCU ESP8266 ESP-12E Architecture &bull; Next.js 16 &bull; Warm Editorial Botanical Edition
          </p>
        </footer>

      </div>
    </main>
  );
}

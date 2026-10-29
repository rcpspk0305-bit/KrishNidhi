"use client";

import { useLanguage } from "@/components/LanguageProvider";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Phone, ArrowRight, Sprout, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";

export default function LoginPage() {
  const { t } = useLanguage();

  const [mobile, setMobile] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // Mock authentication
    setTimeout(() => {
      if (mobile === "9999999999" && password === "krishi123") {
        localStorage.setItem("auth_token", "ps10_authenticated");
        router.push("/plant-monitor");
      } else {
        setError("Invalid credentials. Try 9999999999 / krishi123");
        setLoading(false);
      }
    }, 1200);
  };

  return (
    <main className="section flex items-center justify-center p-4" style={{ backgroundColor: "var(--bg-canvas)" }}>
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="botanical-card p-8 md:p-10 w-full max-w-md bg-white flex flex-col gap-6"
      >
        <div className="text-center">
          <div
            className="inline-flex p-3 rounded-2xl border mb-3"
            style={{
              backgroundColor: "var(--forest-50)",
              borderColor: "var(--forest-100)",
              color: "var(--forest-700)",
            }}
          >
            <Sprout size={28} />
          </div>
          <h1 className="title-md font-serif text-2xl font-bold" style={{ color: "var(--forest-900)" }}>{t("KrishiNidhi Station Login")}</h1>
          <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>{t("Enter your credentials to access the plant monitoring console")}</p>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label className="mono-tag font-semibold block mb-1.5" style={{ color: "var(--text-secondary)" }}>{t("MOBILE NUMBER")}</label>
            <div
              className="flex items-center px-3.5 rounded-xl border bg-white focus-within:ring-2 focus-within:ring-forest-600"
              style={{ borderColor: "var(--border-default)" }}
            >
              <Phone size={16} style={{ color: "var(--text-muted)" }} />
              <input
                type="tel"
                placeholder="9999999999"
                value={mobile}
                onChange={(e) => setMobile(e.target.value)}
                className="w-full py-3 px-3 text-sm bg-transparent outline-none"
                style={{ color: "var(--text-primary)" }}
                required
              />
            </div>
          </div>

          <div>
            <label className="mono-tag font-semibold block mb-1.5" style={{ color: "var(--text-secondary)" }}>{t("PASSWORD")}</label>
            <div
              className="flex items-center px-3.5 rounded-xl border bg-white focus-within:ring-2 focus-within:ring-forest-600"
              style={{ borderColor: "var(--border-default)" }}
            >
              <Lock size={16} style={{ color: "var(--text-muted)" }} />
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full py-3 px-3 text-sm bg-transparent outline-none"
                style={{ color: "var(--text-primary)" }}
                required
              />
            </div>
          </div>

          {error && (
            <div
              className="p-3 rounded-xl border text-xs text-center font-medium"
              style={{
                backgroundColor: "var(--terracotta-50)",
                borderColor: "rgba(189, 81, 52, 0.2)",
                color: "var(--terracotta-700)",
              }}
            >
              {t(error)}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-3 mt-2"
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <>
                <span>{t("Sign In to Console")}</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div className="text-center text-xs pt-4 border-t flex flex-col gap-2" style={{ borderColor: "var(--border-subtle)", color: "var(--text-muted)" }}>
          <p>{t("Demo credentials:")}<span className="mono-tag font-bold" style={{ color: "var(--forest-700)" }}>{t("9999999999 / krishi123")}</span>
          </p>
          <Link href="/" className="font-semibold underline hover:text-forest-800" style={{ color: "var(--forest-700)" }}>{t("Return to Homepage")}</Link>
        </div>
      </motion.div>
    </main>
  );
}

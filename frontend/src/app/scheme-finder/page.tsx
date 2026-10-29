"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Search, 
  ArrowLeft, 
  Landmark, 
  TrendingUp, 
  Users, 
  Calendar,
  ExternalLink,
} from "lucide-react";
import Link from "next/link";

const schemes = [
  {
    id: 1,
    title: "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
    category: "Income Support",
    benefit: "₹6,000 per year in three installments",
    eligibility: "All landholding farmer families",
    tags: ["Central", "Direct Benefit"],
    desc: "A central sector scheme providing income support to all landholding farmers' families in the country to supplement their financial needs."
  },
  {
    id: 2,
    title: "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
    category: "Insurance",
    benefit: "Financial support to farmers suffering crop loss/damage",
    eligibility: "All farmers including sharecroppers and tenant farmers",
    tags: ["Insurance", "Risk Management"],
    desc: "Yield-based crop insurance scheme that provides financial support to farmers for crop failure due to natural calamities, pests & diseases."
  },
  {
    id: 3,
    title: "Soil Health Card Scheme",
    category: "Soil Health",
    benefit: "Testing soil and providing nutrition recommendations",
    eligibility: "All farmers with land holdings",
    tags: ["Testing", "Fertility"],
    desc: "Promotes soil test based and balanced use of fertilizers to enable farmers to realize higher yields at lower cost."
  },
  {
    id: 4,
    title: "PM-KMY (Pradhan Mantri Kisan Maandhan Yojana)",
    category: "Pension",
    benefit: "Monthly pension of ₹3,000",
    eligibility: "Small and marginal farmers aged 18-40 years",
    tags: ["Old Age", "Security"],
    desc: "A voluntary and contributory pension scheme for small and marginal farmers to provide social security in their old age."
  }
];

export default function SchemeFinder() {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const categories = ["All", "Income Support", "Insurance", "Soil Health", "Pension"];

  const filtered = schemes.filter(s => {
    const matchesSearch = s.title.toLowerCase().includes(search.toLowerCase());
    const matchesCat = activeCategory === "All" || s.category === activeCategory;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="min-h-screen bg-surface font-inter text-on-surface">
      <header className="sticky top-0 z-50 mx-auto max-w-7xl rounded-b-3xl bg-white/70 px-6 py-4 shadow-sm backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <Link href="/">
            <motion.div whileHover={{ scale: 1.1 }} className="cursor-pointer rounded-xl bg-surface-container-low p-2.5 transition-colors hover:bg-surface-container">
              <ArrowLeft className="h-5 w-5 text-primary" />
            </motion.div>
          </Link>
          <div>
            <h1 className="font-display text-xl font-bold tracking-tight text-on-surface uppercase">KrishiNidhi</h1>
            <p className="text-[10px] font-bold text-primary tracking-widest uppercase">Benefit Directory</p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto p-6 space-y-12 py-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-container/10">
            <Landmark className="h-4 w-4 text-primary" />
            <span className="text-[10px] font-bold text-primary tracking-widest uppercase">Official Governance Portal</span>
          </div>
          <h2 className="font-display text-5xl font-black tracking-tight text-on-surface">SCHEME FINDER</h2>
          <p className="text-slate-500 text-base max-w-lg mx-auto">Discover agricultural subsidies and support programs tailored to your field telemetry and regional classification.</p>
        </motion.div>

        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search by name or keyword..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white rounded-2xl pl-14 pr-6 py-4 text-on-surface ambient-shadow focus:outline-none focus:ring-2 focus:ring-primary-container transition-all"
            />
          </div>
          
          <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
            {categories.map(cat => (
              <button 
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-6 py-4 rounded-2xl text-[10px] font-bold tracking-widest uppercase transition-all whitespace-nowrap ambient-shadow ${
                  activeCategory === cat 
                  ? "bg-primary text-white glow-primary" 
                  : "bg-white text-slate-500 hover:text-primary"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <AnimatePresence mode="popLayout">
            {filtered.map((s, i) => (
              <motion.div
                key={s.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: i * 0.05 }}
                className="bg-white p-8 rounded-[2rem] ambient-shadow flex flex-col group transition-all hover:bg-surface-container-low"
              >
                <div className="flex justify-between items-start mb-6">
                  <div className="p-3 rounded-2xl bg-surface-container-low group-hover:bg-primary/10 transition-colors">
                    <TrendingUp className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex gap-2">
                    {s.tags.map(t => (
                      <span key={t} className="text-[8px] font-bold tracking-widest text-slate-400 uppercase border border-slate-100 px-3 py-1 rounded-full">{t}</span>
                    ))}
                  </div>
                </div>

                <h3 className="font-display text-xl font-bold text-on-surface mb-2 group-hover:text-primary transition-colors">
                  {s.title}
                </h3>
                <p className="text-slate-500 text-sm mb-6 flex-1 line-clamp-3">
                  {s.desc}
                </p>

                <div className="space-y-4 mb-8 bg-surface-container-low/50 p-4 rounded-2xl">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-white">
                      <Users className="h-4 w-4 text-secondary" />
                    </div>
                    <div>
                      <p className="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Eligibility</p>
                      <p className="text-xs font-bold text-on-surface">{s.eligibility}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-white">
                      <Calendar className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <p className="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Benefit Amount</p>
                      <p className="text-xs font-bold text-primary">{s.benefit}</p>
                    </div>
                  </div>
                </div>

                <button className="w-full py-4 bg-primary text-white rounded-2xl text-[10px] font-bold tracking-[0.2em] uppercase glow-primary hover:brightness-110 transition-all flex items-center justify-center gap-2">
                  Access Portal
                  <ExternalLink className="h-3 w-3" />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </main>

      <style dangerouslySetInnerHTML={{ __html: `
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}} />
    </div>
  );
}

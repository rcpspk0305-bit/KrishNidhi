export const mockFieldData = {
  cropPrediction: "Wheat",
  current: {
    temperature: 24.5,
    humidity: 42.0,
    ph: 6.8,
    tds: 150.0,
    rainfall: 12.0,
    NPK: "80:40:40"
  },
};

export const summaryCards = (data: typeof mockFieldData) => [
  { label: "Optimal pH", value: data.current.ph.toFixed(1) },
  { label: "Stability", value: "94%" },
  { label: "Growth Index", value: "High" },
];

export const buildSeries = (id: string, current: Record<string, number | string>) => {
  const raw = current[id];
  const seed = typeof raw === "number" ? raw : 25;
  return Array.from({ length: 24 }, (_, i) => seed + Math.sin(i / 2) * 2 + (((i * 7) % 10) - 5) * 0.1);
};

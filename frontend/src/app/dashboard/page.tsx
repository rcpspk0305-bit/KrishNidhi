"use client";

import React from "react";
import PlantWorkspace from "@/components/plant-monitor/PlantWorkspace";

export default function DashboardPage() {
  return <PlantWorkspace initialDeviceId="esp8266-plant-01" />;
}

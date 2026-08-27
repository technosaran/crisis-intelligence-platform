"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api";
import { Play, AlertTriangle, Wind, Droplets, Activity } from "lucide-react";

export function SimulatorPanel() {
  const [loading, setLoading] = useState(false);
  const [lastTriggered, setLastTriggered] = useState<string | null>(null);

  const scenarios = [
    { id: "CHENNAI_FLOOD", name: "Chennai Flood", icon: Droplets, color: "text-blue-500", bg: "bg-blue-100" },
    { id: "EARTHQUAKE_MAG_7", name: "Mag 7.0 Earthquake", icon: Activity, color: "text-red-500", bg: "bg-red-100" },
    { id: "CYCLONE_AMPHAN", name: "Category 5 Cyclone", icon: Wind, color: "text-teal-500", bg: "bg-teal-100" }
  ];

  const handleTrigger = async (scenarioId: string) => {
    setLoading(true);
    try {
      await apiClient.post("/simulation/start", {
        scenario_name: scenarioId,
        affected_zones: [1, 2, 3],
        population_affected: 200000,
        duration_days: 5
      });
      setLastTriggered(scenarioId);
      setTimeout(() => setLastTriggered(null), 3000);
    } catch (error) {
      console.error("Failed to trigger simulation", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
      <div className="bg-slate-900 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-500" />
          <h2 className="text-sm font-bold text-white tracking-wide">WAR ROOM SIMULATOR</h2>
        </div>
      </div>
      <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        {scenarios.map((s) => {
          const Icon = s.icon;
          const isTriggered = lastTriggered === s.id;
          return (
            <button
              key={s.id}
              onClick={() => handleTrigger(s.id)}
              disabled={loading}
              className={`flex items-center gap-3 p-3 rounded-lg border text-left transition-all ${
                isTriggered 
                  ? 'border-green-500 bg-green-50 shadow-md' 
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-md'
              }`}
            >
              <div className={`p-2 rounded-md ${s.bg}`}>
                <Icon className={`w-5 h-5 ${s.color}`} />
              </div>
              <div className="flex-1">
                <p className="text-xs font-bold text-slate-800">{s.name}</p>
                <p className="text-[10px] text-slate-500 mt-0.5">
                  {isTriggered ? 'Event Triggered!' : 'Click to simulate'}
                </p>
              </div>
              {!isTriggered && <Play className="w-4 h-4 text-slate-300" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import { AlertsFeed } from "@/components/dashboard/alerts-feed";
import { Bell, RefreshCw, ShieldAlert, CheckCircle2, Play } from "lucide-react";
import { apiClient } from "@/lib/api";

export default function AlertsPage() {
  const [running, setRunning] = useState(false);
  const [cycleMsg, setCycleMsg] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRunAssessmentCycle = async () => {
    setRunning(true);
    setCycleMsg(null);
    try {
      const res = await apiClient.post("/alerts/run_cycle");
      setCycleMsg(`Cycle executed: ${res.data.evaluated_zones} zones evaluated, ${res.data.new_alerts_generated} new alerts generated.`);
      setRefreshKey(prev => prev + 1);
    } catch (err: any) {
      setCycleMsg(`Assessment cycle failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Bell className="w-8 h-8 text-blue-600" />
            Live Intelligence & Alerts Stream
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Autonomous multi-zone threshold monitoring, stockout warnings & emergency event logs.
          </p>
        </div>

        <button
          onClick={handleRunAssessmentCycle}
          disabled={running}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold px-4 py-2.5 rounded-lg text-xs transition-all shadow disabled:opacity-60"
        >
          {running ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {running ? "Scanning Network..." : "Run Autonomous Assessment Cycle"}
        </button>
      </div>

      {cycleMsg && (
        <div className="p-4 bg-blue-50 border border-blue-200 text-blue-800 text-xs rounded-xl flex items-center gap-2 font-bold shadow-xs">
          <CheckCircle2 className="w-4 h-4 text-blue-600" />
          {cycleMsg}
        </div>
      )}

      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between pb-4 mb-4 border-b">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-600" />
            <h3 className="font-bold text-sm text-slate-900">Live Alert Events Log</h3>
          </div>
          <span className="text-xs text-slate-500">Auto-refreshing stream</span>
        </div>

        <AlertsFeed key={refreshKey} />
      </div>
    </div>
  );
}


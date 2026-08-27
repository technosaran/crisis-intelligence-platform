"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { 
  AlertCircle, 
  Package, 
  TrendingUp, 
  Truck, 
  Globe, 
  Database, 
  ShieldAlert, 
  Flame, 
  ArrowRight,
  RefreshCw
} from "lucide-react";
import { AlertsFeed } from "@/components/dashboard/alerts-feed";
import { SimulatorPanel } from "@/components/dashboard/simulator-panel";
import { apiClient } from "@/lib/api";
import { LineChart, Line, ResponsiveContainer } from "recharts";

const MapView = dynamic(() => import("@/components/dashboard/map-view"), {
  ssr: false,
});

export default function DashboardPage() {
  const sparklineData = [{v: 10}, {v: 15}, {v: 8}, {v: 25}, {v: 20}, {v: 30}, {v: 28}];
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [liveLocations, setLiveLocations] = useState<any[]>([]);
  const [loadingLive, setLoadingLive] = useState(false);

  const [summary, setSummary] = useState<any>(null);
  const [loadingSummary, setLoadingSummary] = useState(true);

  const fetchDashboardSummary = () => {
    setLoadingSummary(true);
    apiClient.get("/dashboard/summary")
      .then((res) => {
        setSummary(res.data);
      })
      .catch((err) => console.error("Error fetching summary:", err))
      .finally(() => setLoadingSummary(false));
  };

  useEffect(() => {
    fetchDashboardSummary();
    const interval = setInterval(fetchDashboardSummary, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isLiveMode) {
      setLoadingLive(true);
      apiClient.post("/simulation/fetch-live-earthquakes")
        .then((res) => {
          setLiveLocations(res.data.live_events);
        })
        .catch((err) => console.error("Error fetching live data:", err))
        .finally(() => setLoadingLive(false));
    } else {
      setLiveLocations([]);
    }
  }, [isLiveMode]);

  const [globalDisasters, setGlobalDisasters] = useState<any[]>([]);
  const [loadingGlobal, setLoadingGlobal] = useState(true);

  useEffect(() => {
    setLoadingGlobal(true);
    apiClient.get("/external/live-disasters")
      .then((res) => setGlobalDisasters(res.data?.slice(0, 5) || []))
      .catch((err) => console.error(err))
      .finally(() => setLoadingGlobal(false));
  }, []);

  const kpis = summary?.kpis || {
    critical_shortages: 3,
    total_warehouse_stock: 45000,
    active_deliveries: 6,
    projected_demand_7d: 58200,
    active_crises_count: 1
  };

  const mapLocations = isLiveMode ? liveLocations : (summary?.zones || []);

  return (
    <div className="flex flex-col gap-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">Crisis Operations Command</h2>
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
          </div>
          <p className="text-muted-foreground text-sm mt-1">
            Real-time multi-hazard telemetry, AI shortage prediction & autonomous dispatch.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboardSummary}
            className="p-2 rounded-lg border bg-white dark:bg-slate-900 hover:bg-slate-50 dark:bg-slate-800/50 text-slate-600 transition-all shadow-sm"
            title="Refresh Telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${loadingSummary ? 'animate-spin text-blue-600' : ''}`} />
          </button>

          {/* Mode Switcher */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-800">
            <button
              onClick={() => setIsLiveMode(false)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-bold transition-all ${
                !isLiveMode ? 'bg-white dark:bg-slate-900 shadow-sm text-blue-700' : 'text-slate-500 hover:text-slate-900 dark:text-slate-100'
              }`}
            >
              <Database className="w-3.5 h-3.5" />
              DB Telemetry
            </button>
            <button
              onClick={() => setIsLiveMode(true)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-bold transition-all ${
                isLiveMode ? 'bg-red-600 shadow-sm text-white' : 'text-slate-500 hover:text-slate-900 dark:text-slate-100'
              }`}
            >
              <Globe className="w-3.5 h-3.5" />
              USGS Global Live
            </button>
          </div>
        </div>
      </div>

      {/* Simulator Panel */}
      <SimulatorPanel />

      {/* Active Crisis Alert Banner if any */}
      {summary?.active_crises && summary.active_crises.length > 0 && !isLiveMode && (
        <div className="bg-gradient-to-r from-red-600 to-rose-700 text-white rounded-xl p-4 shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white dark:bg-slate-900/20 rounded-lg">
              <Flame className="w-6 h-6 animate-pulse text-amber-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-black bg-white dark:bg-slate-900/25 px-2 py-0.5 rounded tracking-widest">ACTIVE LEVEL 4 DISASTER</span>
                <span className="text-xs text-rose-200">Population Affected: {summary.active_crises[0].affected_population?.toLocaleString()}</span>
              </div>
              <h3 className="text-lg font-bold mt-0.5">{summary.active_crises[0].name}</h3>
            </div>
          </div>
          <div className="flex gap-2">
            <Link
              href="/decisions"
              className="flex items-center gap-1.5 bg-white dark:bg-slate-900 text-rose-800 hover:bg-rose-50 px-4 py-2 rounded-lg text-xs font-bold transition-all shadow"
            >
              Review AI Actions <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 dark:border-slate-800 bg-white dark:bg-slate-900 dark:bg-slate-900 shadow-sm p-5 flex flex-col justify-between border-l-4 border-l-red-500 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Critical Shortages</p>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-200 dark:text-slate-100 mt-1">
                {isLiveMode ? liveLocations.filter((l: any) => l.severity === "critical").length : kpis.critical_shortages}
              </h3>
              <p className="text-[11px] text-red-600 dark:text-red-400 font-semibold mt-1">High stockout risk</p>
            </div>
            <div className="p-2 bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 rounded-xl z-10">
              <AlertCircle className="w-5 h-5" />
            </div>
          </div>
          <div className="h-12 mt-4 -mx-2 -mb-2 opacity-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData}>
                <Line type="monotone" dataKey="v" stroke="#ef4444" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 dark:border-slate-800 bg-white dark:bg-slate-900 dark:bg-slate-900 shadow-sm p-5 flex flex-col justify-between border-l-4 border-l-blue-500 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Network Inventory</p>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-200 dark:text-slate-100 mt-1">
                {isLiveMode ? "N/A" : kpis.total_warehouse_stock.toLocaleString()}
              </h3>
              <p className="text-[11px] text-blue-600 dark:text-blue-400 font-semibold mt-1">Across 4 Strategic Hubs</p>
            </div>
            <div className="p-2 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-xl z-10">
              <Package className="w-5 h-5" />
            </div>
          </div>
          <div className="h-12 mt-4 -mx-2 -mb-2 opacity-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData.map(d => ({v: d.v * 1.5}))}>
                <Line type="monotone" dataKey="v" stroke="#3b82f6" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-800 dark:border-slate-800 bg-white dark:bg-slate-900 dark:bg-slate-900 shadow-sm p-5 flex flex-col justify-between border-l-4 border-l-emerald-500 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Active Nav Routes</p>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-200 dark:text-slate-100 mt-1">
                {isLiveMode ? "0" : kpis.active_deliveries}
              </h3>
              <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-1">A* graph routed</p>
            </div>
            <div className="p-2 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-xl z-10">
              <Truck className="w-5 h-5" />
            </div>
          </div>
          <div className="h-12 mt-4 -mx-2 -mb-2 opacity-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData.map(d => ({v: d.v * 0.8}))}>
                <Line type="monotone" dataKey="v" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-800 dark:border-slate-800 bg-white dark:bg-slate-900 dark:bg-slate-900 shadow-sm p-5 flex flex-col justify-between border-l-4 border-l-purple-500 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Projected 7D Demand</p>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-200 dark:text-slate-100 mt-1">
                {isLiveMode ? "Predicting..." : kpis.projected_demand_7d.toLocaleString()}
              </h3>
              <p className="text-[11px] text-purple-600 dark:text-purple-400 font-semibold mt-1">XGBoost & LSTM aggregated</p>
            </div>
            <div className="p-2 bg-purple-50 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-xl z-10">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="h-12 mt-4 -mx-2 -mb-2 opacity-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData.map(d => ({v: d.v * 2.2}))}>
                <Line type="monotone" dataKey="v" stroke="#8b5cf6" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>


      {/* Map & Live Alerts Section */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border bg-white dark:bg-slate-900 shadow-sm p-5 relative flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <Globe className="w-4 h-4 text-blue-600" />
                Live Situational GIS & Road Network
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">Interactive spatial view of regional depots, crisis sectors & dynamic status</p>
            </div>
            <div className="flex items-center gap-2 text-xs font-bold">
              <span className="flex items-center gap-1 text-red-600 bg-red-50 px-2 py-1 rounded border border-red-200">
                <span className="w-2 h-2 rounded-full bg-red-500"></span> Crisis
              </span>
              <span className="flex items-center gap-1 text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-200">
                <span className="w-2 h-2 rounded-full bg-blue-500"></span> Depot
              </span>
            </div>
          </div>
          
          {loadingLive ? (
            <div className="h-[420px] flex flex-col items-center justify-center border rounded-lg bg-slate-50 dark:bg-slate-800/50 gap-2">
              <Globe className="w-8 h-8 text-blue-500 animate-spin" />
              <p className="text-xs font-semibold text-slate-500">Connecting to USGS Global Seismic Feed...</p>
            </div>
          ) : (
            <MapView 
              locations={mapLocations} 
              routeCoordinates={summary?.active_routes?.[0]?.coordinates || []}
              routeColor={summary?.active_routes?.[0]?.color || "#2563eb"}
              height="420px" 
            />
          )}

          {/* Quick Zone Health Strip */}
          {summary?.zones && !isLiveMode && (
            <div className="mt-4 pt-4 border-t grid grid-cols-2 md:grid-cols-5 gap-2">
              {summary.zones.map((z: any) => (
                <div key={z.id} className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border text-xs">
                  <p className="font-bold text-slate-800 dark:text-slate-200 truncate">{z.name.split(' ')[0]} {(z.name.split(' ')[1] || '')}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Pop: {((z.population || 0) / 1000).toFixed(0)}k</p>
                  <span className={`inline-block mt-1 text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                    z.severity === 'critical' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                  }`}>
                    {z.severity}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Alerts Feed */}
        <div className="rounded-xl border bg-white dark:bg-slate-900 shadow-sm p-5 flex flex-col">
          <div className="flex justify-between items-center mb-4 pb-2 border-b">
            <div>
              <h3 className="text-base font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-red-600" />
                Live Intelligence Stream
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">Autonomous anomaly detection</p>
            </div>
            <Link href="/alerts" className="text-xs font-bold text-blue-600 hover:underline">
              View All
            </Link>
          </div>

          {isLiveMode ? (
            <div className="flex flex-col gap-3 overflow-y-auto max-h-[460px]">
              {liveLocations.map((event: any, i: number) => (
                <div key={event.id || i} className="border-l-4 border-red-500 pl-3 py-2 bg-red-50/60 rounded-r-md">
                  <p className="text-xs font-bold text-red-600">SEISMIC EVENT DETECTED</p>
                  <p className="text-xs text-slate-800 dark:text-slate-200 mt-0.5 font-medium">{event.name}</p>
                  <span className="text-[10px] text-slate-400 mt-1 block">Magnitude {event.mag} • USGS Live Feed</span>
                </div>
              ))}
            </div>
          ) : (
            <AlertsFeed />
          )}
        </div>
      </div>

      {/* Live Global Alerts (USGS/GDACS) */}
      <div className="rounded-xl border bg-white dark:bg-slate-900 shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4 pb-2 border-b">
          <Globe className="w-5 h-5 text-blue-600" />
          <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">Live Global Alerts (USGS/GDACS)</h3>
        </div>
        
        {loadingGlobal ? (
          <div className="text-center py-6 text-slate-400 text-xs animate-pulse">
            Fetching global disaster feed...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {globalDisasters.length > 0 ? (
              globalDisasters.map((disaster: any, i: number) => (
                <div key={i} className="border border-slate-200 dark:border-slate-800 rounded-lg p-3 bg-slate-50 dark:bg-slate-800/50">
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 mb-1 line-clamp-2">{disaster.title || disaster.name || "Unknown Event"}</h4>
                  <p className="text-[10px] text-slate-500 mb-2">{new Date(disaster.time || disaster.date || Date.now()).toLocaleString()}</p>
                  <span className="inline-block bg-red-100 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded">
                    {disaster.type || "ALERT"}
                  </span>
                </div>
              ))
            ) : (
              <div className="col-span-full text-center py-6 text-slate-400 text-xs">
                No active global disasters found.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}


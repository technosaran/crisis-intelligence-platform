"use client";

import { useEffect, useState, useMemo } from "react";
import { apiClient } from "@/lib/api";
import { AlertCircle, AlertTriangle, Info, MapPin, Clock, Wifi, WifiOff, ShieldAlert } from "lucide-react";
import { useWebSockets } from "@/hooks/useWebSockets";

interface Alert {
  id: number | string;
  type: string;
  severity: string;
  message: string;
  location: string;
  created_at: string;
  is_sos?: boolean;
}

export function AlertsFeed() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");
  
  // Use WS for real-time updates
  const wsUrl = typeof window !== 'undefined' 
    ? `${(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1').replace(/^http/, 'ws')}/ws/alerts`
    : '';
  const { messages: wsMessages, isConnected } = useWebSockets(wsUrl);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await apiClient.get("/alerts/?limit=20");
        setAlerts(response.data || []);
      } catch (error) {
        console.error("Failed to fetch alerts:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
    // Keep a slow fallback poll in case WS drops
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  // Merge historical alerts with new WS alerts
  const combinedAlerts = useMemo(() => {
    const newAlerts = wsMessages
      .filter((m) => m.event_type === "NEW_ALERT" || m.event_type === "NEW_SOS")
      .map((m, idx) => ({ 
        ...m.data, 
        is_sos: m.event_type === "NEW_SOS",
        id: `ws-${m.data?.message?.slice(0, 20) || idx}-${m.data?.created_at || idx}` 
      }));
    
    // De-dupe based on message/location/timestamp roughly
    const combined = [...newAlerts, ...alerts];
    const unique = combined.filter((v, i, a) => a.findIndex(t => (t.id === v.id)) === i);
    return unique;
  }, [alerts, wsMessages]);

  if (loading && combinedAlerts.length === 0) {
    return (
      <div className="py-8 text-center text-slate-400 text-xs animate-pulse">
        Connecting to alert event bus...
      </div>
    );
  }

  const filteredAlerts = filter === "ALL" 
    ? combinedAlerts 
    : combinedAlerts.filter(a => a.severity === filter || (filter === "CRITICAL" && a.is_sos));

  return (
    <div className="flex flex-col gap-3">
      {/* Quick Filter Tabs & WS Status */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex gap-2 text-xs">
          {["ALL", "CRITICAL", "WARNING", "INFO"].map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-3 py-1 rounded-md font-bold text-[11px] transition-all ${
                filter === tab
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1 text-[10px] font-bold px-2 py-1 bg-slate-100 rounded-md">
          {isConnected ? (
            <><Wifi className="w-3 h-3 text-green-500 animate-pulse" /><span className="text-green-600">LIVE</span></>
          ) : (
            <><WifiOff className="w-3 h-3 text-slate-400" /><span className="text-slate-500">POLLING</span></>
          )}
        </div>
      </div>

      {filteredAlerts.length === 0 && (
        <div className="py-8 text-center text-slate-400 text-xs">
          No active alerts under &apos;{filter}&apos; filter.
        </div>
      )}

      <div className="flex flex-col gap-2.5 max-h-[460px] overflow-y-auto pr-1" role="log" aria-live="polite">
        {filteredAlerts.map((alert) => {
          const isSOS = alert.is_sos;
          const isCritical = alert.severity === "CRITICAL" || isSOS;
          const isWarning = alert.severity === "WARNING" && !isSOS;
          const isNew = String(alert.id).startsWith("ws-");

          return (
            <div 
              key={alert.id} 
              className={`border-l-4 p-3.5 rounded-r-xl transition-all shadow-xs ${isNew ? 'animate-in slide-in-from-left-2 fade-in duration-500' : ''} ${
                isSOS 
                  ? 'border-red-600 bg-red-100 animate-pulse'
                  : isCritical 
                  ? 'border-red-500 bg-red-50/70' 
                  : isWarning 
                  ? 'border-amber-500 bg-amber-50/70' 
                  : 'border-blue-500 bg-blue-50/70'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <div className="flex items-center gap-1.5">
                  {isSOS ? (
                    <ShieldAlert className="w-5 h-5 text-red-700 animate-bounce" />
                  ) : isCritical ? (
                    <AlertCircle className="w-4 h-4 text-red-600" />
                  ) : isWarning ? (
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                  ) : (
                    <Info className="w-4 h-4 text-blue-600" />
                  )}
                  <span className={`text-xs font-black uppercase tracking-wider ${
                    isSOS ? 'text-red-800' : isCritical ? 'text-red-700' : isWarning ? 'text-amber-700' : 'text-blue-700'
                  }`}>
                    {isSOS ? "SOS EMERGENCY" : alert.type?.replace(/_/g, " ")}
                  </span>
                  {isNew && <span className="ml-1 w-2 h-2 rounded-full bg-blue-500 animate-pulse" />}
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                  isSOS ? 'bg-red-600 text-white' : isCritical ? 'bg-red-200 text-red-800' : isWarning ? 'bg-amber-200 text-amber-800' : 'bg-blue-200 text-blue-800'
                }`}>
                  {isSOS ? 'CRITICAL' : alert.severity}
                </span>
              </div>

              <p className="text-xs text-slate-800 font-medium leading-relaxed">{alert.message}</p>

              <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2 pt-2 border-t border-slate-200/60 font-mono">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-slate-400" /> {alert.location}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


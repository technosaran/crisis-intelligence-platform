"use client";

import { useState, useEffect, useRef } from "react";
import dynamic from "next/dynamic";
import { apiClient } from "@/lib/api";
import { 
  MapPin, 
  Truck, 
  Clock, 
  Navigation, 
  AlertCircle, 
  Activity, 
  ShieldAlert, 
  Compass, 
  Route as RouteIcon,
  Layers,
  Play,
  Pause,
  RotateCcw
} from "lucide-react";

import { useWebSockets } from "@/hooks/useWebSockets";

const MapView = dynamic(() => import("@/components/dashboard/map-view"), {
  ssr: false,
});

export default function RoutingPage() {
  const [routeMode, setRouteMode] = useState<"direct" | "convoy">("direct");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [detourData, setDetourData] = useState<any>(null);
  const [isDetourMode, setIsDetourMode] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [locations, setLocations] = useState<any[]>([]);
  const [sourceId, setSourceId] = useState("1");
  const [destId, setDestId] = useState("3");
  const [selectedStops, setSelectedStops] = useState<number[]>([2, 3, 5]);
  const [algorithm, setAlgorithm] = useState("astar");
  const [objective, setObjective] = useState("fastest");

  // Convoy Animation State
  const [isAnimating, setIsAnimating] = useState(false);
  const [animProgress, setAnimProgress] = useState(0);
  const [truckPos, setTruckPos] = useState<[number, number] | null>(null);
  const animRef = useRef<any>(null);

  useEffect(() => {
    return () => {
      if (animRef.current) clearInterval(animRef.current);
    };
  }, []);

  useEffect(() => {
    apiClient.get("/simulation/info")
      .then(res => setLocations(res.data.locations || []))
      .catch(err => console.error("Failed to load locations", err));
  }, []);

  const handleRoute = async () => {
    setLoading(true);
    setError(null);
    setIsDetourMode(false);
    setDetourData(null);
    stopAnimation();

    try {
      if (routeMode === "direct") {
        if (sourceId === destId) {
          setError("Source and destination cannot be the same.");
          setLoading(false);
          return;
        }
        const payload = {
          source_location_id: parseInt(sourceId),
          destination_location_id: parseInt(destId),
          algorithm: algorithm,
          objective: objective
        };
        const res = await apiClient.post("/routing/calculate", payload);
        setData(res.data);
      } else {
        if (selectedStops.length === 0) {
          setError("Please select at least one drop-off zone.");
          setLoading(false);
          return;
        }
        const payload = {
          origin_id: parseInt(sourceId),
          stop_ids: selectedStops,
          objective: objective
        };
        const res = await apiClient.post("/routing/convoy-tour", payload);
        setData(res.data);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Network graph incomplete. No navigable route found.");
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateBlockade = async () => {
    if (!data || !data.path || data.path.length < 2) return;
    
    setLoading(true);
    setError(null);
    stopAnimation();
    try {
      const blockedEdge = {
        source_id: data.path[0],
        destination_id: data.path[1]
      };

      const payload = {
        source_location_id: parseInt(sourceId),
        destination_location_id: parseInt(destId),
        blocked_edges: [blockedEdge],
        algorithm: algorithm,
        objective: objective
      };
      
      const res = await apiClient.post("/routing/reroute", payload);
      setDetourData(res.data);
      setIsDetourMode(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Target zone is completely isolated by disaster blockades.");
    } finally {
      setLoading(false);
    }
  };

  const activeRouteData = isDetourMode && detourData ? detourData : data;
  const routeCoordinates = activeRouteData?.route_coordinates || [];

  // Animation controller
  const wsUrl = process.env.NEXT_PUBLIC_API_URL?.replace("http", "ws") || "ws://localhost:8000/api/v1";
  const { messages: wsMessages } = useWebSockets(`${wsUrl}/ws/alerts`);
  const [activeTrucks, setActiveTrucks] = useState<Record<string, [number, number]>>({});

  useEffect(() => {
    // Process incoming GPS telemetry
    const gpsEvents = wsMessages.filter(m => m.event_type === "TRUCK_GPS");
    if (gpsEvents.length > 0) {
      const latest = gpsEvents[gpsEvents.length - 1].data;
      if (latest && latest.lat && latest.lng) {
        setTruckPos([latest.lat, latest.lng]);
        setAnimProgress(latest.progress_percent || 0);
        setIsAnimating(true);
      }
    }

    const arriveEvents = wsMessages.filter(m => m.event_type === "CONVOY_ARRIVED");
    if (arriveEvents.length > 0) {
      setIsAnimating(false);
      setAnimProgress(100);
    }
  }, [wsMessages]);

  const startAnimation = async () => {
    if (routeCoordinates.length < 2) return;
    setIsAnimating(true);
    setAnimProgress(0);
    try {
      await apiClient.post("/routing/dispatch", { route_coordinates: routeCoordinates });
    } catch (e) {
      console.error("Failed to dispatch convoy", e);
      setIsAnimating(false);
    }
  };

  const stopAnimation = () => {
    setIsAnimating(false);
  };

  const resetAnimation = () => {
    stopAnimation();
    setAnimProgress(0);
    if (routeCoordinates.length > 0) {
      setTruckPos(routeCoordinates[0]);
    } else {
      setTruckPos(null);
    }
  };

  const toggleStop = (id: number) => {
    if (selectedStops.includes(id)) {
      setSelectedStops(selectedStops.filter(s => s !== id));
    } else {
      setSelectedStops([...selectedStops, id]);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Navigation className="w-8 h-8 text-emerald-600" />
            Autonomous Logistics & Multi-Stop Fleet Routing
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Constrained Shortest Path (A* / Dijkstra) & Multi-Stop Convoy Tour with live transit telemetry.
          </p>
        </div>

        <div className="flex items-center bg-slate-200/80 p-1 rounded-lg border border-slate-300">
          <button
            onClick={() => setRouteMode("direct")}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
              routeMode === "direct" ? 'bg-white shadow text-emerald-700' : 'text-slate-600'
            }`}
          >
            Direct Nav Leg
          </button>
          <button
            onClick={() => setRouteMode("convoy")}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
              routeMode === "convoy" ? 'bg-white shadow text-emerald-700' : 'text-slate-600'
            }`}
          >
            Multi-Stop Convoy Tour (TSP)
          </button>
        </div>
      </div>

      {/* Control Panel */}
      <div className="rounded-xl border bg-slate-900 text-slate-100 p-5 shadow-lg space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Origin Base Depot</label>
            <select 
              value={sourceId} 
              onChange={e => setSourceId(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-xs font-semibold focus:outline-none focus:border-emerald-500"
            >
              {locations.map(l => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </select>
          </div>
          
          {routeMode === "direct" ? (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Target Destination</label>
              <select 
                value={destId} 
                onChange={e => setDestId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-xs font-semibold focus:outline-none focus:border-emerald-500"
              >
                {locations.map(l => (
                  <option key={l.id} value={l.id}>{l.name}</option>
                ))}
              </select>
            </div>
          ) : (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Selected Drop-offs</label>
              <div className="p-2.5 rounded-lg bg-slate-800 border border-slate-700 text-xs font-mono text-emerald-400 font-bold">
                {selectedStops.length} Destination Zones Selected
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Optimization Criterion</label>
            <select 
              value={objective} 
              onChange={e => setObjective(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-xs font-semibold focus:outline-none focus:border-emerald-500"
            >
              <option value="fastest">Fastest Travel Time</option>
              <option value="safest">Safest (Hazard-Averse)</option>
              <option value="shortest">Shortest Physical Distance</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Pathfinding Algorithm</label>
            <select 
              value={algorithm} 
              onChange={e => setAlgorithm(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-xs font-semibold focus:outline-none focus:border-emerald-500"
            >
              <option value="astar">A* (Heuristic Optimal)</option>
              <option value="dijkstra">Dijkstra (Exhaustive Optimal)</option>
            </select>
          </div>

          <button 
            onClick={handleRoute}
            disabled={loading}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-lg font-bold transition-all shadow-md flex items-center justify-center gap-2 text-xs disabled:opacity-50 h-[38px] uppercase tracking-wider"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Compass className="w-4 h-4" />}
            {loading ? "Solving Spatial Graph..." : routeMode === "convoy" ? "Plot Convoy Tour" : "Plot Convoy Route"}
          </button>
        </div>

        {/* Multi-stop Zone Selector Pill Strip in Convoy Mode */}
        {routeMode === "convoy" && (
          <div className="pt-3 border-t border-slate-800">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              Select Disaster Zones to Include in Convoy Drop-Off Tour:
            </p>
            <div className="flex flex-wrap gap-2">
              {locations.map(loc => {
                const isSelected = selectedStops.includes(loc.id);
                return (
                  <button
                    key={loc.id}
                    onClick={() => toggleStop(loc.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                      isSelected
                        ? 'bg-emerald-600 text-white shadow ring-2 ring-emerald-400/40'
                        : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
                    }`}
                  >
                    {isSelected ? '✓ ' : '+ '} {loc.name}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-xl flex items-start gap-3 shadow-sm">
          <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
          <div>
            <h3 className="text-red-800 font-bold text-sm">Logistics Routing Engine Notice</h3>
            <p className="text-red-700 text-xs mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Main Interactive Map & Manifest Layout */}
      {activeRouteData && !loading && (
        <>
          {/* Stats Bar */}
          <div className="grid gap-4 md:grid-cols-4">
            <div className="rounded-xl border bg-white p-5 flex items-center gap-4 shadow-sm border-l-4 border-l-emerald-500">
              <div className="p-3 bg-emerald-50 rounded-xl text-emerald-600">
                <Truck className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Route Distance</p>
                <h3 className="text-2xl font-black text-slate-900">{activeRouteData.total_distance} <span className="text-xs text-slate-400 font-normal">km</span></h3>
              </div>
            </div>

            <div className="rounded-xl border bg-white p-5 flex items-center gap-4 shadow-sm border-l-4 border-l-amber-500">
              <div className="p-3 bg-amber-50 rounded-xl text-amber-600">
                <Clock className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Estimated Transit</p>
                <h3 className="text-2xl font-black text-slate-900">{activeRouteData.estimated_time_minutes} <span className="text-xs text-slate-400 font-normal">mins</span></h3>
              </div>
            </div>

            <div className="rounded-xl border bg-white p-5 flex items-center gap-4 shadow-sm border-l-4 border-l-blue-500">
              <div className="p-3 bg-blue-50 rounded-xl text-blue-600">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Hazard Exposure Risk</p>
                <h3 className="text-2xl font-black text-slate-900">{((activeRouteData.average_risk_score || 0.1) * 100).toFixed(0)}%</h3>
              </div>
            </div>

            <div className="rounded-xl border bg-white p-5 flex flex-col justify-between shadow-sm border-l-4 border-l-purple-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Live Convoy Sim</p>
                  <p className="text-xs text-slate-500 font-mono">Progress: {animProgress}%</p>
                </div>
                {isAnimating && <span className="animate-ping w-2 h-2 rounded-full bg-emerald-500"></span>}
              </div>

              <div className="flex gap-2 mt-2">
                {!isAnimating ? (
                  <button
                    onClick={startAnimation}
                    className="flex-1 flex items-center justify-center gap-1 bg-emerald-600 hover:bg-emerald-500 text-white px-2.5 py-1.5 rounded-lg text-xs font-bold shadow"
                  >
                    <Play className="w-3.5 h-3.5" /> Start Convoy
                  </button>
                ) : (
                  <button
                    onClick={stopAnimation}
                    className="flex-1 flex items-center justify-center gap-1 bg-amber-600 hover:bg-amber-500 text-white px-2.5 py-1.5 rounded-lg text-xs font-bold shadow"
                  >
                    <Pause className="w-3.5 h-3.5" /> Pause
                  </button>
                )}
                <button
                  onClick={resetAnimation}
                  className="p-1.5 rounded-lg border bg-slate-50 hover:bg-slate-100 text-slate-600 text-xs"
                  title="Reset Convoy"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* GIS Interactive Spatial Map & Waypoint List */}
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Map */}
            <div className="lg:col-span-2 rounded-xl border bg-white shadow-sm p-5 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
                    <RouteIcon className="w-4 h-4 text-emerald-600" />
                    Spatial Trajectory & Real-Time Convoy Simulation
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {routeMode === "convoy" ? "Optimized Multi-Stop Traveling Delivery Sequence" : "Direct Point-to-Point Emergency Dispatch"}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  {routeMode === "direct" && (
                    <button
                      onClick={handleSimulateBlockade}
                      disabled={isDetourMode}
                      className={`text-xs font-bold px-2.5 py-1 rounded transition-all ${
                        isDetourMode 
                          ? 'bg-amber-100 text-amber-800 border border-amber-300' 
                          : 'bg-red-50 text-red-700 hover:bg-red-100 border border-red-200'
                      }`}
                    >
                      {isDetourMode ? "Detour Applied" : "Simulate Bridge Closure"}
                    </button>
                  )}
                  {isDetourMode && (
                    <span className="text-xs bg-red-100 text-red-700 font-bold px-2 py-1 rounded border border-red-200 animate-pulse">
                      DETOUR ACTIVE
                    </span>
                  )}
                </div>
              </div>

              <MapView 
                locations={locations} 
                routeCoordinates={routeCoordinates}
                routeColor={isDetourMode ? "#ef4444" : "#10b981"}
                truckPosition={truckPos}
                height="450px"
              />
            </div>

            {/* Turn-by-Turn Waypoint Manifest */}
            <div className="rounded-xl border bg-white shadow-sm p-5 flex flex-col">
              <h3 className="text-base font-bold text-slate-800 mb-1 flex items-center gap-2">
                <Layers className="w-4 h-4 text-blue-600" />
                Turn-by-Turn Manifest
              </h3>
              <p className="text-xs text-slate-500 mb-4 pb-3 border-b">Sequential transit stops</p>

              <div className="flex-1 overflow-y-auto space-y-4 max-h-[400px]">
                {activeRouteData.waypoints?.map((wp: any, i: number) => {
                  const isStart = i === 0;
                  const isEnd = i === activeRouteData.waypoints.length - 1;

                  return (
                    <div key={`${wp.id}-${i}`} className="flex gap-3 items-start relative">
                      {i < activeRouteData.waypoints.length - 1 && (
                        <div className="absolute left-4 top-8 bottom-0 w-0.5 bg-slate-200"></div>
                      )}
                      <div className={`rounded-full p-2 text-white font-bold text-xs ${
                        isStart ? 'bg-blue-600' : isEnd ? 'bg-emerald-600' : 'bg-slate-700'
                      }`}>
                        <MapPin className="w-4 h-4" />
                      </div>
                      <div className="flex-1 p-3 rounded-lg border bg-slate-50">
                        <div className="flex justify-between items-center">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                            {isStart ? "Origin Base" : isEnd ? "Final Destination" : `Stop ${i}`}
                          </span>
                          <span className="text-[10px] font-mono text-slate-500">ID: {wp.id}</span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-900 mt-0.5">{wp.name}</h4>
                        <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                          {wp.lat?.toFixed(3) ?? 'N/A'}° N, {wp.lng?.toFixed(3) ?? 'N/A'}° E
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-4 pt-3 border-t flex justify-between items-center text-xs text-slate-500">
                <span>Objective: <strong className="text-slate-800">{activeRouteData.algorithm_used}</strong></span>
                <span className="text-emerald-700 font-bold">Nav Check OK</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}



"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";
import { 
  Package, 
  AlertTriangle, 
  CheckCircle, 
  Activity, 
  BarChart3, 
  Database, 
  Scale, 
  Download, 
  Truck, 
  Layers
} from "lucide-react";

export default function AllocationPage() {
  const [mode, setMode] = useState<"multi" | "single">("multi");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  
  const [resources, setResources] = useState<any[]>([]);
  const [resourceId, setResourceId] = useState("1");
  const [supply, setSupply] = useState("12500");
  const [fairnessRatio, setFairnessRatio] = useState(0.20);
  
  const [liveDemands, setLiveDemands] = useState<any[]>([]);
  const [fetchingLive, setFetchingLive] = useState(false);

  useEffect(() => {
    apiClient.get("/simulation/info")
      .then(res => setResources(res.data.resources || []))
      .catch(err => console.error("Failed to load resources", err));
  }, []);

  // Fetch live state when resource changes
  useEffect(() => {
    if (!resourceId) return;
    setFetchingLive(true);
    apiClient.get(`/allocation/live-state/${resourceId}`)
      .then(res => {
        setSupply((res.data.total_available_supply || 12500).toString());
        setLiveDemands(res.data.demands || []);
      })
      .catch(err => console.error("Failed to fetch live state", err))
      .finally(() => setFetchingLive(false));
  }, [resourceId]);

  const handleRunOptimizer = async () => {
    setLoading(true);
    setData(null);
    try {
      if (mode === "multi") {
        const res = await apiClient.post("/allocation/multi-warehouse-optimize", {
          resource_id: parseInt(resourceId),
          fairness_ratio: fairnessRatio
        });
        setData(res.data);
      } else {
        const payload = {
          resource_id: parseInt(resourceId),
          total_available_supply: parseFloat(supply),
          demands: liveDemands.length > 0 ? liveDemands : [
            { location_id: 1, location_name: "Zone A", demand: 4500, priority_score: 92.0 },
            { location_id: 3, location_name: "Zone C", demand: 3800, priority_score: 85.0 },
            { location_id: 4, location_name: "Zone D", demand: 2900, priority_score: 78.0 },
            { location_id: 5, location_name: "Zone E", demand: 4100, priority_score: 88.0 },
          ]
        };
        const res = await apiClient.post(`/allocation/optimize?fairness_ratio=${fairnessRatio}`, payload);
        setData(res.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportManifest = () => {
    if (!data) return;
    const manifest = {
      generated_at: new Date().toISOString(),
      resource_id: resourceId,
      fairness_ratio: fairnessRatio,
      total_allocated: data.total_allocated,
      total_unmet: data.total_unmet_demand,
      allocations: data.allocations,
      shipping_routes: data.shipping_matrix || []
    };

    const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Relief_Allocation_Manifest_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
  };



  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Scale className="w-8 h-8 text-blue-600" />
            Autonomous Resource Allocation Optimizer
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Bounded Linear Programming (GLOP) with Multi-Warehouse Transportation & Fairness Guarantees.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {data && (
            <button
              onClick={handleExportManifest}
              className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white px-3.5 py-2 rounded-lg text-xs font-bold transition-all shadow"
            >
              <Download className="w-4 h-4 text-blue-400" />
              Export Manifest
            </button>
          )}

          <div className="flex items-center bg-slate-200/80 p-1 rounded-lg border border-slate-300">
            <button
              onClick={() => setMode("multi")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                mode === "multi" ? 'bg-white shadow text-blue-700' : 'text-slate-600'
              }`}
            >
              Multi-Depot Transportation
            </button>
            <button
              onClick={() => setMode("single")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                mode === "single" ? 'bg-white shadow text-blue-700' : 'text-slate-600'
              }`}
            >
              Single Pool LP
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Controls Bar */}
      <div className="rounded-xl border bg-slate-900 text-slate-100 p-5 shadow-lg grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-blue-400" /> Resource Category
          </label>
          <select 
            value={resourceId} 
            onChange={e => setResourceId(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-xs font-semibold focus:outline-none focus:border-blue-500"
          >
            {resources.map(r => (
              <option key={r.id} value={r.id}>{r.name} ({r.category})</option>
            ))}
          </select>
        </div>

        {mode === "single" ? (
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Network Supply Buffer</label>
            <input 
              type="number"
              value={supply} 
              onChange={e => setSupply(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-xs font-mono font-bold"
            />
          </div>
        ) : (
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Depot Strategic Sources</label>
            <div className="p-2.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-blue-300 font-mono font-bold">
              4 Strategic Regional Warehouses
            </div>
          </div>
        )}

        <div>
          <div className="flex justify-between text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
            <span>Fairness Guarantee (α):</span>
            <span className="text-blue-400 font-mono">{(fairnessRatio * 100).toFixed(0)}%</span>
          </div>
          <input 
            type="range" 
            min={0.0} 
            max={0.40} 
            step={0.05}
            value={fairnessRatio}
            onChange={e => setFairnessRatio(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
        </div>

        <button 
          onClick={handleRunOptimizer}
          disabled={loading || fetchingLive}
          className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-lg font-bold transition-all shadow-md flex items-center justify-center gap-2 text-xs disabled:opacity-50 h-[38px] uppercase tracking-wider"
        >
          {loading ? <Activity className="w-4 h-4 animate-spin" /> : <BarChart3 className="w-4 h-4" />}
          {loading ? "Solving Linear Program..." : "Solve Allocation LP"}
        </button>
      </div>

      {!data && !loading && (
        <div className="rounded-xl border bg-white p-12 shadow-sm flex flex-col items-center justify-center text-center">
          <Scale className="w-14 h-14 text-slate-300 mb-3" />
          <h3 className="text-lg font-bold text-slate-800">Optimization Engine Standing By</h3>
          <p className="text-xs text-slate-500 max-w-md mt-1">
            Click <strong>Solve Allocation LP</strong> above to run Google OR-Tools Simplex Solver against live inventory buffers and priority weight functions.
          </p>
        </div>
      )}

      {data && !loading && (
        <>
          {/* Summary KPIs */}
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border bg-white p-5 flex items-center gap-4 shadow-sm border-l-4 border-l-blue-600">
              <div className="p-3 bg-blue-50 rounded-xl text-blue-600">
                <Package className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Allocated</p>
                <h3 className="text-2xl font-black text-slate-900">{data.total_allocated?.toLocaleString()} <span className="text-xs text-slate-400 font-normal">units</span></h3>
              </div>
            </div>

            <div className="rounded-xl border bg-white p-5 flex items-center gap-4 shadow-sm border-l-4 border-l-emerald-500">
              <div className="p-3 bg-emerald-50 rounded-xl text-emerald-600">
                <CheckCircle className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Fulfillment Ratio</p>
                <h3 className="text-2xl font-black text-slate-900">
                  {(() => {
                    const totalDemand = data.total_demand || data.allocations?.reduce((sum: number, a: any) => sum + (a.allocated_amount || 0) + (a.unmet_demand || 0), 0) || 0;
                    return totalDemand > 0 ? ((data.total_allocated / totalDemand) * 100).toFixed(1) : '100';
                  })()}%
                </h3>
              </div>
            </div>

            <div className="rounded-xl border bg-white p-5 flex items-center gap-4 shadow-sm border-l-4 border-l-red-500">
              <div className="p-3 bg-red-50 rounded-xl text-red-600">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Unmet Deficit</p>
                <h3 className="text-2xl font-black text-red-600">{data.total_unmet_demand?.toLocaleString()} <span className="text-xs text-slate-400 font-normal">units</span></h3>
              </div>
            </div>
          </div>

          {/* Multi-Warehouse Transportation Dispatch Matrix */}
          {data.shipping_matrix && data.shipping_matrix.length > 0 && (
            <div className="rounded-xl border bg-white shadow-sm overflow-hidden">
              <div className="p-5 border-b bg-slate-50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Truck className="w-5 h-5 text-blue-600" />
                  <h3 className="font-bold text-sm text-slate-900">Multi-Warehouse Transportation & Routing Plan</h3>
                </div>
                <span className="text-xs font-semibold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded">
                  Distance-Cost Penalties Minimized
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="text-[11px] text-slate-500 uppercase bg-slate-100/70 border-b">
                    <tr>
                      <th className="px-6 py-3">Origin Warehouse</th>
                      <th className="px-6 py-3">Destination Relief Zone</th>
                      <th className="px-6 py-3">Shipped Quantity</th>
                      <th className="px-6 py-3">Transit Distance</th>
                      <th className="px-6 py-3">Dispatch Directive</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {data.shipping_matrix.map((route: any, i: number) => (
                      <tr key={`${route.warehouse_name}-${route.location_name}-${i}`} className="hover:bg-slate-50">
                        <td className="px-6 py-3.5 font-bold text-slate-800">{route.warehouse_name}</td>
                        <td className="px-6 py-3.5 font-bold text-blue-700">{route.location_name}</td>
                        <td className="px-6 py-3.5 font-mono font-bold text-slate-900">{route.shipped_amount.toLocaleString()} units</td>
                        <td className="px-6 py-3.5 font-mono text-slate-600">{route.distance_km} km</td>
                        <td className="px-6 py-3.5">
                          <span className="text-[10px] bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded uppercase">
                            AUTONOMOUS DISPATCH
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Zone Fulfillment Progress Cards */}
          <div className="rounded-xl border bg-white shadow-sm overflow-hidden p-6">
            <div className="flex justify-between items-center pb-4 mb-4 border-b">
              <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
                <Layers className="w-5 h-5 text-blue-600" />
                Zone-by-Zone Fulfillment Under Priority & Fairness Constraints
              </h3>
              <span className="text-xs text-slate-500 font-mono">GLOP LP Optimal Solution</span>
            </div>

            <div className="grid gap-5">
              {data.allocations?.map((a: any, i: number) => (
                <div key={a.location_id || a.location_name || i} className="p-4 rounded-xl border bg-slate-50/60 space-y-2">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-sm text-slate-900">{a.location_name}</h4>
                        <span className="text-[10px] bg-slate-200 text-slate-700 font-bold px-1.5 py-0.5 rounded">
                          Priority Score: {a.priority_score?.toFixed(0)}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Requested: {((a.allocated_amount || 0) + (a.unmet_demand || 0)).toLocaleString()} units
                      </p>
                    </div>

                    <div className="text-right">
                      <span className="text-base font-bold text-blue-700 font-mono">
                        {a.allocated_amount?.toLocaleString()}
                      </span>
                      <span className="text-xs text-slate-500 ml-1">units allocated</span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden flex">
                    <div 
                      className="bg-blue-600 h-3 transition-all duration-700" 
                      style={{ width: `${a.fulfilled_percentage}%` }}
                    ></div>
                    <div 
                      className="bg-red-400 h-3 transition-all duration-700 opacity-60" 
                      style={{ width: `${100 - a.fulfilled_percentage}%` }}
                    ></div>
                  </div>

                  <div className="flex justify-between text-xs font-semibold text-slate-600 pt-1">
                    <span className="text-blue-700">{a.fulfilled_percentage}% Fulfilled</span>
                    {a.unmet_demand > 0 ? (
                      <span className="text-red-600 flex items-center gap-1 font-bold">
                        <AlertTriangle className="w-3.5 h-3.5" /> Deficit: {a.unmet_demand.toLocaleString()} units
                      </span>
                    ) : (
                      <span className="text-emerald-600 font-bold flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5" /> Fully Fulfilled
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}


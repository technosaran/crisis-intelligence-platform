"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";
import { 
  PlayCircle, 
  Globe, 
  Activity, 
  AlertTriangle, 
  Sliders, 
  CheckCircle2,
  ShieldCheck
} from "lucide-react";

export default function SimulationPage() {
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selectedScenarioKey, setSelectedScenarioKey] = useState("CHENNAI_FLOOD");
  
  const [popAffected, setPopAffected] = useState(300000);
  const [durationDays, setDurationDays] = useState(7);
  const [affectedZones, setAffectedZones] = useState<number[]>([1, 2, 3]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [locations, setLocations] = useState<any[]>([]);

  useEffect(() => {
    apiClient.get("/simulation/info")
      .then(res => setLocations(res.data.locations || []))
      .catch(console.error);
  }, []);

  const toggleZone = (id: number) => {
    if (affectedZones.includes(id)) {
      setAffectedZones(affectedZones.filter(z => z !== id));
    } else {
      setAffectedZones([...affectedZones, id]);
    }
  };

  useEffect(() => {
    apiClient.get("/simulation/scenarios")
      .then(res => {
        setScenarios(res.data || []);
      })
      .catch(console.error);
  }, []);

  const activeScenario = scenarios.find(s => s.id === selectedScenarioKey) || {
    id: "CHENNAI_FLOOD",
    title: "Chennai Urban Flash Floods",
    type: "Flood",
    severity: "CRITICAL",
    description: "Massive monsoon depression causing urban inundation of low-lying sectors. Water contamination and critical shortage of Insulin and potable water across northern wards.",
    multipliers: { Medical: 3.8, Food: 2.2, Shelter: 3.5, Water: 4.5 },
    default_affected_population: 320000,
    default_duration_days: 7
  };

  const handleSelectScenario = (sc: any) => {
    setSelectedScenarioKey(sc.id);
    if (sc.default_affected_population) setPopAffected(sc.default_affected_population);
    if (sc.default_duration_days) setDurationDays(sc.default_duration_days);
  };

  const handleStart = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await apiClient.post("/simulation/start", {
        scenario_name: selectedScenarioKey,
        affected_zones: affectedZones,
        population_affected: popAffected,
        duration_days: durationDays
      });
      setResult(res.data);
    } catch (err: any) {
      setResult({ error: err.response?.data?.detail || err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <PlayCircle className="w-8 h-8 text-blue-600" />
            Disaster Simulation Sandbox
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Inject controlled crisis shocks to validate Demand Forecasting, LP Allocation & Graph Routing models.
          </p>
        </div>
      </div>

      {/* Scenario Selection Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {scenarios.map((sc) => {
          const isSelected = sc.id === selectedScenarioKey;
          return (
            <div
              key={sc.id}
              onClick={() => handleSelectScenario(sc)}
              className={`rounded-xl border p-4 cursor-pointer transition-all flex flex-col justify-between ${
                isSelected
                  ? 'border-blue-600 bg-blue-50/50 shadow-md ring-2 ring-blue-500/20'
                  : 'bg-white hover:border-slate-300 hover:shadow-sm'
              }`}
            >
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                    sc.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    {sc.type}
                  </span>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-600" />}
                </div>
                <h4 className="font-bold text-sm text-slate-900">{sc.title}</h4>
                <p className="text-xs text-slate-500 line-clamp-2 mt-1">{sc.description}</p>
              </div>
              <div className="mt-3 pt-2 border-t text-[11px] text-slate-400 font-mono">
                Duration: {sc.default_duration_days || 7} Days
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Scenario Configuration & Deployer */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Configuration Panel */}
        <div className="rounded-xl border bg-white shadow-sm p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 pb-3 border-b mb-4">
              <Sliders className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-base text-slate-900">Custom Parameter Injection</h3>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <div className="flex justify-between font-bold text-slate-700 mb-1">
                  <span>Affected Population:</span>
                  <span className="text-blue-600 font-mono">{popAffected.toLocaleString()} people</span>
                </div>
                <input 
                  type="range" 
                  min={50000} 
                  max={1000000} 
                  step={25000}
                  value={popAffected}
                  onChange={e => setPopAffected(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>

              <div>
                <div className="flex justify-between font-bold text-slate-700 mb-1">
                  <span>Disaster Horizon Duration:</span>
                  <span className="text-blue-600 font-mono">{durationDays} Days</span>
                </div>
                <input 
                  type="range" 
                  min={3} 
                  max={21} 
                  step={1}
                  value={durationDays}
                  onChange={e => setDurationDays(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-2">Demand Shockwave Multipliers:</label>
                <div className="grid grid-cols-2 gap-2 font-mono">
                  {Object.entries(activeScenario.multipliers || {}).map(([cat, mult]: [string, any]) => (
                    <div key={cat} className="p-2 rounded bg-slate-50 border flex justify-between">
                      <span className="text-slate-600">{cat}:</span>
                      <span className="text-red-600 font-bold">+{((mult - 1) * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-2">Affected Zones:</label>
                <div className="flex flex-wrap gap-2">
                  {locations.map(loc => {
                    const isSelected = affectedZones.includes(loc.id);
                    return (
                      <button
                        key={loc.id}
                        onClick={() => toggleZone(loc.id)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                          isSelected
                            ? 'bg-blue-600 text-white shadow ring-2 ring-blue-400/40'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
                        }`}
                      >
                        {isSelected ? '✓ ' : '+ '} {loc.name}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          <button 
            onClick={handleStart}
            disabled={loading}
            className="w-full mt-6 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-lg font-bold transition-all shadow-md disabled:opacity-70 text-xs uppercase tracking-wider"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
            {loading ? "Injecting Disaster Shocks..." : `Deploy Scenario: ${activeScenario.title}`}
          </button>
        </div>

        {/* Real-time Status Panel */}
        <div className="rounded-xl border bg-slate-900 text-slate-100 p-6 flex flex-col items-center justify-center min-h-[340px]">
          {!result && !loading && (
            <div className="text-center p-6">
              <Globe className="w-14 h-14 text-slate-700 mx-auto mb-3" />
              <h4 className="font-bold text-sm text-slate-300">Simulator Standing By</h4>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                Select a disaster scenario and click &apos;Deploy Scenario&apos; to trigger mathematical demand shockwaves across zones.
              </p>
            </div>
          )}
          
          {loading && (
            <div className="text-center w-full max-w-xs p-6">
              <Activity className="w-10 h-10 text-blue-400 mx-auto mb-3 animate-spin" />
              <p className="text-xs font-bold text-blue-300 mb-2">Simulating Disaster Shockwaves...</p>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div className="bg-blue-500 h-1.5 rounded-full animate-pulse w-3/4"></div>
              </div>
            </div>
          )}

          {result && !loading && !result.error && (
            <div className="w-full bg-slate-800/80 p-5 rounded-xl border border-slate-700 space-y-3">
              <div className="flex items-center gap-2 text-emerald-400 pb-2 border-b border-slate-700">
                <ShieldCheck className="w-5 h-5" />
                <h4 className="font-bold text-sm">Disaster Injected Successfully</h4>
              </div>
              <div className="space-y-1.5 text-xs text-slate-300">
                <p className="flex justify-between"><span className="text-slate-500">Crisis ID:</span> <span className="font-mono font-bold text-blue-400">#{result.crisis_id}</span></p>
                <p className="flex justify-between"><span className="text-slate-500">Telemetry Status:</span> <span className="text-emerald-400 font-bold">SYNCHRONIZED</span></p>
                <p className="flex justify-between"><span className="text-slate-500">System Trace:</span> <span className="text-slate-300">{result.message}</span></p>
              </div>
              <div className="p-3 bg-blue-500/10 text-blue-300 text-[11px] rounded border border-blue-500/20 mt-3">
                Telemetry seeded. You can now examine the updated <strong>Forecasting Curves</strong>, run the <strong>Linear Allocation Optimizer</strong>, and compute <strong>Convoy Routes</strong>.
              </div>
            </div>
          )}

          {result?.error && (
            <div className="w-full bg-red-950/40 p-5 rounded-xl border border-red-800/60 text-red-300">
              <AlertTriangle className="w-5 h-5 mb-1 text-red-400" />
              <h4 className="font-bold text-xs">Simulation Injection Error</h4>
              <p className="text-xs text-red-400 mt-1">{result.error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


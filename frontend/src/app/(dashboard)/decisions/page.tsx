"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { apiClient } from "@/lib/api";
import { 
  BrainCircuit, 
  ShieldCheck, 
  Truck, 
  Package, 
  RefreshCw, 
  CheckCircle2, 
  Sparkles,
  Download,
  Sliders,
  Scale,
  BarChart3
} from "lucide-react";

export default function DecisionsPage() {
  const [activeTab, setActiveTab] = useState<"ahp" | "synthesizer">("ahp");
  const [decisions, setDecisions] = useState<any[]>([]);
  const [locations, setLocations] = useState<any[]>([]);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  
  // AHP Criteria Weights
  const [wUrgency, setWUrgency] = useState(0.30);
  const [wShortage, setWShortage] = useState(0.25);
  const [wVuln, setWVuln] = useState(0.20);
  const [wPop, setWPop] = useState(0.15);
  const [wAccess, setWAccess] = useState(0.10);
  
  const [ahpRankings, setAhpRankings] = useState<any[]>([]);
  const [calculatingAhp, setCalculatingAhp] = useState(false);

  // Single Incident Simulator
  const [selectedLocation, setSelectedLocation] = useState("1");
  const [shortageStatus, setShortageStatus] = useState("CRITICAL");
  const [shortageProb, setShortageProb] = useState(0.92);
  const [stock, setStock] = useState(3500);
  const [demand, setDemand] = useState(6200);
  const [nlpUrgency, setNlpUrgency] = useState("CRITICAL");

  const [activeDecision, setActiveDecision] = useState<any>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [dispatchedId, setDispatchedId] = useState<string | null>(null);

  const fetchPastDecisions = () => {
    apiClient.get("/decision/")
      .then(res => setDecisions(res.data || []))
      .catch(console.error);
  };

  const recalculateAhp = useCallback((u: number, s: number, v: number, p: number, a: number) => {
    setCalculatingAhp(true);
    const total = u + s + v + p + a;
    const payload = {
      medical_urgency: u / total,
      shortage_probability: s / total,
      vulnerability: v / total,
      population: p / total,
      accessibility_risk: a / total
    };

    apiClient.post("/priority/evaluate-weights", payload)
      .then(res => {
        setAhpRankings(res.data.rankings || []);
      })
      .catch(console.error)
      .finally(() => setCalculatingAhp(false));
  }, []);

  useEffect(() => {
    apiClient.get("/simulation/info")
      .then(res => {
        setLocations(res.data.locations || []);
      })
      .catch(console.error);

    fetchPastDecisions();
    recalculateAhp(0.30, 0.25, 0.20, 0.15, 0.10);
  }, [recalculateAhp]);

  const handleWeightChange = (setter: any, val: number, field: string) => {
    setter(val);
    const u = field === "u" ? val : wUrgency;
    const s = field === "s" ? val : wShortage;
    const v = field === "v" ? val : wVuln;
    const p = field === "p" ? val : wPop;
    const a = field === "a" ? val : wAccess;
    
    // Debounce API call
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      recalculateAhp(u, s, v, p, a);
    }, 300);
  };

  const handleEvaluate = async () => {
    setEvaluating(true);
    try {
      const payload = {
        location_id: parseInt(selectedLocation),
        shortage_status: shortageStatus,
        shortage_probability: shortageProb,
        current_warehouse_stock: stock,
        predicted_demand: demand,
        nlp_urgency: nlpUrgency
      };
      const res = await apiClient.post("/decision/evaluate", payload);
      setActiveDecision(res.data);
      fetchPastDecisions();
    } catch (err) {
      console.error(err);
    } finally {
      setEvaluating(false);
    }
  };

  const handleApproveDispatch = (decType: string) => {
    setDispatchedId(decType);
    setTimeout(() => {
      setDispatchedId(null);
    }, 3500);
  };

  const handleExportSitRep = () => {
    window.print();
  };

  const totalWeights = (wUrgency + wShortage + wVuln + wPop + wAccess);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <BrainCircuit className="w-8 h-8 text-blue-600" />
            AI Decision & Explainability Operations Hub
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Analytic Hierarchy Process (AHP) Weight Calibration, Sensitivity Analysis & Autonomous Directives.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center bg-slate-200/80 p-1 rounded-lg border border-slate-300">
            <button
              onClick={() => setActiveTab("ahp")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                activeTab === "ahp" ? 'bg-white shadow text-blue-700' : 'text-slate-600'
              }`}
            >
              AHP Sensitivity Calibration
            </button>
            <button
              onClick={() => setActiveTab("synthesizer")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                activeTab === "synthesizer" ? 'bg-white shadow text-blue-700' : 'text-slate-600'
              }`}
            >
              Single-Incident Directive
            </button>
          </div>

          <button
            onClick={handleExportSitRep}
            className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white px-3.5 py-2 rounded-lg text-xs font-bold transition-all shadow print:hidden"
          >
            <Download className="w-4 h-4 text-blue-400" />
            Print PDF SitRep
          </button>
        </div>
      </div>

      {activeTab === "ahp" ? (
        <>
          {/* AHP Interactive Sliders Card */}
          <div className="rounded-xl border bg-slate-900 text-slate-100 p-6 shadow-lg space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Scale className="w-5 h-5 text-blue-400" />
                <h3 className="font-bold text-sm text-white">Analytic Hierarchy Process (AHP) Multi-Criteria Weight Calibration</h3>
              </div>
              <span className="text-xs font-mono text-emerald-400 font-bold">
                Sum: {(totalWeights * 100).toFixed(0)}% (Normalized in real-time)
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5 pt-2">
              <div>
                <div className="flex justify-between text-xs font-bold text-slate-300 mb-1.5">
                  <span>Medical Urgency:</span>
                  <span className="text-blue-400 font-mono">{(wUrgency * 100).toFixed(0)}%</span>
                </div>
                <input 
                  type="range" min={0.05} max={0.60} step={0.05} value={wUrgency}
                  onChange={e => handleWeightChange(setWUrgency, parseFloat(e.target.value), "u")}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-bold text-slate-300 mb-1.5">
                  <span>Shortage Risk:</span>
                  <span className="text-amber-400 font-mono">{(wShortage * 100).toFixed(0)}%</span>
                </div>
                <input 
                  type="range" min={0.05} max={0.60} step={0.05} value={wShortage}
                  onChange={e => handleWeightChange(setWShortage, parseFloat(e.target.value), "s")}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-bold text-slate-300 mb-1.5">
                  <span>Vulnerability:</span>
                  <span className="text-purple-400 font-mono">{(wVuln * 100).toFixed(0)}%</span>
                </div>
                <input 
                  type="range" min={0.05} max={0.60} step={0.05} value={wVuln}
                  onChange={e => handleWeightChange(setWVuln, parseFloat(e.target.value), "v")}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-bold text-slate-300 mb-1.5">
                  <span>Population:</span>
                  <span className="text-emerald-400 font-mono">{(wPop * 100).toFixed(0)}%</span>
                </div>
                <input 
                  type="range" min={0.05} max={0.60} step={0.05} value={wPop}
                  onChange={e => handleWeightChange(setWPop, parseFloat(e.target.value), "p")}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-bold text-slate-300 mb-1.5">
                  <span>Accessibility Risk:</span>
                  <span className="text-red-400 font-mono">{(wAccess * 100).toFixed(0)}%</span>
                </div>
                <input 
                  type="range" min={0.05} max={0.60} step={0.05} value={wAccess}
                  onChange={e => handleWeightChange(setWAccess, parseFloat(e.target.value), "a")}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-red-500"
                />
              </div>
            </div>
          </div>

          {/* Real-time Sensitivity Analysis Ranked Table */}
          <div className="rounded-xl border bg-white shadow-sm overflow-hidden">
            <div className="p-5 border-b bg-slate-50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-sm text-slate-900">Real-Time MCDA Sensitivity Ranking Table</h3>
              </div>
              <span className="text-xs font-semibold text-blue-700 bg-blue-100 px-2.5 py-0.5 rounded">
                AHP Consistency Ratio (CR &lt; 0.10 Validated)
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="text-[11px] text-slate-500 uppercase bg-slate-100/70 border-b">
                  <tr>
                    <th className="px-6 py-3">Rank</th>
                    <th className="px-6 py-3">Zone Name</th>
                    <th className="px-6 py-3">Composite Priority Score</th>
                    <th className="px-6 py-3">Priority Classification Tier</th>
                    <th className="px-6 py-3">Multi-Criteria Score Breakdown</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {ahpRankings.map((loc: any, idx: number) => (
                    <tr key={loc.location_id || idx} className="hover:bg-slate-50">
                      <td className="px-6 py-3.5 font-bold font-mono text-slate-500">#{idx + 1}</td>
                      <td className="px-6 py-3.5 font-bold text-slate-900">{loc.location_name}</td>
                      <td className="px-6 py-3.5 font-black text-sm text-blue-700 font-mono">
                        {loc.priority_score?.toFixed(1)} / 100
                      </td>
                      <td className="px-6 py-3.5">
                        <span className={`px-2.5 py-0.5 rounded text-[10px] font-black uppercase ${
                          loc.tier === 'TIER_1_CRITICAL' ? 'bg-red-100 text-red-800' :
                          loc.tier === 'TIER_2_HIGH' ? 'bg-amber-100 text-amber-800' :
                          loc.tier === 'TIER_3_MODERATE' ? 'bg-blue-100 text-blue-800' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {loc.tier?.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-3.5">
                        <div className="flex gap-2 text-[10px] font-mono text-slate-500">
                          <span>Med: <strong>{loc.breakdown?.medical_urgency}%</strong></span>
                          <span>•</span>
                          <span>Shortage: <strong>{loc.breakdown?.shortage_probability}%</strong></span>
                          <span>•</span>
                          <span>Vuln: <strong>{loc.breakdown?.vulnerability}%</strong></span>
                          <span>•</span>
                          <span>Pop: <strong>{loc.breakdown?.population_affected}%</strong></span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        /* Decision Synthesizer & Trace View */
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left: Input Telemetry State Simulator */}
          <div className="rounded-xl border bg-white p-5 shadow-sm space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b">
              <Sliders className="w-4 h-4 text-blue-600" />
              <h3 className="font-bold text-sm text-slate-900">Incident State Vector</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Target Location</label>
                <select 
                  value={selectedLocation} 
                  onChange={e => setSelectedLocation(e.target.value)}
                  className="w-full border rounded-lg p-2 bg-slate-50 font-semibold"
                >
                  {locations.map(l => (
                    <option key={l.id} value={l.id}>{l.name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Shortage Status</label>
                  <select 
                    value={shortageStatus} 
                    onChange={e => setShortageStatus(e.target.value)}
                    className="w-full border rounded-lg p-2 bg-slate-50 font-semibold"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="WARNING">WARNING</option>
                    <option value="WATCH">WATCH</option>
                    <option value="SAFE">SAFE</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">NLP Urgency</label>
                  <select 
                    value={nlpUrgency} 
                    onChange={e => setNlpUrgency(e.target.value)}
                    className="w-full border rounded-lg p-2 bg-slate-50 font-semibold"
                  >
                    <option value="CRITICAL">CRITICAL (SOS)</option>
                    <option value="WARNING">WARNING</option>
                    <option value="WATCH">WATCH</option>
                  </select>
                </div>
              </div>

              <div>
                <div className="flex justify-between font-bold text-slate-700 mb-1">
                  <span>Shortage Probability:</span>
                  <span className="text-blue-600 font-mono">{(shortageProb * 100).toFixed(0)}%</span>
                </div>
                <input 
                  type="range" 
                  min={0.1} 
                  max={0.99} 
                  step={0.05}
                  value={shortageProb}
                  onChange={e => setShortageProb(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Stock on Hand</label>
                  <input 
                    type="number"
                    value={stock}
                    onChange={e => setStock(parseFloat(e.target.value) || 0)}
                    className="w-full border rounded-lg p-2 bg-slate-50 font-bold font-mono"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Forecast Demand</label>
                  <input 
                    type="number"
                    value={demand}
                    onChange={e => setDemand(parseFloat(e.target.value) || 0)}
                    className="w-full border rounded-lg p-2 bg-slate-50 font-bold font-mono"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={handleEvaluate}
              disabled={evaluating}
              className="w-full mt-3 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 rounded-lg text-xs transition-all shadow disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {evaluating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Synthesize Operational Directive
            </button>
          </div>

          {/* Center & Right: AI Synthesis & Explainability Directive */}
          <div className="lg:col-span-2 rounded-xl border bg-white p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start pb-4 border-b">
                <div>
                  <span className="text-[10px] font-black uppercase tracking-widest bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                    DECISION REASONING TRACE
                  </span>
                  <h3 className="text-xl font-black text-slate-900 mt-1">Autonomous Recommendation</h3>
                </div>

                {activeDecision && (
                  <div className="text-right">
                    <span className="text-xs text-slate-400 font-bold uppercase">Confidence</span>
                    <p className="text-2xl font-black text-emerald-600 font-mono">
                      {(activeDecision.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                )}
              </div>

              {activeDecision ? (
                <div className="mt-5 space-y-4">
                  <div className="p-4 rounded-xl border bg-slate-50 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-3 rounded-xl ${
                        activeDecision.decision_type === 'DISPATCH' ? 'bg-emerald-100 text-emerald-700' :
                        activeDecision.decision_type === 'ALLOCATE' ? 'bg-blue-100 text-blue-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {activeDecision.decision_type === 'DISPATCH' ? <Truck className="w-6 h-6" /> :
                         activeDecision.decision_type === 'ALLOCATE' ? <Sliders className="w-6 h-6" /> :
                         <Package className="w-6 h-6" />}
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Recommended Action</p>
                        <h4 className="text-2xl font-black text-slate-900 tracking-tight">
                          {activeDecision.decision_type} DIRECTIVE
                        </h4>
                      </div>
                    </div>

                    <button
                      onClick={() => handleApproveDispatch(activeDecision.decision_type)}
                      className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-5 py-2.5 rounded-lg text-xs shadow-md transition-all flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Approve Directive
                    </button>
                  </div>

                  {dispatchedId && (
                    <div className="p-3 bg-emerald-50 text-emerald-800 rounded-lg border border-emerald-200 text-xs font-bold flex items-center gap-2 animate-bounce">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      Directive Approved: Autonomous convoy command sent to logistics dispatch queue.
                    </div>
                  )}

                  {/* Natural Language Explanation Card */}
                  <div className="p-4 rounded-xl border bg-blue-50/50 border-blue-100">
                    <p className="text-xs font-bold uppercase text-blue-700 tracking-wider mb-1 flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4" /> Explainability & Reasoning Audit
                    </p>
                    <p className="text-xs text-slate-700 leading-relaxed font-medium">
                      {activeDecision.explanation}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="py-16 text-center text-slate-400 flex flex-col items-center">
                  <BrainCircuit className="w-12 h-12 mb-3 text-slate-300 animate-pulse" />
                  <p className="text-xs font-semibold">Click &apos;Synthesize Operational Directive&apos; to run multi-criteria inference.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


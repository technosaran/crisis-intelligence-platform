"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api";
import { 
  Radio, 
  Search, 
  Activity, 
  Cpu, 
  ShieldAlert, 
  Terminal, 
  Mic, 
  MicOff,
  ArrowRight,
  Volume2,
  Languages
} from "lucide-react";

export default function NLPIntelPage() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // Fetch past signals
  useEffect(() => {
    apiClient.get("/nlp/signals")
      .then(res => setHistory(res.data.reverse()))
      .catch(console.error);
  }, []);

  const samplePresets = [
    {
      label: "Hospital Oxygen Outage (English)",
      text: "Emergency SOS! Government hospital in Zone A is completely out of Oxygen Cylinders. We have 45 ICU patients crashing. Roads are flooded."
    },
    {
      label: "Chennai Flood - Coastal Rescue (Tamil Transliteration)",
      text: "Aabathu! Zone C la 300 kudumbangal flood la maatikitaanga. Thanneer thevai and mudhal udhavi First Aid Kits udane anupavum."
    },
    {
      label: "Cyclone Shelter Food Crisis (English/Hindi)",
      text: "SOS from Zone E East Harbor Shelter. Food rations exhausted for 800 stranded refugees. Immediate need for Rice Packs and Drinking Water."
    },
    {
      label: "Zone D Bridge Collapse (Emergency Trauma)",
      text: "Bridge washed away near Zone D. 250 casualties reported after structural collapse. Urgent requirement for Emergency Medicine and Antibiotics."
    }
  ];

  // Speech Recognition Initializer
  const handleToggleVoice = () => {
    if (isRecording) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsRecording(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Web Speech API is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setIsRecording(true);
    };

    recognition.onresult = (event: any) => {
      let interimTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          setText(prev => prev + " " + event.results[i][0].transcript);
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }
    };

    recognition.onerror = (err: any) => {
      console.error("Speech recognition error", err);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const handleAnalyze = async () => {
    if (!text) return;
    setLoading(true);
    try {
      const res = await apiClient.post("/nlp/analyze", {
        source: isRecording ? "MICROPHONE_VOICE_STREAM" : "VHF_RADIO_INTERCEPT",
        raw_text: text,
        latitude: null,
        longitude: null
      });
      setResult(res.data.signal);
      setHistory(prev => [res.data.signal, ...prev]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
            <Radio className="w-8 h-8 text-blue-600" /> Signal Intelligence (SIGINT) & Voice SOS Ingestion
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Natural Language Processing (NLP) Entity Extraction Engine with Web Speech Recognition & Multilingual Intercepts.
          </p>
        </div>
      </div>

      {/* Preset Buttons Bar */}
      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
          <Languages className="w-4 h-4 text-blue-600" /> Quick Multilingual Distress Intercept Presets:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
          {samplePresets.map((preset) => (
            <button
              key={preset.label}
              onClick={() => setText(preset.text)}
              className="text-left p-2.5 rounded-lg border bg-slate-50 hover:bg-blue-50/60 hover:border-blue-300 transition-all text-xs font-medium text-slate-800"
            >
              <div className="font-bold text-blue-700">{preset.label}</div>
              <div className="text-[11px] text-slate-500 truncate mt-0.5">{preset.text}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="rounded-xl border bg-slate-950 p-6 shadow-xl flex flex-col justify-between text-slate-300">
          <div>
            <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-mono font-bold text-slate-100">SECURE_RADIO_STREAM_01</h3>
              </div>
              <div className="flex items-center gap-2">
                {isRecording && (
                  <span className="text-[10px] font-mono text-red-400 bg-red-950 px-2 py-0.5 rounded border border-red-800 animate-pulse flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span> MIC RECORDING LIVE
                  </span>
                )}
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                  CHANNEL 146.520 MHz
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-slate-400" /> Intercepted Audio Transcript / Distress Payload
              </label>

              <button
                onClick={handleToggleVoice}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  isRecording 
                    ? 'bg-red-600 text-white animate-pulse shadow-lg' 
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                }`}
              >
                {isRecording ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5 text-red-400" />}
                {isRecording ? "Stop Listening" : "Record Voice SOS"}
              </button>
            </div>

            <textarea 
              value={text}
              onChange={e => setText(e.target.value)}
              className="w-full h-32 bg-slate-900 border border-slate-700 rounded-lg p-3.5 text-emerald-400 font-mono text-xs focus:outline-none focus:border-emerald-500 resize-none leading-relaxed"
              placeholder="Speak via microphone above, select a preset, or paste raw citizen distress text..."
            ></textarea>
          </div>

          <div className="flex gap-3 mt-4">
            <button 
              onClick={() => setText("")}
              className="bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white px-3 py-2.5 rounded-lg font-bold transition-all text-xs border border-slate-700"
            >
              Clear
            </button>
            <button 
              onClick={handleAnalyze}
              disabled={loading || !text}
              className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-5 py-2.5 rounded-lg font-black transition-all shadow-md disabled:opacity-50 flex items-center justify-center gap-2 text-xs uppercase tracking-wider"
            >
              {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Cpu className="w-4 h-4" />}
              {loading ? "Performing NER Analysis..." : "Extract Crisis Entities"}
            </button>
          </div>
        </div>

        {/* Output Panel */}
        <div className="rounded-xl border bg-white p-6 shadow-sm flex flex-col justify-between relative overflow-hidden">
          <div>
            <div className="flex justify-between items-center mb-4 pb-4 border-b">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Search className="w-4 h-4 text-blue-600" /> NLP Entity Extraction Results
              </h3>
              {result && (
                <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                  Extracted & Formatted
                </span>
              )}
            </div>

            {!result && !loading && (
              <div className="py-14 flex flex-col items-center justify-center text-slate-400">
                <Cpu className="w-12 h-12 mb-3 text-slate-300 animate-pulse" />
                <p className="text-xs font-semibold">Speak or select a preset and click &apos;Extract Crisis Entities&apos;.</p>
              </div>
            )}

            {loading && (
              <div className="py-14 flex flex-col items-center justify-center text-blue-600 gap-3">
                <Activity className="w-8 h-8 animate-spin" />
                <p className="text-xs font-bold text-slate-600">Performing Named Entity Recognition (NER)...</p>
              </div>
            )}

            {result && !loading && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-blue-50 p-3.5 rounded-xl border border-blue-100">
                    <p className="text-[10px] font-bold text-blue-500 uppercase tracking-wider mb-0.5">Target Location</p>
                    <p className="text-base font-bold text-slate-900">{result.location || "UNKNOWN ZONE"}</p>
                  </div>
                  <div className="bg-indigo-50 p-3.5 rounded-xl border border-indigo-100">
                    <p className="text-[10px] font-bold text-indigo-500 uppercase tracking-wider mb-0.5">Resource Needed</p>
                    <p className="text-base font-bold text-slate-900">{result.resource || "General Relief"}</p>
                  </div>
                  <div className="bg-red-50 p-3.5 rounded-xl border border-red-100">
                    <p className="text-[10px] font-bold text-red-500 uppercase tracking-wider mb-0.5">Urgency Classification</p>
                    <p className="text-base font-black text-red-700 flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4 text-red-600" /> {result.urgency || "CRITICAL"}
                    </p>
                  </div>
                  <div className="bg-emerald-50 p-3.5 rounded-xl border border-emerald-100">
                    <p className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider mb-0.5">Entity Confidence</p>
                    <p className="text-base font-black text-emerald-700 font-mono">{(result.confidence * 100).toFixed(0)}%</p>
                  </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-medium">Affected Population Estimate:</span>
                  <span className="font-bold font-mono text-slate-900">{result.affected_population || 200} people</span>
                </div>
              </div>
            )}
          </div>

          {result && !loading && (
            <div className="mt-4 pt-3 border-t flex justify-end">
              <Link
                href="/decisions"
                className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-bold transition-all shadow"
              >
                Forward to AI Decision Hub <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* History Table */}
      <div className="rounded-xl border bg-white shadow-sm overflow-hidden">
        <div className="p-5 border-b bg-slate-50 flex items-center justify-between">
          <h3 className="font-bold text-sm text-slate-800">Historical Signal Intercepts Ledger</h3>
          <span className="text-xs text-slate-500">{history.length} Intercepts Logged</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="text-[11px] text-slate-500 uppercase bg-slate-100/70 border-b">
              <tr>
                <th className="px-6 py-3">Location</th>
                <th className="px-6 py-3">Resource</th>
                <th className="px-6 py-3">Urgency</th>
                <th className="px-6 py-3">Confidence</th>
                <th className="px-6 py-3">Event Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {history.slice(0, 6).map((h, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="px-6 py-3 font-bold text-slate-900">{h.location || "Sector Grid"}</td>
                  <td className="px-6 py-3 text-blue-600 font-medium">{h.resource || "Emergency Stock"}</td>
                  <td className="px-6 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      h.urgency === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                    }`}>
                      {h.urgency}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-emerald-600 font-mono font-bold">{(h.confidence * 100).toFixed(0)}%</td>
                  <td className="px-6 py-3 text-slate-500 font-mono">{h.event_type || "DISTRESS_CALL"}</td>
                </tr>
              ))}
              {history.length === 0 && (
                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-400">No signals intercepted yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}



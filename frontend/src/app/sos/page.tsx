"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api";
import { AlertCircle, CheckCircle2, ShieldAlert } from "lucide-react";

export default function SOSPortal() {
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !location || !message) return;
    
    setStatus("submitting");
    try {
      await apiClient.post("/nlp/sos-submit", {
        name,
        location,
        message,
        timestamp: new Date().toISOString(),
      });
      setStatus("success");
      setName("");
      setLocation("");
      setMessage("");
    } catch (err: any) {
      console.error(err);
      setStatus("error");
      setErrorMsg(err.response?.data?.detail || "Failed to submit SOS. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-red-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-red-600 p-6 text-white text-center flex flex-col items-center">
          <ShieldAlert className="w-12 h-12 mb-2 animate-pulse" />
          <h1 className="text-3xl font-black uppercase tracking-widest">Emergency SOS</h1>
          <p className="text-red-100 text-sm mt-1 font-medium">Crisis Intelligence Platform</p>
        </div>

        <div className="p-6">
          {status === "success" ? (
            <div className="text-center py-8">
              <CheckCircle2 className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-slate-900 mb-2">SOS Received</h2>
              <p className="text-slate-600 text-sm mb-6">
                Your emergency request has been securely transmitted to the nearest command center and relief agencies.
              </p>
              <button 
                onClick={() => setStatus("idle")}
                className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-xl transition-all"
              >
                Submit Another Report
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {status === "error" && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                  <span>{errorMsg}</span>
                </div>
              )}
              
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full border-2 border-slate-200 rounded-xl p-3 focus:border-red-500 focus:ring-0 transition-colors font-medium outline-none"
                  placeholder="John Doe"
                  disabled={status === "submitting"}
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Current Location
                </label>
                <input
                  type="text"
                  required
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full border-2 border-slate-200 rounded-xl p-3 focus:border-red-500 focus:ring-0 transition-colors font-medium outline-none"
                  placeholder="Address, City, or Coordinates"
                  disabled={status === "submitting"}
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Emergency Message
                </label>
                <textarea
                  required
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={4}
                  className="w-full border-2 border-slate-200 rounded-xl p-3 focus:border-red-500 focus:ring-0 transition-colors font-medium outline-none resize-none"
                  placeholder="Describe your situation, number of people, injuries, etc."
                  disabled={status === "submitting"}
                />
              </div>

              <button
                type="submit"
                disabled={status === "submitting"}
                className="w-full bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-black uppercase tracking-widest py-4 rounded-xl shadow-lg transition-all disabled:opacity-70 mt-2 flex justify-center items-center gap-2"
              >
                {status === "submitting" ? (
                  <span className="animate-pulse">Transmitting...</span>
                ) : (
                  "Submit SOS"
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

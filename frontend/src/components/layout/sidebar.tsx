"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Radio, 
  PlaySquare, 
  TrendingUp, 
  Scale, 
  Navigation, 
  Bell, 
  BrainCircuit,
  ShieldCheck
} from "lucide-react";

const navigation = [
  { name: "Crisis Dashboard", href: "/", icon: LayoutDashboard },
  { name: "AI Decision Hub", href: "/decisions", icon: BrainCircuit, badge: "AI" },
  { name: "Demand Forecasting", href: "/forecast", icon: TrendingUp },
  { name: "Resource Allocation", href: "/allocation", icon: Scale },
  { name: "Logistics Routing", href: "/routing", icon: Navigation },
  { name: "Signal Intel (NLP)", href: "/nlp-intel", icon: Radio },
  { name: "Disaster Sandbox", href: "/simulation", icon: PlaySquare },
  { name: "Live Alerts Log", href: "/alerts", icon: Bell },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-64 shrink-0 bg-slate-900 text-slate-200 border-r border-slate-800 min-h-screen sticky top-0 h-screen z-30">
      <div className="flex h-[64px] items-center border-b border-slate-800 px-6 gap-3 shrink-0">
        <div className="p-2 bg-blue-600 text-white rounded-lg shadow-sm">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-sm text-white tracking-wide">CRISIS AI INTEL</h1>
          <p className="text-[10px] text-blue-400 font-mono font-semibold tracking-wider">AUTONOMOUS LOGISTICS</p>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto py-4 px-3">
        <div className="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Platform Modules
        </div>
        <nav className="grid items-start text-xs font-semibold gap-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center justify-between gap-3 rounded-lg px-3 py-2.5 transition-all ${
                  isActive
                    ? "bg-blue-600 text-white shadow-md shadow-blue-500/20 font-bold"
                    : "text-slate-400 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] bg-blue-500/20 text-blue-300 px-1.5 py-0.5 rounded border border-blue-500/30">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-4 border-t border-slate-800/80 bg-slate-950/60 m-3 rounded-xl text-[11px] text-slate-400 shrink-0">
        <div className="flex items-center justify-between">
          <span className="font-bold text-slate-200">Capstone Ready</span>
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
        </div>
        <p className="text-[10px] text-slate-500 mt-1 font-mono">OR-Tools • PyTorch • XGBoost</p>
      </div>
    </aside>
  );
}



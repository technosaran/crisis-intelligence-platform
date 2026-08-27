"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Menu, 
  X, 
  Bell, 
  PlaySquare, 
  TrendingUp, 
  Scale, 
  Navigation, 
  Radio, 
  BrainCircuit, 
  LayoutDashboard,
  LogIn,
  LogOut,
  User as UserIcon
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

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


export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const currentPage = navigation.find(n => n.href === pathname)?.name || "Crisis Operations";

  return (
    <>
      <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/85 dark:bg-slate-950/85 backdrop-blur-md px-4 md:px-6 justify-between shadow-xs">
        {/* Left: Mobile Toggle & Page Title */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-block text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">Operations /</span>
            <h1 className="text-base md:text-lg font-bold text-slate-900 dark:text-slate-100">{currentPage}</h1>
          </div>
        </div>

        {/* Right: Live System Pulse & Quick Profile */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 px-3 py-1.5 rounded-full text-xs font-semibold border border-emerald-200/60 dark:border-emerald-800/50">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>SYSTEM ONLINE</span>
          </div>


          <Link 
            href="/alerts" 
            className="p-2 rounded-lg text-slate-500 hover:text-slate-800 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative"
            title="Active Alerts"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
          </Link>

          <div className="flex items-center gap-2.5 pl-3 border-l border-slate-200 dark:border-slate-800">
            {user ? (
              <>
                <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-xs">
                  <UserIcon className="w-4 h-4" />
                </div>
                <div className="hidden md:block text-left text-xs mr-2">
                  <p className="font-bold text-slate-800 leading-tight">{user.full_name}</p>
                  <p className="text-[10px] text-slate-400 font-mono truncate w-24">{user.email}</p>
                </div>
                <button
                  onClick={logout}
                  className="p-2 rounded-lg text-slate-500 hover:text-red-600 hover:bg-red-50 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold text-sm transition-colors"
              >
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 top-16 z-50 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 text-slate-100 p-4 border-b border-slate-800 shadow-2xl max-h-[calc(100vh-4rem)] overflow-y-auto">
            <nav className="grid gap-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center justify-between gap-3 rounded-lg px-4 py-3 text-sm font-semibold transition-all ${
                      isActive
                        ? "bg-blue-600 text-white font-bold"
                        : "text-slate-400 hover:text-white hover:bg-slate-800"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="w-4 h-4" />
                      <span>{item.name}</span>
                    </div>
                    {item.badge && (
                      <span className="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded border border-blue-500/30">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      )}
    </>
  );
}


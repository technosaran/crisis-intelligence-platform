"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Radio, TriangleAlert, Bell } from "lucide-react";

const mobileNav = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Field Intel", href: "/nlp-intel", icon: Radio },
  { name: "SOS Report", href: "/sos", icon: TriangleAlert, isAction: true },
  { name: "Alerts", href: "/alerts", icon: Bell },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 pb-safe shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
      <nav className="flex items-center justify-around h-16 px-2">
        {mobileNav.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          
          if (item.isAction) {
            return (
              <Link
                key={item.name}
                href={item.href}
                className="-mt-6 flex flex-col items-center justify-center"
              >
                <div className="w-14 h-14 bg-red-600 rounded-full flex items-center justify-center shadow-lg shadow-red-600/30 border-4 border-slate-100 dark:border-slate-950">
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-[10px] font-bold text-red-600 dark:text-red-400 mt-1">{item.name}</span>
              </Link>
            )
          }

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${
                isActive 
                  ? "text-blue-600 dark:text-blue-400" 
                  : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100"
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? "fill-blue-600/20" : ""}`} />
              <span className="text-[10px] font-bold">{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

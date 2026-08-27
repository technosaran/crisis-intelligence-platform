import re

with open('frontend/src/app/(dashboard)/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

if 'from "recharts"' not in content:
    content = content.replace('import { apiClient } from "@/lib/api";', 'import { apiClient } from "@/lib/api";\nimport { LineChart, Line, ResponsiveContainer } from "recharts";')

if 'const sparklineData =' not in content:
    content = content.replace('export default function DashboardPage() {', 'export default function DashboardPage() {\n  const sparklineData = [{v: 10}, {v: 15}, {v: 8}, {v: 25}, {v: 20}, {v: 30}, {v: 28}];')

kpi_regex = re.compile(r'<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">.*?(?=\s*\{/\* Map & Live Alerts Section \*/\})', re.DOTALL)
new_kpis = """<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-5 flex flex-col justify-between border-l-4 border-l-red-500 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Critical Shortages</p>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-100 mt-1">
                {isLiveMode ? liveLocations.filter((l: any) => l.severity === "critical").length : kpis.critical_shortages}
              </h3>
              <p className="text-[11px] text-red-600 dark:text-red-400 font-semibold mt-1">High stockout risk</p>
            </div>
            <div className="p-2 bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 rounded-xl z-10">
              <AlertCircle className="w-5 h-5" />
            </div>
          </div>
          <div className="h-12 mt-4 -mx-2 -mb-2 opacity-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData}>
                <Line type="monotone" dataKey="v" stroke="#ef4444" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-5 flex flex-col justify-between border-l-4 border-l-blue-500 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Network Inventory</p>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-100 mt-1">
                {isLiveMode ? "N/A" : kpis.total_warehouse_stock.toLocaleString()}
              </h3>
              <p className="text-[11px] text-blue-600 dark:text-blue-400 font-semibold mt-1">Across 4 Strategic Hubs</p>
            </div>
            <div className="p-2 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-xl z-10">
              <Package className="w-5 h-5" />
            </div>
          </div>
          <div className="h-12 mt-4 -mx-2 -mb-2 opacity-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData.map(d => ({v: d.v * 1.5}))}>
                <Line type="monotone" dataKey="v" stroke="#3b82f6" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-5 flex flex-col justify-between border-l-4 border-l-emerald-500 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Active Nav Routes</p>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-100 mt-1">
                {isLiveMode ? "0" : kpis.active_deliveries}
              </h3>
              <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-1">A* graph routed</p>
            </div>
            <div className="p-2 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-xl z-10">
              <Truck className="w-5 h-5" />
            </div>
          </div>
          <div className="h-12 mt-4 -mx-2 -mb-2 opacity-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData.map(d => ({v: d.v * 0.8}))}>
                <Line type="monotone" dataKey="v" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-5 flex flex-col justify-between border-l-4 border-l-purple-500 hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Projected 7D Demand</p>
              <h3 className="text-2xl font-black text-slate-800 dark:text-slate-100 mt-1">
                {isLiveMode ? "Predicting..." : kpis.projected_demand_7d.toLocaleString()}
              </h3>
              <p className="text-[11px] text-purple-600 dark:text-purple-400 font-semibold mt-1">XGBoost & LSTM aggregated</p>
            </div>
            <div className="p-2 bg-purple-50 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-xl z-10">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="h-12 mt-4 -mx-2 -mb-2 opacity-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sparklineData.map(d => ({v: d.v * 2.2}))}>
                <Line type="monotone" dataKey="v" stroke="#8b5cf6" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
"""
content = kpi_regex.sub(new_kpis, content)

content = content.replace('text-slate-900', 'text-slate-900 dark:text-slate-100')
content = content.replace('bg-white', 'bg-white dark:bg-slate-900')
content = content.replace('bg-slate-100', 'bg-slate-100 dark:bg-slate-800')
content = content.replace('bg-slate-50', 'bg-slate-50 dark:bg-slate-800/50')
content = content.replace('border-slate-200', 'border-slate-200 dark:border-slate-800')
content = content.replace('text-slate-800', 'text-slate-800 dark:text-slate-200')
content = content.replace('dark:bg-slate-900 dark:text-slate-100', 'dark:bg-slate-900 dark:text-slate-100') # fix double dupes if any

with open('frontend/src/app/(dashboard)/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

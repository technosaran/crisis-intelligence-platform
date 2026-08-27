import re

with open('frontend/src/components/dashboard/map-view.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

if 'useTheme' not in content:
    content = content.replace('import { useEffect, useState } from "react";', 'import { useEffect, useState } from "react";\nimport { useTheme } from "next-themes";')

if 'const { theme } = useTheme();' not in content:
    content = content.replace('const [isMounted, setIsMounted] = useState(false);', 'const [isMounted, setIsMounted] = useState(false);\n  const { theme } = useTheme();')

old_tile = """<TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />"""

new_tile = """<TileLayer
          attribution={theme === "dark" ? "&copy; <a href='https://carto.com/attributions'>CARTO</a>" : "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"}
          url={theme === "dark" ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}
        />"""

content = content.replace(old_tile, new_tile)

red_icon_logic = 'if (loc.severity === "critical") return RedIcon;'
pulsing_red = """if (loc.severity === "critical") return L.divIcon({
      className: "pulsing-marker",
      html: `<div class="relative flex h-5 w-5 items-center justify-center"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-4 w-4 bg-red-600 border border-white"></span></div>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });"""

content = content.replace(red_icon_logic, pulsing_red)

# Ensure the container background is dark-mode friendly
content = content.replace('bg-slate-900/5', 'bg-slate-900/5 dark:bg-slate-800')

with open('frontend/src/components/dashboard/map-view.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

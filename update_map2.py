with open('frontend/src/components/dashboard/map-view.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('import { useTheme } from "next-themes";\n', '')
content = content.replace('  const { theme } = useTheme();\n', '')

old_tile = """<TileLayer
          attribution={theme === "dark" ? "&copy; <a href='https://carto.com/attributions'>CARTO</a>" : "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"}
          url={theme === "dark" ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}
        />"""
        
new_tile = """<TileLayer
          attribution="&copy; <a href='https://carto.com/attributions'>CARTO</a>"
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />"""

content = content.replace(old_tile, new_tile)

with open('frontend/src/components/dashboard/map-view.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

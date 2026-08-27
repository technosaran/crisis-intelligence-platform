"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Leaflet default icons
const DefaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const RedIcon = L.icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const OrangeIcon = L.icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const GreenIcon = L.icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const BlueIcon = L.icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// Custom Truck Convoy Marker
const TruckIcon = L.divIcon({
  className: "truck-marker",
  html: `<div style="background-color:#10b981; border:2px solid #ffffff; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; box-shadow:0 0 12px rgba(16,185,129,0.7);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18.5" r="2.5"/><circle cx="7" cy="18.5" r="2.5"/></svg></div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

export interface LocationNode {
  id: number;
  name: string;
  lat: number;
  lng: number;
  type: string;
  severity?: string;
  population?: number;
  current_stock?: number;
  recent_demand?: number;
  mag?: number;
}

function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

export default function MapView({ 
  locations = [], 
  routeCoordinates = [],
  routeColor = "#2563eb",
  height = "420px",
  truckPosition = null
}: { 
  locations?: LocationNode[];
  routeCoordinates?: [number, number][];
  routeColor?: string;
  height?: string;
  truckPosition?: [number, number] | null;
}) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <div style={{ height }} className="w-full bg-slate-900/5 dark:bg-slate-800 flex items-center justify-center animate-pulse rounded-lg border text-sm text-slate-400">
        Loading GIS Spatial View...
      </div>
    );
  }

  const displayLocations: LocationNode[] = locations.length > 0 ? locations : [
    { id: 1, name: "Zone A (North Hospital Depot)", lat: 13.118, lng: 80.220, type: "crisis", severity: "critical", population: 180000 },
    { id: 2, name: "Zone B (Central Logistics Base)", lat: 13.050, lng: 80.245, type: "warehouse", severity: "safe", population: 250000 },
    { id: 3, name: "Zone C (South Coastal Relief)", lat: 12.970, lng: 80.215, type: "crisis", severity: "warning", population: 210000 },
    { id: 4, name: "Zone D (West Medical Center)", lat: 13.040, lng: 80.140, type: "crisis", severity: "warning", population: 160000 },
    { id: 5, name: "Zone E (East Harbor Shelter)", lat: 13.090, lng: 80.290, type: "crisis", severity: "critical", population: 190000 },
  ];

  const centerLat = routeCoordinates.length > 0 
    ? routeCoordinates[0][0] 
    : displayLocations.length > 0 
    ? displayLocations[0].lat 
    : 13.05;
    
  const centerLng = routeCoordinates.length > 0 
    ? routeCoordinates[0][1] 
    : displayLocations.length > 0 
    ? displayLocations[0].lng 
    : 80.24;

  const defaultZoom = routeCoordinates.length > 0 ? 12 : locations.some(l => l.mag) ? 3 : 11;

  const getMarkerIcon = (loc: LocationNode) => {
    if (loc.type === "warehouse") return BlueIcon;
    if (loc.severity === "critical") return L.divIcon({
      className: "pulsing-marker",
      html: `<div class="relative flex h-5 w-5 items-center justify-center"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-4 w-4 bg-red-600 border border-white"></span></div>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });
    if (loc.severity === "warning") return OrangeIcon;
    return GreenIcon;
  };

  return (
    <div style={{ height }} className="w-full rounded-lg overflow-hidden border relative z-0">
      <MapContainer
        center={[centerLat, centerLng]}
        zoom={defaultZoom}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={false}
      >
        <ChangeView center={[centerLat, centerLng]} zoom={defaultZoom} />
        <TileLayer
          attribution="&copy; <a href='https://carto.com/attributions'>CARTO</a>"
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Render Route Polyline */}
        {routeCoordinates && routeCoordinates.length > 1 && (
          <Polyline
            positions={routeCoordinates}
            pathOptions={{
              color: routeColor,
              weight: 5,
              opacity: 0.85,
              dashArray: routeColor === "#ef4444" ? "8, 8" : undefined
            }}
          />
        )}

        {/* Render Live Moving Convoy Truck Marker */}
        {truckPosition && (
          <Marker position={truckPosition} icon={TruckIcon}>
            <Popup>
              <div className="p-1 text-xs font-bold text-emerald-800">
                🚚 Active Relief Convoy in Transit
              </div>
            </Popup>
          </Marker>
        )}

        {/* Location Markers */}
        {displayLocations.map((loc) => (
          <Marker
            key={loc.id}
            position={[loc.lat, loc.lng]}
            icon={getMarkerIcon(loc)}
          >
            <Popup>
              <div className="p-1 min-w-[160px]">
                <div className="flex items-center justify-between gap-2 border-b pb-1 mb-1">
                  <strong className="text-xs text-slate-900">{loc.name}</strong>
                </div>
                <div className="text-[11px] space-y-0.5 text-slate-600">
                  <p><span className="font-semibold">Type:</span> {loc.type?.toUpperCase()}</p>
                  {loc.severity && (
                    <p>
                      <span className="font-semibold">Status:</span>{" "}
                      <span className={loc.severity === "critical" ? "text-red-600 font-bold" : "text-amber-600 font-bold"}>
                        {loc.severity.toUpperCase()}
                      </span>
                    </p>
                  )}
                  {loc.population && <p><span className="font-semibold">Population:</span> {loc.population.toLocaleString()}</p>}
                  {loc.current_stock !== undefined && <p><span className="font-semibold">Stock:</span> {loc.current_stock.toLocaleString()} units</p>}
                  {loc.mag && <p><span className="font-semibold">Magnitude:</span> M{loc.mag}</p>}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}



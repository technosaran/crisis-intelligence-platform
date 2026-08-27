from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/live-disasters")
async def get_live_disasters():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch live disasters"}
        
    data = response.json()
    disasters = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        
        disasters.append({
            "title": props.get("title"),
            "magnitude": props.get("mag"),
            "time": props.get("time"),
            "coordinates": geom.get("coordinates")
        })
        
    return disasters

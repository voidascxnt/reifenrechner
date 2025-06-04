from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import math
import json
import csv
from io import StringIO

app = FastAPI(title="Smart Felgen-Reifen Kompatibilitäts-Rechner")

# Statische Dateien servieren
app.mount("/static", StaticFiles(directory="static"), name="static")

# Umfassende Reifendatenbank
tire_database = [
    # 14 Zoll
    {"width": 165, "aspect": 70, "diameter": 14},
    {"width": 175, "aspect": 65, "diameter": 14},
    {"width": 185, "aspect": 60, "diameter": 14},
    {"width": 195, "aspect": 55, "diameter": 14},
    {"width": 205, "aspect": 50, "diameter": 14},
    
    # 15 Zoll  
    {"width": 175, "aspect": 65, "diameter": 15},
    {"width": 185, "aspect": 60, "diameter": 15},
    {"width": 195, "aspect": 55, "diameter": 15},
    {"width": 205, "aspect": 50, "diameter": 15},
    {"width": 215, "aspect": 45, "diameter": 15},
    {"width": 225, "aspect": 40, "diameter": 15},
    
    # 16 Zoll
    {"width": 185, "aspect": 55, "diameter": 16},
    {"width": 195, "aspect": 50, "diameter": 16},
    {"width": 205, "aspect": 45, "diameter": 16},
    {"width": 215, "aspect": 40, "diameter": 16},
    {"width": 225, "aspect": 35, "diameter": 16},
    
    # 17 Zoll
    {"width": 205, "aspect": 50, "diameter": 17},
    {"width": 215, "aspect": 45, "diameter": 17},
    {"width": 225, "aspect": 40, "diameter": 17},
    {"width": 235, "aspect": 35, "diameter": 17},
    {"width": 245, "aspect": 30, "diameter": 17},
    
    # 18 Zoll
    {"width": 225, "aspect": 40, "diameter": 18},
    {"width": 235, "aspect": 35, "diameter": 18},
    {"width": 245, "aspect": 30, "diameter": 18},
    {"width": 255, "aspect": 25, "diameter": 18},
    
    # 19 Zoll  
    {"width": 235, "aspect": 35, "diameter": 19},
    {"width": 245, "aspect": 30, "diameter": 19},
    {"width": 255, "aspect": 25, "diameter": 19},
    {"width": 275, "aspect": 20, "diameter": 19},
    
    # 20 Zoll
    {"width": 245, "aspect": 30, "diameter": 20},
    {"width": 255, "aspect": 25, "diameter": 20},
    {"width": 275, "aspect": 20, "diameter": 20}
]

# Felgenbreiten-Kompatibilität  
rim_compatibility = {
    5.0: (155, 165, 175),
    5.5: (165, 175, 185), 
    6.0: (175, 185, 205),
    6.5: (185, 195, 215),
    7.0: (195, 205, 225),
    7.5: (205, 215, 235),
    8.0: (215, 225, 245),
    8.5: (225, 235, 255),
    9.0: (235, 245, 265),
    9.5: (245, 255, 275),
    10.0: (255, 265, 285)
}

class TireResult(BaseModel):
    width: int
    aspect: int  
    diameter: int
    rim_width: float
    deviation_percent: float
    category: str
    scene_points: int
    stretch_factor: str
    tuev_friendly: bool

def calculate_rolling_circumference(width: int, aspect: int, diameter: int) -> float:
    sidewall_height = width * (aspect / 100)
    rim_diameter_mm = diameter * 25.4
    total_diameter = rim_diameter_mm + (2 * sidewall_height)
    return math.pi * total_diameter

def calculate_stretch_factor(tire_width: int, rim_width: float) -> str:
    ideal_width = rim_width * 25.4
    stretch_percent = (ideal_width / tire_width) * 100
    
    if stretch_percent > 115:
        return "EXTREM"
    elif stretch_percent > 110:
        return "STARK" 
    elif stretch_percent > 105:
        return "MODERAT"
    else:
        return "NORMAL"

def calculate_scene_points(width: int, aspect: int, diameter: int) -> int:
    points = 0
    
    # JDM Style Points
    if 15 <= diameter <= 17:
        points += 5
    if aspect <= 45:
        points += 10
    if 195 <= width <= 225:
        points += 5
        
    # Euro Style Points  
    if 18 <= diameter <= 20:
        points += 5
    if aspect <= 35:
        points += 15
        
    return points

def categorize_tire(deviation: float, aspect: int, scene_points: int) -> str:
    if deviation <= 1.0:
        return "🎯 Optimal"
    elif deviation <= 1.5:
        if aspect <= 45:
            return "🏁 Sportlich"
        else:
            return "👍 Empfohlen"
    elif scene_points >= 15:
        return "🔥 Scene"
    else:
        return "😌 Komfort"

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    with open("frontend.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/berechne", response_model=List[TireResult])
def berechne_kompatible_reifen(
    serien_width: int = Query(..., description="Serienreifenbreite in mm"),
    serien_aspect: int = Query(..., description="Serienflankenhöhe in Prozent"), 
    serien_diameter: int = Query(..., description="Seriendurchmesser in Zoll")
):
    serien_circumference = calculate_rolling_circumference(serien_width, serien_aspect, serien_diameter)
    min_circumference = serien_circumference * 0.975  # -2,5%
    max_circumference = serien_circumference * 1.015  # +1,5%
    
    results = []
    
    for tire in tire_database:
        for rim_width, (min_width, ideal_width, max_width) in rim_compatibility.items():
            if min_width <= tire["width"] <= max_width:
                circ = calculate_rolling_circumference(tire["width"], tire["aspect"], tire["diameter"])
                
                if min_circumference <= circ <= max_circumference:
                    deviation = abs((circ - serien_circumference) / serien_circumference) * 100
                    scene_points = calculate_scene_points(tire["width"], tire["aspect"], tire["diameter"])
                    stretch = calculate_stretch_factor(tire["width"], rim_width)
                    category = categorize_tire(deviation, tire["aspect"], scene_points)
                    tuev_friendly = deviation <= 1.5 and stretch != "EXTREM"
                    
                    results.append(TireResult(
                        width=tire["width"],
                        aspect=tire["aspect"], 
                        diameter=tire["diameter"],
                        rim_width=rim_width,
                        deviation_percent=round(deviation, 2),
                        category=category,
                        scene_points=scene_points,
                        stretch_factor=stretch,
                        tuev_friendly=tuev_friendly
                    ))
    
    # Sortieren nach Abweichung
    results.sort(key=lambda x: x.deviation_percent)
    return results

@app.get("/export")
def export_csv(
    serien_width: int,
    serien_aspect: int, 
    serien_diameter: int
):
    results = berechne_kompatible_reifen(serien_width, serien_aspect, serien_diameter)
    
    def generate_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Breite", "Flanke", "Durchmesser", "Felgenbreite", "Abweichung%", "Kategorie", "Scene Points", "Stretch", "TÜV"])
        
        for result in results:
            writer.writerow([
                result.width, result.aspect, result.diameter, result.rim_width,
                result.deviation_percent, result.category, result.scene_points, 
                result.stretch_factor, "✅" if result.tuev_friendly else "⚠️"
            ])
            
        csv_content = output.getvalue()
        output.close()
        return csv_content
    
    return StreamingResponse(
        iter([generate_csv()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=felgen_kompatibilitaet.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

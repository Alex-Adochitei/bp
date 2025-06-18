from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import ObiectivTuristic
from typing import List
import math
import openrouteservice

router = APIRouter(prefix = "/ruta", tags = ["Ruta turistica"])

ORS_API_KEY = "5b3ce3597851110001cf624893c18f31566c43bab5ab2e6a5a55952b"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def tsp_greedy(start_lat, start_lng, obiective):
    traseu = []
    current_lat, current_lng = start_lat, start_lng
    ramase = obiective.copy()

    while ramase:
        urmatorul = min(ramase, key = lambda obj: haversine(current_lat, current_lng, obj.coordonataX, obj.coordonataY))
        traseu.append(urmatorul)
        current_lat, current_lng = urmatorul.coordonataX, urmatorul.coordonataY
        ramase.remove(urmatorul)

    return traseu

def get_route_from_ors(coordonate: List[tuple]):
    client = openrouteservice.Client(key = ORS_API_KEY)
    ruta = client.directions(
        coordinates=coordonate,
        profile = 'driving-car',
        format = 'geojson'
    )
    return ruta

@router.post("/genereaza")
def genereaza_ruta(
    user_lat: float = Query(..., description = "Latitudine utilizator"),
    user_lng: float = Query(..., description = "Longitudine utilizator"),
    obiective_ids: List[int] = Query(..., description = "Lista de id-uri obiective"),
    db: Session = Depends(get_db)
):
    obiective = db.query(ObiectivTuristic).filter(ObiectivTuristic.idObiectiv.in_(obiective_ids)).all()
    obiective_ordonate = tsp_greedy(user_lat, user_lng, obiective)

    coordonate = [(user_lng, user_lat)] + [(obj.coordonataY, obj.coordonataX) for obj in obiective_ordonate]

    ruta_geojson = get_route_from_ors(coordonate)

    return {
        "geojson": ruta_geojson,
        "obiective": [
            {
                "idObiectiv": obj.idObiectiv,
                "nume": obj.nume,
                "lat": obj.coordonataX,
                "lng": obj.coordonataY
            } for obj in obiective_ordonate
        ]
    }
from database import get_db
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from routes.auth import get_current_user
from sqlalchemy.orm import Session
import models
import schemas

router = APIRouter(prefix = "/userVisits", tags = ["User Visits"])

#API ce marcheaza un obiectiv ca vizitat
@router.post("/visit", response_model = schemas.UserVisitResponseSchema)
def add_user_visit(
    user_visit: schemas.UserVisitCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    print("Request primit:", user_visit.dict()) 

    #verificam daca obiectivul a mai fost vizitat in acea zi
    existing_visit = db.query(models.UserVisits).filter_by(
        idUser = current_user.idUser, 
        idObiectiv = user_visit.idObiectiv, 
        dataVizita = user_visit.dataVizita or date.today()
    ).first()

    if existing_visit:
        raise HTTPException(status_code = 400, detail = "The objective has already been visited today.")

    #il adaugam in tabel
    db_visit = models.UserVisits(
        idUser = current_user.idUser, 
        idObiectiv = user_visit.idObiectiv, 
        dataVizita = user_visit.dataVizita or date.today()
    )
    db.add(db_visit)
    db.commit()

    return {"message": "Marked as visited.", "idObiectiv": user_visit.idObiectiv, "visited": True}


#API ce returneaza obiectivele vizitate de userul curent
@router.get("/view", response_model = list[schemas.ObiectivVizitatSimplu])
def get_user_visits(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    #luam toate vizitele din UserVisits
    visits = db.query(models.UserVisits).filter_by(
        idUser = current_user.idUser
    ).all()

    if not visits:
        raise HTTPException(status_code = 404, detail = "You have no visited objectives.")

    #pregatim lista de raspuns
    results = []
    for visit in visits:
        obiectiv = db.query(models.ObiectivTuristic).filter_by(
            idObiectiv = visit.idObiectiv
        ).first()
        if obiectiv:
            results.append({
                "idObiectiv": obiectiv.idObiectiv,
                "nume": obiectiv.nume,
                "dataVizita": visit.dataVizita
            })

    return results
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from routes.auth import get_current_user
from sqlalchemy.orm import Session
import models
import schemas

router = APIRouter(prefix = "/userSaves", tags = ["User Saves"])

#API ce salveaza un obiectiv in lista Saves a userului curent
@router.post("/save", response_model = schemas.UserSaveResponseSchema)
def add_user_save(
    user_save: schemas.UserSavesCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    print("Request primit:", user_save.dict()) 

    #verificam daca obiectivul este deja salvat
    existing_save = db.query(models.UserSaves).filter_by(
        idUser = current_user.idUser, idObiectiv = user_save.idObiectiv
    ).first()
    
    if existing_save:
        raise HTTPException(status_code = 400, detail = "The objective is already saved.")

    #il adaugam in tabel
    db_save = models.UserSaves(idUser = current_user.idUser, idObiectiv = user_save.idObiectiv)
    db.add(db_save)
    db.commit()

    return {"message": "Objective saved successfully.", "idObiectiv": user_save.idObiectiv, "saved": True}

#API pentru stergerea unui obiectiv din lista Saves
@router.delete("/{idObiectiv}", response_model = schemas.UserSaveResponseSchema)
def delete_user_save(
    idObiectiv: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    #cautam obiectivul
    db_save = db.query(models.UserSaves).filter_by(
        idUser = current_user.idUser, idObiectiv = idObiectiv
    ).first()
    
    if not db_save:
        raise HTTPException(status_code = 404, detail = "Objective not found in Saves.")
    
    #il stergem
    db.delete(db_save)
    db.commit()

    return {"message": "Objective deleted from Saves.", "idObiectiv": idObiectiv, "saved": False}

#API pentru afisarea listei de obiective salvate de user
@router.get("/view", response_model = list[schemas.ObiectivTuristicSchema])
def get_user_saves(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    #luam toate UserSaves pentru userul curent
    saves = db.query(models.UserSaves).filter_by(
        idUser = current_user.idUser
    ).all()

    if not saves:
        return {"message": "You have no saved objectives."}

    #afisam obiectivele corespunzatoare
    obiective = db.query(models.ObiectivTuristic).filter(
        models.ObiectivTuristic.idObiectiv.in_([s.idObiectiv for s in saves])
    ).all()

    #afisam poza daca este cazul
    for obiectiv in obiective:
        obiectiv.poze = db.query(models.PozeObiectiv).filter_by(
            idObiectiv = obiectiv.idObiectiv
        ).all()

    return obiective
from database import get_db
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Users
from routes.auth import get_current_user
from sqlalchemy.orm import Session
from geopy.distance import geodesic
import json
import models
import schemas

router = APIRouter(prefix = "/obiective", tags = ["Obiective Turistice"])

ZILE_ROMANA = {
    'Monday': 'Luni',
    'Tuesday': 'Marti',
    'Wednesday': 'Miercuri',
    'Thursday': 'Joi',
    'Friday': 'Vineri',
    'Saturday': 'Sambata',
    'Sunday': 'Duminica'
}

#API ce returneaza toate obiectivele turistice
@router.get("/", response_model = list[schemas.ObiectivTuristicSchema])
def get_all_obiective(
    db: Session = Depends(get_db)
):
    obiective = db.query(models.ObiectivTuristic).all()

    for obiectiv in obiective:
        obiectiv.poze = db.query(models.PozeObiectiv).filter_by(idObiectiv = obiectiv.idObiectiv).all()

    return obiective

#API ce returneaza obiectivele turistice dupa un anumit tip
@router.get("/tip/{idTip}", response_model = list[schemas.ObiectivTuristicSchema])
def get_obiective_by_tip(
    idTip: int, 
    db: Session = Depends(get_db)
):
    obiective = db.query(models.ObiectivTuristic).filter(models.ObiectivTuristic.idTip == idTip).all()

    for obiectiv in obiective:
        obiectiv.poze = db.query(models.PozeObiectiv).filter_by(idObiectiv = obiectiv.idObiectiv).all()

    return obiective

#API ce returneaza doar obiectivele turistice deschise
@router.get("/open", response_model = list[schemas.ObiectivTuristicSchema])
def get_open_obiective(
    db: Session = Depends(get_db)
):
    obiective = db.query(models.ObiectivTuristic).all()
    obiective_deschise = []

    #ora curenta si ziua curenta
    ziua_engleza = datetime.now().strftime('%A')
    ziua_curenta = ZILE_ROMANA.get(ziua_engleza)
    ora_curenta = datetime.now().strftime('%H:%M')

    for obiectiv in obiective:
        #converteste programul din JSON
        try:
            program = json.loads(obiectiv.program)
        except json.JSONDecodeError:
            continue  #daca programul e invalid, sarim peste obiectivul asta

        #obtine intervalul orar pentru ziua curenta
        interval = program.get(ziua_curenta)

        #verifica daca obiectivul e deschis conform programului
        if interval and interval != "Inchis":
            ora_start, ora_end = interval.split('-')
            if ora_start <= ora_curenta <= ora_end:
                #adauga obiectivul doar daca este deschis conform programului
                obiective_deschise.append(obiectiv)

    #adauga pozele pentru fiecare obiectiv deschis
    for obiectiv_deschis in obiective_deschise:
        obiectiv_deschis.poze = db.query(models.PozeObiectiv).filter_by(idObiectiv = obiectiv_deschis.idObiectiv).all()

    return obiective_deschise


#API care verifica daca un obiectiv este deschis sau inchis in functie de ora utilizatorului
@router.get("/status/{idObiectiv}")
def check_obiectiv_status(
    idObiectiv: int,
    db: Session = Depends(get_db)
):
    obiectiv = db.query(models.ObiectivTuristic).filter_by(idObiectiv = idObiectiv).first()

    if not obiectiv:
        raise HTTPException(status_code = 404, detail = "Obiectivul nu a fost gasit.")

    #ora curenta si ziua curenta
    ziua_engleza = datetime.now().strftime('%A')
    ziua_curenta = ZILE_ROMANA.get(ziua_engleza)
    ora_curenta = datetime.now().strftime('%H:%M')
    
    #converteste programul din JSON
    try:
        program = json.loads(obiectiv.program)
    except json.JSONDecodeError:
        return {"idObiectiv": idObiectiv, "status": "Invalid program format."}

    #obtine intervalul orar pentru ziua curenta
    interval = program.get(ziua_curenta)

    if not interval:
        return {"idObiectiv": idObiectiv, "status": "Unknown"}

    #extrage ora de deschidere si inchidere
    ora_start, ora_end = interval.split('-')

    #verificam daca ora curenta este in interval
    if ora_start <= ora_curenta <= ora_end:
        status = "Deschis"
    else:
        status = "Inchis"

    return {"idObiectiv": idObiectiv, "status": status}

#API pentru reviews
@router.post("/review")
def adauga_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    #verificam daca userul a mai lasat un review
    existing_review = db.query(models.Review).filter_by(
        idUser = current_user.idUser,
        idObiectiv = review.idObiectiv
    ).first()
    
    if existing_review:
        raise HTTPException(status_code = 400, detail = "You have already left a review.")

    #salvam reviewul
    new_review = models.Review(
        idUser = current_user.idUser,
        idObiectiv = review.idObiectiv,
        nota = review.nota,
        comentariu = review.comentariu
    )
    db.add(new_review)

    #actualizam nota si numarul de recenzii
    obiectiv = db.query(models.ObiectivTuristic).filter_by(idObiectiv = review.idObiectiv).first()

    #cautam obiectivul turistic
    if not obiectiv:
        raise HTTPException(status_code = 404, detail = "The objective was not found.")

    #recalculam media notelor si actualizam numarul de recenzii
    if obiectiv.notaRecenzii is None:
        obiectiv.notaRecenzii = review.nota
        obiectiv.numarRecenzii = 1
    else:
        total = obiectiv.notaRecenzii * obiectiv.numarRecenzii
        total += review.nota
        obiectiv.numarRecenzii += 1
        obiectiv.notaRecenzii = total / obiectiv.numarRecenzii

    db.commit()
    return {"message": "Review added successfully!"}

#API care verifica daca userul a scris deja un review
@router.get("/hasReviewed")
def has_user_reviewed(
    idObiectiv: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    #cautam daca userul a scris deja un review pentru obiectivul respectiv
    review = db.query(models.Review).filter_by(
        idUser = current_user.idUser,
        idObiectiv = idObiectiv
    ).first()

    return review is not None
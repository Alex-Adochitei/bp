from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import models
import re
import schemas

router = APIRouter(prefix = "/users", tags = ["Users"])
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto") #configurarea hashing parole

#validare cu regex
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$")

#API ce returneaza toti utilizatorii
@router.get("/", response_model = list[schemas.UserSchema])
def get_users(
    db: Session = Depends(get_db)
):
    return db.query(models.Users).all()

#API de inregistrare pentru un nou utilizator
@router.post("/register", response_model = schemas.UserSchema)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    #validare email
    if not EMAIL_REGEX.match(user.userEmail):
        raise HTTPException(status_code = 400, detail = "Invalid e-mail.")
    
    #validare parola
    if not PASSWORD_REGEX.match(user.userPassword):
        raise HTTPException(status_code = 400, detail = "The password must have at least 8 characters, one uppercase letter and one number.")
    
    #verificare duplicate
    existing_user = db.query(models.Users).filter(models.Users.userEmail == user.userEmail).first()
    if existing_user:
        raise HTTPException(status_code = 400, detail = "E-mail is already in use.")

    #hash parola
    hashed_password = pwd_context.hash(user.userPassword)

    db_user = models.Users(
        userName = user.userName,
        userEmail = user.userEmail,
        userPassword = hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

#API de stergere a utilizatorului
@router.delete("/{email}")
def delete_user(
    email: str,
    db: Session = Depends(get_db)
):
    #cautam utilizatorul
    db_user = db.query(models.Users).filter(models.Users.userEmail == email).first()
    if not db_user:
        raise HTTPException(status_code = 404, detail = "User not found.")
    
    #stergem inregistrarile dependente din UserVisits
    db.query(models.UserVisits).filter(models.UserVisits.idUser == db_user.idUser).delete()

    #stergem utilizatorul
    db.delete(db_user)
    db.commit()

    return {"message": f"User {email} deleted successfully."}

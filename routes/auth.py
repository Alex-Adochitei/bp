from database import get_db
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session

#setari JWT
SECRET_KEY = "cheia-super-secreta"
ALGORITHM = "HS256" #algoritmul de criptare pentru JWT
ACCESS_TOKEN_EXPIRE_DAYS = 30

#configurare autentificare si hashing
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto") #context pentru hash-ul parolelor
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "auth/login") #defineste modul in care se obtine tokenul

router = APIRouter(prefix = "/auth", tags = ["Authentication"]) #creeaza un router FastAPI pentru autentificare

#functie pentru generarea JWT
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy() #copiem datele in token
    expire = datetime.utcnow() + expires_delta #calculam timpul de expirare
    to_encode.update({"exp": expire}) #adaugam expirarea in token

    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM) #codificam si semnam JWTul

#API pentru login, retuneaza un JWT
@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    db_user = db.query(Users).filter(Users.userEmail == form_data.username).first() #primeste emailul si parola prin OAuth2PasswordRequestForm

    #cautam utilizatorul in bd si verificam daca acesta exista si daca parola sa este corecta
    if not db_user or not pwd_context.verify(form_data.password, db_user.userPassword):
        raise HTTPException(status_code = 400, detail = "Incorrect e-mail or password!")
    
    #generam tokenul corect pentru 30 de zile
    access_token = create_access_token(
        data = {"idUser": db_user.idUser}, 
        expires_delta = timedelta(days = ACCESS_TOKEN_EXPIRE_DAYS)
    )

    #returnam tokenul, tipul tokenului si numele utilizatorului
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "userName": db_user.userName
    }

#functie pentru obtinerea userului logat
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        print(f"Token: {token}") #afisam tokenul primit
        
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM]) #decodificam tokenul
        user_id: int = payload.get("idUser") #extragem idUser

        print(f"Decoded user_id: {user_id}") #afisam user_id

        if user_id is None:
            raise HTTPException(status_code = 401, detail = "Token invalid: user_id missing")
        
        user = db.query(Users).filter(Users.idUser == user_id).first() #cautam obiectul in bd

        if user is None:
            raise HTTPException(status_code = 401, detail = "Token invalid: user not found")
        
        return user
    
    except JWTError as e:
        print(f"JWTError: {e}") #afisam eroarea JWT
        raise HTTPException(status_code = 401, detail = "Token invalid")
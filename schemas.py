from datetime import date
from pydantic import Field, BaseModel, EmailStr
from typing import Optional, List, Annotated

#schema pentru tipul unui obiectiv turistic
class TipObiectivSchema(BaseModel):
    numeTip: str

#schema pentru o poza asociata unui obiectiv turistic
class PozeObiectivSchema(BaseModel):
    idPoza: int
    urlPoza: str

    class Config:
        from_attributes = True #permite maparea de la modelul object-relational mappers

#schema principala pentru un obiectiv turistic
class ObiectivTuristicSchema(BaseModel):
    idObiectiv: int
    nume: str
    coordonataX: float
    coordonataY: float
    stare: str
    program: str
    contact: str
    descriere: Optional[str] = None
    notaRecenzii: Optional[float] = None
    numarRecenzii: Optional[int] = None
    idTip: int
    poze: List[PozeObiectivSchema] = []

    class Config:
        from_attributes = True #permite conversia din modelul ORM

#schema pentru datele unui user
class UserSchema(BaseModel):
    idUser: int
    userName: str
    userEmail: EmailStr

    class Config:
        from_attributes = True 

#schema pentru crearea unui user nou
class UserCreate(BaseModel):
    userName: str
    userEmail: EmailStr
    userPassword: str

#schema pentru autentificarea userului
class UserLogin(BaseModel):
    userEmail: EmailStr
    userPassword: str

#schema pentru salvarea unui obiectiv de catre un user
class UserSaveSchema(BaseModel):
    idUser: int
    idObiectiv: int

    class Config:
        orm_mode = True #activeaza suport pentru conversie din ORM

#respunsul pentru actiunea de salvarea a unui obiectiv
class UserSaveResponseSchema(BaseModel):
    message: str       
    idObiectiv: int     
    saved: bool         

    class Config:
        orm_mode = True

#schema pentru cererea de salvare a unui obiectiv
class UserSavesCreate(BaseModel):
    idObiectiv: int

#schema pentru marcarea unei vizite la un obiectiv
class UserVisitCreate(BaseModel):
    idObiectiv: int
    dataVizita: date | None = None 

#raspunsul dupa ce userul a marca o vizita
class UserVisitResponseSchema(BaseModel):
    message: str
    idObiectiv: int
    visited: bool

#schema unui obiectiv vizitat
class ObiectivVizitatSimplu(BaseModel):
    idObiectiv: int
    nume: str
    dataVizita: date

    class Config:
        orm_mode = True

#schema pentru crearea unei recenzii pentru un obiectiv
class ReviewCreate(BaseModel):
    idObiectiv: int
    nota: Annotated[int, Field(ge = 1, le = 5)]
    comentariu: str | None = None

#raspuns pentru a verifica daca userul a lasat deja o recenzie
class HasReviewedResponse(BaseModel):
    reviewed: bool
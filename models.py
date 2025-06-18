from database import engine
from datetime import date
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base() #baza pentru toate clasele declarate

class TipObiectiv(Base):
    __tablename__ = "TipObiectiv"
    idTip = Column(Integer, primary_key = True, index = True)
    numeTip = Column(String(50), nullable = False)

class ObiectivTuristic(Base):
    __tablename__ = "ObiectivTuristic"

    idObiectiv = Column(Integer, primary_key = True, index = True)
    nume = Column(String(100), nullable = False)
    coordonataX = Column(Float, nullable = False)
    coordonataY = Column(Float, nullable = False)
    stare = Column(String(10), nullable = False, default = "Deschis")
    program = Column(String, nullable = False)
    contact = Column(String, nullable = False)
    descriere = Column(String)
    notaRecenzii = Column(Float)
    numarRecenzii = Column(Integer)
    idTip = Column(Integer, ForeignKey("TipObiectiv.idTip"))

    poze = relationship("PozeObiectiv", back_populates = "obiectiv")

class PozeObiectiv(Base):
    __tablename__ = "PozeObiectiv"

    idPoza = Column(Integer, primary_key = True, index = True)
    idObiectiv = Column(Integer, ForeignKey("ObiectivTuristic.idObiectiv", ondelete = "CASCADE"))
    urlPoza = Column(String, nullable = False)

    obiectiv = relationship("ObiectivTuristic", back_populates = "poze")

class Users(Base):
    __tablename__ = "Users"
    idUser = Column(Integer, primary_key = True, index = True)
    userName = Column(String(100), nullable = False)
    userEmail = Column(String(100), unique = True, nullable = False)
    userPassword = Column(String, nullable = False)

class UserSaves(Base):
    __tablename__ = "UserSaves"
    idUser = Column(Integer, ForeignKey("Users.idUser", ondelete = "CASCADE"), primary_key = True)
    idObiectiv = Column(Integer, ForeignKey("ObiectivTuristic.idObiectiv", ondelete = "CASCADE"), primary_key = True)

class UserVisits(Base):
    __tablename__ = "UserVisits"
    idUser = Column(Integer, ForeignKey("Users.idUser"), primary_key = True)
    idObiectiv = Column(Integer, ForeignKey("ObiectivTuristic.idObiectiv"), primary_key = True)
    dataVizita = Column(Date, default = date.today(), primary_key = True)

class Review(Base):
    __tablename__ = "Reviews"
    idReview = Column(Integer, primary_key = True, index = True)
    idUser = Column(Integer, ForeignKey("Users.idUser", ondelete = "CASCADE"))
    idObiectiv = Column(Integer, ForeignKey("ObiectivTuristic.idObiectiv", ondelete = "CASCADE"))
    nota = Column(Integer, nullable = False)
    comentariu = Column(String)
    dataReview = Column(Date, default = date.today())

    user = relationship("Users")
    obiectiv = relationship("ObiectivTuristic")

Base.metadata.create_all(bind = engine) #creeaza tabelele in baza de date pe baza modelelor de mai sus
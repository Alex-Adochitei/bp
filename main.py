from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import obiective, ruta, users, userSaves, auth, userVisits
import uvicorn
import threading
import webbrowser
import time

app = FastAPI(title = "BucovinaWanders Beckend", version = "1.0") #instanta FastAPI

#inregistrare rute din fisiere separate
app.include_router(obiective.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(userSaves.router)
app.include_router(userVisits.router)
app.include_router(ruta.router)

def open_swagger():
    time.sleep(1) 
    webbrowser.open("http://127.0.0.1:8000/docs") #deschide interfata swagger in browser

#ruleaza aplicatia cand fisierul este executat direct
if __name__ == "__main__":
    threading.Thread(target = open_swagger).start() #ruleaza open_swagger intr-un fir de executie separat
    uvicorn.run("main:app", host = "127.0.0.1", port = 8000, reload = True)
    #uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)

#middleware pentru CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], #permite orice origine
    allow_credentials = True, #permite trimiterea de cookieuri
    allow_methods = ["*"], #permite toate metodele HTTP
    allow_headers = ["*"], #permite rotate headerele
)
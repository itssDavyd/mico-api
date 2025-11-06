import os
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()

SESSION_TOKEN = os.getenv("SESSION_TOKEN", "32pNKMho7HhIbJPyDksH")
USERNAME = os.getenv("FIRST_USERNAME", "admin")
PASSWORD = os.getenv("FIRST_PASWORD", "5kh57g8WONIMk5g137wt")

class LoginData(BaseModel):
    username: str
    password: str


def verify_session(request: Request):
    token = request.cookies.get("session")
    if token != SESSION_TOKEN:
        raise HTTPException(status_code=401, detail="No autorizado")

@router.post("/login")
def login(data: LoginData, response: Response):
    if data.username == USERNAME and data.password == PASSWORD:
        response.set_cookie(key="session", value=SESSION_TOKEN, httponly=True, samesite="lax", secure=False)
        return {"mensaje": "Login correcto"}
    
    raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

@router.get("/logout")
def logout(response: Response):
    response.delete_cookie("session")
    
    return {"mensaje": "Logout correcto"}

@router.get("/protected")
def protected(request: Request, _=Depends(verify_session)):
    return {"mensaje": f"Hola {USERNAME}, esta ruta está protegida"}
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from config import get_settings

router = APIRouter()


class LoginData(BaseModel):
    username: str
    password: str


def verify_session(request: Request) -> None:
    settings = get_settings()
    token = request.cookies.get("session")
    if token != settings.session_token:
        raise HTTPException(status_code=401, detail="No autorizado")


@router.post("/login")
def login(data: LoginData, response: Response) -> dict[str, str]:
    settings = get_settings()
    if data.username == settings.first_username and data.password == settings.first_password:
        response.set_cookie(
            key="session",
            value=settings.session_token,
            httponly=True,
            samesite="lax",
            secure=False,
        )
        return {"mensaje": "Login correcto"}

    raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")


@router.get("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("session")
    return {"mensaje": "Logout correcto"}


@router.get("/protected")
def protected(_: None = Depends(verify_session)) -> dict[str, str]:
    settings = get_settings()
    return {"mensaje": f"Hola {settings.first_username}, esta ruta está protegida"}

from fastapi import APIRouter

from app.api.v1.routes import platform as platform_routes
from app.api.v1.routes.platform import LoginPayload, RegisterPayload

router = APIRouter()


@router.post("/signup")
def signup(payload: RegisterPayload):
    return platform_routes.register(payload)


@router.post("/login")
def login(payload: LoginPayload):
    return platform_routes.login(payload)


@router.get("/me")
def me(user_id: str):
    return platform_routes.me(user_id)

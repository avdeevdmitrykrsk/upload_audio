from fastapi import APIRouter

from app.api.endpoints import audio_file_router, auth_router, user_router

main_router = APIRouter(prefix='/api')

main_router.include_router(audio_file_router)
main_router.include_router(auth_router)
main_router.include_router(user_router)

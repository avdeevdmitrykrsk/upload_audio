from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routers import main_router

app = FastAPI()
app.include_router(main_router)

app.mount('/uploads', StaticFiles(directory='uploads'), name='uploads')

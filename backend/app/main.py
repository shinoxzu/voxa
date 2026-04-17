from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import AppProvider, RequestProvider
from app.routes.meetings import router as meetings_router

app = FastAPI(title="Voxa")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

container = make_async_container(AppProvider(), RequestProvider())
setup_dishka(container, app)

app.include_router(meetings_router, prefix="/api")

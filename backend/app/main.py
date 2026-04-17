import logging

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import AppProvider, RequestProvider
from app.routes.meetings import router as meetings_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    force=True,
)

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

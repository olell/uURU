"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler
from sqlmodel import Session
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.db import engine, engine_asterisk, init_asterisk_db, init_db, drop_db
from app.core.config import settings

from app.api.main import router as api_router
from app.telephoning.websip import WebSIPManager
from app.telephoning.main import Telephoning

background_scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with Session(engine) as session:
        init_db(session)

    with Session(engine_asterisk) as session_asterisk:
        init_asterisk_db(session_asterisk)

    Telephoning.instance().start(app, background_scheduler)
    background_scheduler.add_job(
        WebSIPManager.instance().job, "interval", seconds=30, args=[engine_asterisk]
    )
    background_scheduler.start()

    yield

    Telephoning.instance().stop()
    background_scheduler.shutdown()

    with Session(engine_asterisk) as session_asterisk:
        WebSIPManager.instance().teardown(session_asterisk)

    if settings.LIFESPAN_DROP_DB:
        drop_db()


logging.basicConfig(
    level=settings.logging_loglevel,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

logger.info("Foo Bar!")

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(api_router, prefix=settings.API_V1_STR)

build_path = Path("frontend/build")
app.mount("/app", StaticFiles(directory=build_path), name="static")


@app.middleware("http")
async def fallback(request: Request, call_next):
    if request.url.path.startswith("/app"):
        relative_path = request.url.path.removeprefix("/app/").strip("/")
        target_file = build_path / relative_path

        if not target_file.is_file() or target_file == build_path:
            return FileResponse(build_path / "index.html")

    return await call_next(request)


@app.get("/")
def index():
    return RedirectResponse("/app/")


app.mount(
    "/static/telephoning",
    StaticFiles(directory="static/telephoning"),
    name="static",
)

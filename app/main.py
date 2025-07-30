from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler
from sqlmodel import Session

from app.core.db import engine, init_db, drop_db
from app.core.config import settings

from app.api.main import router as api_router
from app.web.main import router as web_router
from app.telephoning.main import Telephoning


@asynccontextmanager
async def lifespan(app: FastAPI):
    with Session(engine) as session:
        init_db(session)

    Telephoning.instance().start(app)

    yield

    Telephoning.instance().stop()

    if settings.LIFESPAN_DROP_DB:
        drop_db()


app = FastAPI(
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# @app.exception_handler(403)
# @app.exception_handler(404)
# @app.exception_handler(HTTPException)
# async def web_exception_handler(request: Request, exc: HTTPException):
#     # keep default handler for api
#     if str(request.url.path).startswith(settings.API_V1_STR):
#         return await http_exception_handler(request, exc)

#     return RedirectResponse(f"/error/{exc.status_code}")


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(web_router, prefix=settings.WEB_PREFIX)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def add_session_cookie(request: Request, call_next):
    sessid = None
    set_sessid = False
    if request.cookies.get("session", None) is None:
        set_sessid = True
        sessid = str(uuid.uuid4())
        request.cookies.update({"session": sessid})
    response = await call_next(request)

    if set_sessid:
        response.set_cookie(key="session", value=sessid)

    return response


# @app.middleware("http")
# async def handle_exception_web(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception as e:
#         if str(request.url.path).startswith(settings.API_V1_STR):
#             raise e

#         if isinstance(e, HTTPException):
#             return RedirectResponse(f"/error/{e.status_code}")
#         else:
#             return RedirectResponse("/error/0")

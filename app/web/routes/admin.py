from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.db import SessionDep
from app.models.crud.user import filter_user_by_username
from app.web.templates import templates
from app.web.deps import AdminUser

router = APIRouter(prefix="/admin")

@router.get("/users", response_class=HTMLResponse)
def user_list_page(request: Request, session: SessionDep, user: AdminUser, query: Optional[str] = None):
    users = filter_user_by_username(session, query)
    return templates.TemplateResponse(request, "admin/userlist.j2.html", {
        "user": user,
        "users": users
    })
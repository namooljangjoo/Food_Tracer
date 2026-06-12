import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from admin_service import build_admin_report

load_dotenv()

app = FastAPI(title="FoodTracer Dashboard")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()


def require_dashboard_password(
    credentials: HTTPBasicCredentials = Depends(security),
):
    expected_password = os.getenv("WEB_DASHBOARD_PASSWORD")

    if not expected_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard password is not configured.",
        )

    password_ok = secrets.compare_digest(
        credentials.password,
        expected_password,
    )

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid dashboard credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    authenticated: bool = Depends(require_dashboard_password),
):
    report = build_admin_report()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "report": report,
        },
    )

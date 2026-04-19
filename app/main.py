'''Main application file for the Admission Management System.'''
from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine, Base
from app import models
from app import auth
from app.routes import setup, program, applicant, admission, dashboard

app = FastAPI(title="Admission Management System", version="1.0")

# Session middleware (secret key should be changed in production)
app.add_middleware(SessionMiddleware, secret_key="dev-secret-key-change-in-production")

# Create tables in database
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
except Exception as e:
    print(f"Error creating database tables: {e}")
    raise

# Include API routes
app.include_router(setup.router)
app.include_router(program.router)
app.include_router(applicant.router)
app.include_router(admission.router)
app.include_router(dashboard.router)

# Templates
templates = Jinja2Templates(directory="app/templates")


# ==========================================
# AUTH DEPENDENCIAS
# ==========================================

def get_current_user(request: Request):
    """Return current logged-in user from session, or None."""
    return request.session.get("user")


def require_login(request: Request):
    """Require user to be logged in, else redirect to login."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return user


def require_role(request: Request, allowed_roles: list):
    """Require user to have one of the allowed roles, else redirect to login."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if user["role"] not in allowed_roles:
        return RedirectResponse(url="/dashboard", status_code=303)
    return user


# ==========================================
# AUTH ROUTES
# ==========================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """Serve the login page."""
    # If already logged in, redirect to role-appropriate page
    user = request.session.get("user")
    if user:
        return RedirectResponse(url=get_role_based_redirect_url(user), status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"error": error or ""})


@app.post("/login")
async def login(request: Request):
    """Process login form submission."""
    form = await request.form()
    
    # Safely extract form values
    username_raw = form.get("username")  # type: ignore
    password_raw = form.get("password")  # type: ignore
    
    # Convert to strings safely
    username = str(username_raw).strip() if username_raw is not None else ""
    password = str(password_raw) if password_raw is not None else ""

    user = auth.verify_password(username, password)
    if not user:
        return RedirectResponse(url="/login?error=Invalid+username+or+password", status_code=303)

    request.session["user"] = user
    
    # Redirect based on user role
    return RedirectResponse(url=get_role_based_redirect_url(user), status_code=303)


@app.post("/logout")
async def logout(request: Request):
    """Clear session and redirect to login."""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


def get_role_based_redirect_url(user: dict) -> str:
    """Get the appropriate redirect URL based on user role."""
    if user["role"] == "admin":
        return "/ui/setup"
    elif user["role"] == "officer":
        return "/ui/admissions"
    else:  # viewer
        return "/dashboard"


# ==========================================
# UI ROUTING (JINJA2 TEMPLATES)
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def root_redirect(request: Request):
    """Redirect root based on user role."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url=get_role_based_redirect_url(user), status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_ui(request: Request):
    """
    Serves the frontend Management Dashboard shell.
    The data will be loaded dynamically via JavaScript (fetch).
    """
    if not request.session.get("user"):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request, name="dashboard.html",
        context={"current_user": request.session.get("user")}
    )

@app.get("/ui/setup", response_class=HTMLResponse)
async def setup_ui(request: Request):
    """Serves the Admin Setup page (admin only)."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if user["role"] != "admin":
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request, name="setup.html",
        context={"current_user": user}
    )

@app.get("/ui/admissions", response_class=HTMLResponse)
async def admissions_ui(request: Request):
    """Serves the Admission Officer page (admin or officer only)."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if user["role"] not in ("admin", "officer"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request, name="admissions.html",
        context={"current_user": user}
    )

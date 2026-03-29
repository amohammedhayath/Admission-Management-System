"""Simple hardcoded-user authentication for the Admission Management System."""
from typing import Optional

# Hardcoded users: username -> {password, role, display_name}
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "display_name": "Administrator",
    },
    "officer": {
        "password": "officer123",
        "role": "officer",
        "display_name": "Admission Officer",
    },
    "viewer": {
        "password": "viewer123",
        "role": "viewer",
        "display_name": "Viewer",
    },
}

# Role access map: role -> list of allowed pages/prefixes
ROLE_ACCESS = {
    "admin": ["/", "/dashboard", "/ui/setup", "/ui/admissions", "/ui/dashboard",
              "/programs", "/applicants", "/admissions", "/setup", "/dashboard"],
    "officer": ["/", "/dashboard", "/ui/admissions", "/ui/dashboard",
                "/programs", "/applicants", "/admissions", "/dashboard"],
    "viewer": ["/", "/dashboard", "/ui/dashboard", "/dashboard/stats"],
}


def verify_password(username: str, password: str) -> Optional[dict]:
    """Verify username/password and return user data (without password) or None."""
    user = USERS.get(username)
    if user and user["password"] == password:
        return {"username": username, "role": user["role"], "display_name": user["display_name"]}
    return None


def get_user(username: str) -> Optional[dict]:
    """Return user data without password, or None."""
    user = USERS.get(username)
    if user:
        return {"username": username, "role": user["role"], "display_name": user["display_name"]}
    return None


def can_access(role: str, path: str) -> bool:
    """Check if a role can access a given path."""
    allowed = ROLE_ACCESS.get(role, [])
    return any(path.startswith(p) for p in allowed)

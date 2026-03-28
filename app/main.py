'''Main application file for the Admission Management System.'''
from fastapi import FastAPI
from app.database import engine, Base

# Import models (VERY IMPORTANT)
from app import models

# Import routes
from app.routes import program
from app.routes import applicant
from app.routes import admission
from app.routes import dashboard

app = FastAPI()


# Create tables in database
Base.metadata.create_all(bind=engine)


# Include routes
app.include_router(program.router)
app.include_router(applicant.router)
app.include_router(admission.router)
app.include_router(dashboard.router)


@app.get("/")
async def read_root():
    return {"message": "Admission Management System Running"}

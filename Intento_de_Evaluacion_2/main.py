import patch_pydantic 
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from models.vuelo import Base
from database import engine
from api.endpoints import router as vuelos_router
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


# Crear la tabla de base de datos, si no esta creado el archivo lo crea.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión de Vuelos",
    description="API para gestión de vuelos en aeropuerto usando lista doblemente enlazada",
    version="1.0.0"
)

app.include_router(vuelos_router, prefix="/vuelos")

@app.get("/")
def read_root():
    return {"message": "Bienvenido al Sistema de Gestión de Vuelos"}

@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request, exc):
    if "UNIQUE constraint failed" in str(exc):
        return JSONResponse(
            status_code=400,
            content={"detail": "El número de vuelo ya existe."},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Error de base de datos."},
    )
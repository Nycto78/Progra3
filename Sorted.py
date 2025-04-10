from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Prioridad_Colas_Base import PrioridadColaSorted
from database import SessionLocal
from Tabla import Mision, Personaje, MisionPersonaje
import datetime

app = FastAPI()
cola_prioridad = PrioridadColaSorted()

# Modelos de entrada
class MisionPrioridad(BaseModel):
    nombre: str
    descripcion: str
    prioridad: int
    personaje_id: int 

# Obtener sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Agregar misión con prioridad y personaje
@app.post("/misiones_prioridad/")
def agregar_mision_prioridad(mision: MisionPrioridad, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).filter(Personaje.id == mision.personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    # Encolar misión en estructura de prioridad
    cola_prioridad.add(mision.prioridad, {
        "nombre": mision.nombre,
        "descripcion": mision.descripcion,
        "personaje_id": mision.personaje_id
    })

    # Guardar misión en la base de datos
    nueva_mision = Mision(
        nombre=mision.nombre,
        descripcion=mision.descripcion,
        estado="pendiente",
        experiencia=10,
        fecha_creacion=datetime.datetime.utcnow()
    )
    db.add(nueva_mision)
    db.commit()
    db.refresh(nueva_mision)

    # Relacionar misión con personaje
    relacion = MisionPersonaje(
        personaje_id=personaje.id,
        mision_id=nueva_mision.id,
        orden=0
    )
    db.add(relacion)
    db.commit()

    return {
        "message": "Misión con prioridad agregada y asignada",
        "prioridad": mision.prioridad,
        "personaje": personaje.nombre
    }

# Ver todas las misiones pendientes en la cola
@app.get("/misiones_prioridad/todas/")
def ver_todas():
    return {"misiones": cola_prioridad.ver_todo()}

# Completar la siguiente misión en la cola
@app.post("/misiones_prioridad/siguiente/")
def siguiente_mision(db: Session = Depends(get_db)):
    if cola_prioridad.is_empty():
        return {"message": "No hay misiones en la cola"}

    prioridad, val = cola_prioridad.remove_min()

    # Buscar misión en base de datos
    mision_db = db.query(Mision).filter(Mision.nombre == val["nombre"]).first()
    if not mision_db:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    # Marcar como completada
    mision_db.estado = "completada"
    db.commit()

    # Relación misión-personaje
    relacion = db.query(MisionPersonaje).filter(MisionPersonaje.mision_id == mision_db.id).first()
    personaje = db.query(Personaje).filter(Personaje.id == relacion.personaje_id).first() if relacion else None

    if personaje:
        personaje.experiencia += mision_db.experiencia
        personaje.nivel = personaje.experiencia // 70
        db.commit()

    return {
        "message": "Misión completada",
        "mision": {
            "nombre": mision_db.nombre,
            "descripcion": mision_db.descripcion,
            "prioridad": prioridad,
            "estado": mision_db.estado
        },
        "personaje_asignado": {
            "id": personaje.id,
            "nombre": personaje.nombre,
            "experiencia": personaje.experiencia,
            "nivel": personaje.nivel
        } if personaje else None
    }

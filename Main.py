from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, engine
from Tabla import Base, Mision, Personaje, MisionPersonaje
from TDA_Cola_config import ColaArray
from Prioridad_Colas_Base import PrioridadColaSorted
import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()
cola_misiones = ColaArray()
cola_personajes = ColaArray()
cola_prioridad = PrioridadColaSorted()
colas_por_personaje = {}

# Obtener la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear personaje
@app.post("/personaje")
def crear_personaje(nombre: str, nivel: int, db: Session = Depends(get_db)):
    nuevo = Personaje(nombre=nombre, nivel=nivel, experiencia=0)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    cola_personajes.enqueue(nuevo.id)
    return {"message": "Personaje creado", "id": nuevo.id}

# Crear mision

@app.post("/misiones")
def crear_mision(
    nombre: str,
    descripcion: str,
    prioridad: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    nueva = Mision(
        nombre=nombre,
        descripcion=descripcion,
        estado="pendiente",
        fecha_creacion=datetime.datetime.utcnow()
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    cola_prioridad.add(prioridad, nueva.id)

    return {
        "message": "Misión creada",
        "id": nueva.id,
        "prioridad": prioridad
    }

# Aceptar mision
@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(personaje_id)
    mision = db.query(Mision).get(mision_id)
    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrada")

    if personaje_id not in colas_por_personaje:
        colas_por_personaje[personaje_id] = ColaArray()

    colas_por_personaje[personaje_id].enqueue(mision_id)

    asignacion = MisionPersonaje(personaje_id=personaje_id, mision_id=mision_id)
    db.add(asignacion)
    db.commit()
    return {"message": "Misión aceptada por personaje", "personaje_id": personaje_id, "mision_id": mision_id}

# Completar misión
@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, experiencia: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    if personaje_id not in colas_por_personaje or colas_por_personaje[personaje_id].is_empty():
        raise HTTPException(status_code=400, detail="No hay misiones en la cola para este personaje")

    mision_id = colas_por_personaje[personaje_id].dequeue()
    mision = db.query(Mision).get(mision_id)

    if not mision or mision.estado == "completada":
        raise HTTPException(status_code=404, detail="Misión no encontrada o ya completada")

    mision.estado = "completada"
    personaje.experiencia += experiencia
    db.commit()

    return {
        "message": "Misión completada",
        "mision_id": mision.id,
        "mision_nombre": mision.nombre,
        "experiencia_total": personaje.experiencia
    }

# Listar misiones FIFO del personaje
@app.get("/personajes/{personaje_id}/misionesListar")
def listar_misiones_de_personaje(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    # Si no hay cola en memoria, intentamos reconstruirla desde la base de datos
    if personaje_id not in colas_por_personaje:
        colas_por_personaje[personaje_id] = ColaArray()
        asignaciones = db.query(MisionPersonaje).filter_by(personaje_id=personaje_id).order_by(MisionPersonaje.id.asc()).all()
        for asignacion in asignaciones:
            colas_por_personaje[personaje_id].enqueue(asignacion.mision_id)

    cola = colas_por_personaje.get(personaje_id)
    if not cola or cola.esta_vacia():
        return {"message": f"{personaje.nombre} no tiene misiones en cola"}

    ids = cola.obtener_lista()
    resultado = []
    for i, m_id in enumerate(ids):
        m = db.query(Mision).get(m_id)
        estado = "activa" if i == len(ids) - 1 else "pendiente"
        if m:
            resultado.append({
                "id": m.id,
                "nombre": m.nombre,
                "descripcion": m.descripcion,
                "estado": estado
            })

    return {
        "personaje": personaje.nombre,
        "misiones": resultado
    }
    
# Activar nueva misión (abandonar actual)
@app.post("/personajes/{id}/siguienteMision")
def siguiente_mision_personaje(id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    cola = colas_por_personaje.get(id)
    if not cola or cola.esta_vacia():
        raise HTTPException(status_code=404, detail="No hay misiones en cola para este personaje")

    # Marcar misión activa anterior como "abandonada"
    for m_id in cola.obtener_lista():
        mision_db = db.query(Mision).get(m_id)
        if mision_db and mision_db.estado == "activa":
            mision_db.estado = "abandonada"
            db.commit()
            break

    nueva_id = cola.obtener_lista()[-1]
    nueva_mision = db.query(Mision).get(nueva_id)
    if nueva_mision:
        nueva_mision.estado = "activa"
        db.commit()

    return {
        "message": f"{personaje.nombre} abandonó su misión activa. Ahora está activa la última misión añadida.",
        "nueva_mision_activa": {
            "id": nueva_mision.id,
            "nombre": nueva_mision.nombre,
            "descripcion": nueva_mision.descripcion,
            "estado": nueva_mision.estado
        }
    }

# Obtener cantidad de misiones aceptadas
@app.get("/personajes/{id}/misionesCantidad")
def cantidad_misiones_personaje(id: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    cantidad = db.query(MisionPersonaje).filter(MisionPersonaje.personaje_id == id).count()

    return {
        "personaje": personaje.nombre,
        "cantidad_misiones": cantidad
    }

# Listar misiones no aceptadas aún
@app.get("/misiones/no-aceptadas")
def listar_misiones_no_aceptadas(db: Session = Depends(get_db)):
    subquery = db.query(MisionPersonaje.mision_id).subquery()
    misiones_no_aceptadas = db.query(Mision).filter(Mision.id.not_in(subquery)).all()
    return misiones_no_aceptadas

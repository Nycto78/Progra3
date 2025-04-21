from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.lista_vuelos import ListaVuelos
from models.vuelo import Vuelo
from schemas.vuelo import CrearVuelo, Respuestavuelo
from database import get_db

router = APIRouter()

# Lista doblemente enlazada
lista_vuelos = ListaVuelos()

@router.post("/vuelos", response_model=Respuestavuelo)
def agregar_vuelo(vuelo: CrearVuelo, db: Session = Depends(get_db)):
    # Verificar si el vuelo ya existe
    vuelo_existente = db.query(Vuelo).filter(Vuelo.numero_vuelo == vuelo.numero_vuelo).first()
    if vuelo_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un vuelo con el número {vuelo.numero_vuelo}"
        )
    db_vuelo = Vuelo(**vuelo.dict())
    db.add(db_vuelo)
    db.commit()
    db.refresh(db_vuelo)
    
    if vuelo.emergencia:
        lista_vuelos.insertar_al_frente(db_vuelo)
    else:
        lista_vuelos.insertar_al_final(db_vuelo)
    
    return db_vuelo

@router.get("/vuelos/total")
def obtener_total_vuelos():
    """Retorna el número total de vuelos en cola"""
    return {"total_vuelos": len(lista_vuelos)}

@router.get("/vuelos/proximo", response_model=Respuestavuelo)
def obtener_proximo_vuelo():
    """Retorna el primer vuelo sin remover"""
    vuelo = lista_vuelos.obtener_primero()
    if not vuelo:
        raise HTTPException(status_code=404, detail="No hay vuelos en cola")
    return vuelo

@router.get("/vuelos/ultimo", response_model=Respuestavuelo)
def obtener_ultimo_vuelo():
    """Retorna el último vuelo sin remover"""
    vuelo = lista_vuelos.obtener_ultimo()
    if not vuelo:
        raise HTTPException(status_code=404, detail="No hay vuelos en cola")
    return vuelo

@router.post("/vuelos/insertar", response_model=Respuestavuelo)
def insertar_vuelo_posicion(vuelo: CrearVuelo, posicion: int, db: Session = Depends(get_db)):
    """Inserta un vuelo en una posición específica"""
    db_vuelo = Vuelo(**vuelo.dict())
    db.add(db_vuelo)
    db.commit()
    db.refresh(db_vuelo)
    
    lista_vuelos.insertar_en_posicion(db_vuelo, posicion)
    return db_vuelo

@router.delete("/vuelos/extraer", response_model=Respuestavuelo)
def extraer_vuelo_posicion(posicion: int, db: Session = Depends(get_db)):
    """Remueve un vuelo de una posición dada"""
    try:
        vuelo = lista_vuelos.extraer_de_posicion(posicion)
        # Actualizar estado en la base de datos
        db_vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo.id).first()
        db_vuelo.estado = "Cancelado"
        db.commit()
        return vuelo
    except IndexError:
        raise HTTPException(status_code=404, detail="Posición inválida")

@router.get("/vuelos/lista")
def listar_vuelos():
    """Lista todos los vuelos en orden actual"""
    return lista_vuelos.listar_vuelos()

@router.patch("/vuelos/reordenar")
def reordenar_vuelos(posicion_origen: int, posicion_destino: int, db: Session = Depends(get_db)):
    """Reordena un vuelo de una posición a otra en la lista doblemente enlazada"""
    try:
        # Extraer el vuelo de la posición origen
        vuelo = lista_vuelos.extraer_de_posicion(posicion_origen)
        
        # Insertar en la nueva posición
        lista_vuelos.insertar_en_posicion(vuelo, posicion_destino)
        
        # Actualizar la base de datos (si es necesario)
        db_vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo.id).first()
        if db_vuelo:
            db.commit()  
        
        return {
            "mensaje": f"Vuelo movido de posición {posicion_origen} a {posicion_destino}",
            "vuelo": vuelo.numero_vuelo,
            "nueva_posicion": posicion_destino,
            "lista_actual": [v.numero_vuelo for v in lista_vuelos.listar_vuelos()]
        }
        
    except IndexError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Posición inválida: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al reordenar vuelos: {str(e)}"
        )
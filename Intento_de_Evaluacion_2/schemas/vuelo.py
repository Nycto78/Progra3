from pydantic import BaseModel
from datetime import datetime

'''Interaciones'''
class VueloBase(BaseModel):
    numero_vuelo: str
    aerolinea: str
    origen: str
    destino: str
    hora_programada: datetime
    emergencia: bool = False
    estado: str = "Programado"

class CrearVuelo(BaseModel):
    numero_vuelo: str 
    aerolinea: str
    origen: str
    destino: str
    hora_programada: datetime
    emergencia: bool = False
    estado: str = "Programado"

class Respuestavuelo(VueloBase):
    id: int
    
    class Config:
        orm_mode = True
        from_attributes = True
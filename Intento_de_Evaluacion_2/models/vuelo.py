from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base

class Vuelo(Base):
    __tablename__ = 'vuelos'
    '''Data de vuelos'''
    id = Column(Integer, primary_key=True, index=True)
    numero_vuelo = Column(String, unique=True, index=True)
    aerolinea = Column(String)
    origen = Column(String)
    destino = Column(String)
    hora_programada = Column(DateTime)
    emergencia = Column(Boolean, default=False)
    estado = Column(String, default="Programado")  # Programado, Retrasado, Cancelado
    
    def __repr__(self):
        return f"<Vuelo {self.numero_vuelo} {self.origen}-{self.destino}>"
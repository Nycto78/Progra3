from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Personaje(Base):
    __tablename__ = "personajes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    nivel = Column(Integer, default=1)
    experiencia = Column(Integer)

    misiones_asignadas = relationship("MisionPersonaje", back_populates="personaje")

class Mision(Base):
    __tablename__ = "misiones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    estado = Column(String, default="pendiente")
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)

    asignaciones = relationship("MisionPersonaje", back_populates="mision")

class MisionPersonaje(Base):
    __tablename__ = "misiones_personaje"

    id = Column(Integer, primary_key=True, index=True)
    personaje_id = Column(Integer, ForeignKey("personajes.id"))
    mision_id = Column(Integer, ForeignKey("misiones.id"))

    personaje = relationship("Personaje", back_populates="misiones_asignadas")
    mision = relationship("Mision", back_populates="asignaciones")
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Opinion(Base):
    __tablename__ = 'opiniones'

    id = Column(Integer, primary_key=True, index=True)
    trabajador_id = Column(Integer, nullable=False)
    comentario = Column(String, nullable=False)
    calificacion = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.now(timezone.utc))








""" Terminado without-extra-data-1.py, la version mas simple, sin datos extra de:
10/2 agrega altas y mantiene registros anteriores
https://github.com/ben519/fastapi-many-to-many/blob/master/without-extra-data-1.py
Se creó la mase de datos mydb.db para que no de el error que daba originalmente
Para ejecutar hay que borrar primero la base mydb.db. 

La version posterior debe preservar la base e incorporar las altas y bajas.

FastAPI app called 'Laburing' that serves information about Servicios y Trabajadores. A simple example of a
"many-to-many" relationship *without* extra data.
27 de marzo 2025 ultima versión
"""
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select, Select
from sqlalchemy.orm import declarative_base, relationship, joinedload
from sqlalchemy.schema import PrimaryKeyConstraint
from typing import Annotated, Optional
from sqlmodel import SQLModel, Field
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from fastapi.staticfiles import StaticFiles

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]
###import models
from sqlalchemy.pool import SingletonThreadPool
engine = create_engine('sqlite:///mydb.db',
                poolclass=SingletonThreadPool)
# Make the DeclarativeMeta
Base = declarative_base()

# Declare Classes / Tables
#nuevos############### 28 / 3
class Usuarios_Servicios_Trabajadores(Base):
    __tablename__ = 'usuarios_servicios_trabajadores'
    ##id = Column(Integer, primary_key=True)
    # clave compuesta por el servicio + el trabajador
    #SQLite does not support autoincrement for composite primary keys
    usuario_id = Column ('usuario_id', ForeignKey('usuarios.id'), primary_key=True)
    servicio_trabajador_id = Column('servicio_trabajador_id', ForeignKey('servicios_trabajadores.id'), primary_key=True)


###############  
class Servicios_Trabajadores(Base):
    __tablename__ = 'servicios_trabajadores'
    id = Column(Integer, primary_key=True)
    # clave compuesta por el servicio + el trabajador
    #SQLite does not support autoincrement for composite primary keys
    servicio_id = Column ('servicio_id', ForeignKey('servicios.id'), primary_key=True)
    trabajador_id = Column('trabajador_id', ForeignKey('trabajadores.id'), primary_key=True)
    precioxhora = Column ('precioxhora',Integer)
     #nuevos############### 28 / 3
    usuarios = relationship("Usuario", secondary="usuarios_servicios_trabajadores", back_populates='servicios_trabajadores')  
    #trabajadores = relationship("Trabajador", secondary="servicios", back_populates='servicios_trabajadores')  

    ###############       
class Servicios_TrabajadoresUpdate(SQLModel):
    precioxhora: int | None = None
      

class Servicio(Base):
    __tablename__ = 'servicios'
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    trabajadores = relationship("Trabajador", secondary="servicios_trabajadores", back_populates='servicios')

class Trabajador(Base):
    __tablename__ = 'trabajadores'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    dni = Column(String, nullable=False)
    correoElec = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    localidad = Column(String, nullable=False)
    wsapp = Column(String, nullable=False)
    foto = Column(String, nullable=False)
    penales = Column(String, nullable=False)
    servicios = relationship("Servicio", secondary="servicios_trabajadores", back_populates='trabajadores')

    #nuevos############### 28 / 3

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    dni = Column(String, nullable=False)
    correoElec = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    localidad = Column(String, nullable=False)
    wsapp = Column(String, nullable=False)
    servicios_trabajadores = relationship("Servicios_Trabajadores", secondary="usuarios_servicios_trabajadores", back_populates='usuarios')

#nuevos############### 28 / 3

class TrabajadorUpdate(SQLModel):
    #id: int | None = None
    #nombre: str | None = None
    #dni: str | None = None
    # los campos anteriores no se pueden actualizar
    correoElec: str | None = None
    direccion: str | None = None
    localidad: str | None = None
    wsapp: str | None = None
    penales: str | None = None

###

class UsuarioBase(SQLModel):
    nombre: str = Field(index=True)

class TrabajadorBase(SQLModel):
    nombre: str = Field(index=True)

#nuevo
class ServicioTrabajadorBase(SQLModel):
    precioxhora: int = Field(index=True)
##### nuevo 28 / 3
class ServicioTrabajadorBase(SQLModel):
    precioxhora: int = Field(index=True)


class TrabajadorPublic(TrabajadorBase):
    id: int
##### nuevo
class ServicioTrabajadorPublic(ServicioTrabajadorBase):
    id: int

##############################  
    
# Create the tables in the database
Base.metadata.create_all(engine)

# Insert data, en la práctica estos valores deberían pasarse como parámetros
from sqlalchemy.orm import Session
#aqui estaba la inicializacion
import json
from typing import List
from pydantic import BaseModel, constr
from fastapi.encoders import jsonable_encoder
class UsuarioServicioTrabajadorBase(BaseModel):
    usuario_id: int
    servicio_trabajador_id: int
    
class ServicioTrabajadorBase(BaseModel):
    servicio_id: int
    trabajador_id: int
    precioxhora: int

class TrabajadorBase(BaseModel):
    nombre: str
    dni: str
    correoElec: str
    direccion: str
    localidad: str
    wsapp: str
    foto: str
    penales: str

class UsuarioBase(BaseModel):
    nombre: str
    dni: str
    correoElec: str
    direccion: str
    localidad: str
    wsapp: str
  
class Config:
        orm_mode = True

class ServicioBase(BaseModel):
    #id: int
    titulo: str
    
class Config:
        orm_mode = True

class ServicioSchema(ServicioBase):
    trabajadores: List[TrabajadorBase]

class TrabajadorSchema(TrabajadorBase):
    servicios: List[ServicioBase]
#####################################

class ServicioTrabajadorSchema(ServicioTrabajadorBase):
    serviciostrabajadores: List[ServicioTrabajadorBase]
#####################################
def get_session():
    with Session(engine) as session:
        yield session
#####################################
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()
# Ruta absoluta a la carpeta de fotos
app.mount("/static", StaticFiles(directory="fotos"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
###
@app.post("/registro Usuarios/", status_code=status.HTTP_201_CREATED)
async def crear_registro_Usuario(registro:UsuarioBase, db:db_dependency):
    db_registro = Usuario(**registro.dict())
    db.add(db_registro)
    db.commit()
    return "El Alta del Usuario se realizó exitosamente"

### ahora la tabla asociativa con Usuarios
@app.post("/Relacionar Usuarios con Trabajador - Servicio /", status_code=status.HTTP_201_CREATED)
async def crear_Relacion_Usuario_Trabajador_Servicio(registro:UsuarioServicioTrabajadorBase, db:db_dependency):
    db_registro = Usuarios_Servicios_Trabajadores(**registro.dict())
    
    db.add(db_registro)
    db.commit()
    return "El Alta del Usuario / Trabajador - Servicio / Relacionado se realizó exitosamente"

##28 / 3
@app.post("/registro/", status_code=status.HTTP_201_CREATED)
async def crear_registro_Trabajador(registro:TrabajadorBase, db:db_dependency):
    db_registro = Trabajador(**registro.dict())
    db.add(db_registro)
    db.commit()
    return "El Alta del Trabajador se realizó exitosamente"

@app.post("/registro Servicio/", status_code=status.HTTP_201_CREATED)
async def crear_registro_Servicio(registro:ServicioBase, db:db_dependency):
    db_registro = Servicio(**registro.dict())
    db.add(db_registro)
    db.commit()
    return "El Alta del Servicio se realizó exitosamente"

### ahora la tabla asociativa
@app.post("/Relacionar_Trabajador_Servicio /", status_code=status.HTTP_201_CREATED)
async def crear_Relacion_Trabajador_Servicio(registro:ServicioTrabajadorBase, db:db_dependency):
    db_registro = Servicios_Trabajadores(**registro.dict())
    db_registro.id = int(str(db_registro.servicio_id) + str(db_registro.trabajador_id))
    db.add(db_registro)
    db.commit()
    return "El Alta del Trabajador - Servicio / Relacionado se realizó exitosamente"
##################################################
### borro registro Servicio

@app.delete("/Borro registro Servicio")
async def delete_servicio(servicioid: int, db: Session = Depends(get_db)):
    usersr = db.query(Servicio).get({"id": servicioid})
    #elimino la fila que es unica. Con el get solucioné el problema de selección multiple filas con datos: 10,3, 10,4
    if not usersr:  
        return("No existe ese Servicio")
    db.delete(usersr)
    db.commit()
    return(usersr)
 
##############################################
### ahora borro registro Trabajador

@app.delete("/Borro registro Trabajador")
async def delete_trabajador(trabajadorid: int, db: Session = Depends(get_db)):
    usertr = db.query(Trabajador).get({"id": trabajadorid})
    #elimino la fila que es unica. Con el get solucioné el problema de selección multiple filas con datos: 10,3, 10,4
    if not usertr:  
        return("No existe ese Trabajador")
    db.delete(usertr)
    db.commit()
    return(usertr)
 
##############################################
### ahora borro registro de la tabla asociativa
# Mucho laburo
@app.delete("/Borro registro Relación Trabajador Servicio")
async def delete_Relacion_trabajador_servicio(servicioid: int, trabajadorid: int, db: Session = Depends(get_db)):
    usersi = db.query(Servicios_Trabajadores).get({"id":int(str(servicioid)+str(trabajadorid)),"servicio_id": servicioid, "trabajador_id": trabajadorid})
    #falta eliminarlo por método Manu
    #elimino la fila que es unica. Con el get solucioné el problema de selección multiple filas con datos: 10,3, 10,4
    if not usersi:  
        return("No existe ese Servicio con ese Trabajador")
    db.delete(usersi)
    db.commit()
    return(usersi)
 
#############################################

@app.get("/Obtengo_registro_Relación_Trabajador_Servicio")
async def Busco_Relacion_trabajador_servicio(servicioid: int, trabajadorid: int, db: Session = Depends(get_db)):
    usersi = db.query(Servicios_Trabajadores).get({"id":int(str(servicioid)+str(trabajadorid)),"servicio_id": servicioid, "trabajador_id": trabajadorid})
    #falta eliminarlo por método Manu
    #elimino la fila que es unica. Con el get solucioné el problema de selección multiple filas con datos: 10,3, 10,4
    if not usersi:  
        return("No existe ese Servicio con ese Trabajador")
    db_serviciostrabajadoresId = db.query(Servicios_Trabajadores.id).all() 
    db_serviciostrabajadores = db.query(Servicios_Trabajadores.servicio_id).all() 
    db_serviciostrabajadores1 = db.query(Servicios_Trabajadores.trabajador_id).all() 
    db_serviciostrabajadores2 = db.query(Servicios_Trabajadores.precioxhora).all() 
    db_serviciostrabajadores3 = db.query(Servicio.titulo).all() 
    tit = [row[0] for row in db_serviciostrabajadores3] 

   
    db_servicios =  db.query(Servicio.id).all() 
    tas = [row[0] for row in db_servicios]  

    db_trabajadores = db.query(Trabajador.id).all()
    db_trabajadoresname = db.query(Trabajador.nombre).all()
    tat = [row[0] for row in db_trabajadoresname]

    tags = [row[0] for row in db_serviciostrabajadores]  
    tags1 = [row[0] for row in db_serviciostrabajadores1]  
    pxh =   [row[0] for row in db_serviciostrabajadores2] 
    clave =  [row[0] for row in db_serviciostrabajadoresId] 


#+ Recorro la tabla servicios_trabajadores y listo sus contenidos en users. Esto lo hago de 1 sola vez en lugar de hacer multiples querys

    users=''
    for i in range(0, len(tags1)):
        #Manu
        users = users +  str(clave[i]) + ' '+str(db.query(Servicio).get({"id": tags[i]}).id) + '-' + db.query(Servicio).get({"id": tags[i]}).titulo +' ============> '+str(db.query(Trabajador).get({"id": tags1[i]}).id) + '-' + db.query(Trabajador).get({"id": tags1[i]}).nombre  + " Precio por Hora $ " + str(pxh[i]) + '---'
        ##users = users +  str(clave[i]) + ' '+str([ s.id for s in db_servicios if s.id == tags[i]]) + '-' + str([ tit[s.id-1] for s in db_servicios if s.id == tags[i]])  +' ============> '+str([ s.id for s in db_trabajadores if s.id == tags1[i]]) + '-' + str([ tat[s.id-1] for s in db_trabajadores if s.id == tags1[i]])  + " Precio por Hora $ " + str(pxh[i]) + '---'
    users = users.split(sep='---', maxsplit=-1)
    #return {'Servicios': tags, 'Trabajadores': tags1,  'Nombres de Servicios': tangarr, 'Nombres de Trabajadores': cgtarr,'Clave - Nombre de Trabajador y Clave - Servicio': users}
    #return {'Claves - Nombre de Trabajador y Servicio Ofrecido por él': users}
    return usersi
#############################################


##########

@app.get("/Listo_registros_Profesion_Trabajador_Servicio/{param}")
async def Listo_Profesion_trabajador_servicio(param: str, db: Session = Depends(get_db)):

    # Cuento los registros de servicios_trabajadores existentes
    db_profes = db.query(Servicios_Trabajadores).join(Servicio).join(Trabajador).filter(Servicio.titulo == param).count() 
    # Selecciono las columnas a listar: Joint de las 3 tablas de 
    db_stmt = select(Servicios_Trabajadores.id, Servicio.titulo, Trabajador.nombre,Trabajador.wsapp,Trabajador.foto, Trabajador.penales).select_from (Servicios_Trabajadores).join (Servicio).join(Trabajador).where(Servicio.titulo == param and Servicio.id == Servicios_Trabajadores.servicio_id and Servicios_Trabajadores.trabajador_id == Trabajador.id) 
    
    # ejecuto la consulta
    result = db.execute(db_stmt)
    # asigno los valores a los 4 campos seleccionados
    id =  [row[0] for row in result]

    result = db.execute(db_stmt)
    servicio =  [row[1] for row in result]

    result = db.execute(db_stmt)
    nombre =  [row[2] for row in result]

    result = db.execute(db_stmt)
    wsapp =  [row[3] for row in result]

# agregado foto y penales
    result = db.execute(db_stmt)
    foto =  [row[4] for row in result]

    result = db.execute(db_stmt)
    penales =  [row[5] for row in result]

    
    a=[]
    #b=''
    #genero tantos strings al front como registros existen de servicios_trabajadores
    for i in range(0, db_profes):
        a = a +[servicio[i]]+[nombre[i]]+['---']+[wsapp[i]]+['./'+foto[i]]+[penales[i]]
        #a = a +[servicio[i]]+[nombre[i]]+['---']+['*****']+['./'+foto[i]]

        #a = a +str(id[i])+' '+str(servicio[i])+' '+str(nombre[i])+' ' + ' $'+str(costo[i])+' ' +str(foto[i])+'---'
        w = wsapp[i]
        #b= b +str(foto[i])
    #a = a.split(sep='---', maxsplit=-1)
    #b = b.split(sep='---', maxsplit=-1)

    #a.pop() 
    #'./claudio.jpeg'
    
    return {'RegLog': a, 'Ws':w }
    #return {'RegLog': a }

#############################################

@app.get("/Trabajador_Servicios_Relacionados")
async def get_Relacion_Trabajador_Servicios(db: Session = Depends(get_db)):
    db_serviciostrabajadoresId = db.query(Servicios_Trabajadores.id).all() 
    db_serviciostrabajadores = db.query(Servicios_Trabajadores.servicio_id).all() 
    db_serviciostrabajadores1 = db.query(Servicios_Trabajadores.trabajador_id).all() 
    db_serviciostrabajadores2 = db.query(Servicios_Trabajadores.precioxhora).all() 
    db_serviciostrabajadores3 = db.query(Servicio.titulo).all() 
    tit = [row[0] for row in db_serviciostrabajadores3] 

   
    db_servicios =  db.query(Servicio.id).all() 
    tas = [row[0] for row in db_servicios]  

    db_trabajadores = db.query(Trabajador.id).all()
    db_trabajadoresname = db.query(Trabajador.nombre).all()
    tat = [row[0] for row in db_trabajadoresname]

    tags = [row[0] for row in db_serviciostrabajadores]  
    tags1 = [row[0] for row in db_serviciostrabajadores1]  
    pxh =   [row[0] for row in db_serviciostrabajadores2] 
    clave =  [row[0] for row in db_serviciostrabajadoresId] 

    
#+ Recorro la tabla servicios_trabajadores y listo sus contenidos en users. Esto lo hago de 1 sola vez en lugar de hacer multiples querys

    users=''
    for i in range(0, len(tags1)):
        #Manu
        #users = users +  "Iden: " + str(clave[i]) + ' '+str(db.query(Servicio).get({"id": tags[i]}).id) + '-' + db.query(Servicio).get({"id": tags[i]}).titulo +' ============> '+str(db.query(Trabajador).get({"id": tags1[i]}).id) + '-' + db.query(Trabajador).get({"id": tags1[i]}).nombre  + " Precio por Hora $ " + str(pxh[i]) + '---'
        users = users +  str(clave[i]) + ' '+str([ s.id for s in db_servicios if s.id == tags[i]]) + '-' + str([ tit[s.id-1] for s in db_servicios if s.id == tags[i]])  +' ============> '+str([ s.id for s in db_trabajadores if s.id == tags1[i]]) + '-' + str([ tat[s.id-1] for s in db_trabajadores if s.id == tags1[i]])  + " Precio por Hora $ " + str(pxh[i]) + '---'
    users = users.split(sep='---', maxsplit=-1)
    #return {'Servicios': tags, 'Trabajadores': tags1,  'Nombres de Servicios': tangarr, 'Nombres de Trabajadores': cgtarr,'Clave - Nombre de Trabajador y Clave - Servicio': users}
    #return {'Claves - Nombre de Trabajador y Servicio Ofrecido por él': users}
    return users
#############################################
@app.get("/Usuarios_Trabajadores_Servicios_Relacionados")
async def get_Relacion_Usuario_Trabajador_Servicios(db: Session = Depends(get_db)):
    db_servicios =  db.query(Servicio.id).all() 
    db_serviciostrabajadores = db.query(Servicios_Trabajadores).all()
    db_servtrab = db.query(Servicios_Trabajadores.servicio_id).all() 
    db_usuarisserviciostrabajadores = db.query(Usuarios_Servicios_Trabajadores.servicio_trabajador_id).all() 
    db_ususertra = db.query(Usuarios_Servicios_Trabajadores.usuario_id).all() 
    cla  = [row[0] for row in db_ususertra]
    db_ust = db.query(Usuarios_Servicios_Trabajadores.servicio_trabajador_id).all() 
    clo  = [row[0] for row in db_ust]
    db_usuarios = db.query(Usuarios_Servicios_Trabajadores.usuario_id).all() 
    #determino los contratos
    claves = [row[0] for row in db_usuarisserviciostrabajadores]
    
    # determino los usuarios con contrato
    usus = [row[0] for row in db_usuarios]
    tags = [row[0] for row in db_servtrab] 
    db_serviciostrabajadores3 = db.query(Servicio.titulo).all() 
    tit = [row[0] for row in db_serviciostrabajadores3] 
    db_trabajadoresname = db.query(Trabajador.nombre).all()
    
    tat = [row[0] for row in db_trabajadoresname]
    db_serviciostrabajadores2 = db.query(Servicios_Trabajadores.precioxhora).all() 
    pxh =   [row[0] for row in db_serviciostrabajadores2]
    db_usuarioname = db.query(Usuario.nombre).all()
    nom = [row[0] for row in db_usuarioname] 
    # Manu userst=list(range(len(usus)))
    userst=list(range(len(usus)))
    users=''
    
    for i in range(0, len(usus)):
        users = users +str(set([s.usuario_id  for s in db_ususertra if cla[i] == s.usuario_id])) + str(set([nom[s.usuario_id-1]  for s in db_ususertra if cla[i] == s.usuario_id]))  + '----------->' + str(set([s.servicio_trabajador_id  for s in db_ust if clo[i] == s.servicio_trabajador_id])) + str([ tit[s.servicio_id-1]  for s in db_serviciostrabajadores if claves[i] == s.id]) + str([ tat[s.trabajador_id-1]  for s in db_serviciostrabajadores if claves[i] == s.id])  + " Precio por Hora $ " + str([ pxh[s.trabajador_id-1]  for s in db_serviciostrabajadores if claves[i] == s.id]) + '///'
    users = users.split(sep='///', maxsplit=-1)
        #users = users + str([ tit[t.id-1] for t in db_servicios if t.id == tags[j]]) 
           
           # Manu
           # Manu userst[i] = [ s for s in db_serviciostrabajadores if s.id == claves[i]]
           # Mejoro lo de Manu
           
  
           #userst[i] = db_serviciostrabajadores.filter(id == claves[i])
           #userst[i] = db.query(Servicios_Trabajadores).where (Servicios_Trabajadores.id == claves[i]).all()  
           #cadena=cadena + str(userst[i].values())
    # Manu return {'Usuarios': usus,  'Contratos': userst}
    #return {'Usuarios': usus,  'Contratos': users}
    ##return {'Usuario contrató a: -----------> ':users}
    return users

    #return {'Usuarios': usus,  'Contratos': cadena}
    #return {'Claves': len(claves)}
  
####################################################
@app.get("/Servicios")
async def Servicios(db: Session = Depends(get_db)):

    # Cuento los registros de servicios_trabajadores existentes
    db_servicios = db.query(Servicio.id).all()
    tags = [row[0] for row in db_servicios] 
    # Selecciono las columnas a listar: Joint de las 3 tablas de 
    db_stmt = select(Servicio.titulo).select_from (Servicio) 
    
    # ejecuto la consulta
    result = db.execute(db_stmt)
    # asigno los valores a los 4 campos seleccionados
    servicio =  [row[0] for row in result]

    a=''
    #genero tantos strings al front como registros existen de servicios_trabajadores
    for i in range(0, len(tags)):
        a = a +str(servicio[i])+'---'
    a = a.split(sep='---', maxsplit=-1)
    a.pop()
    return {'RegLog': a }
####################################################

@app.get("/Servicios/{id}", response_model=ServicioSchema)
async def get_servicio(id: int, db: Session = Depends(get_db)):
    db_servicio = db.query(Servicio).options(joinedload(Servicio.trabajadores)).\
        where(Servicio.id == id).one()
    return db_servicio


@app.get("/Trabajadores/{id}", response_model=TrabajadorSchema)
async def get_trabajador(id: int, db: Session = Depends(get_db)):
    db_trabajador = db.query(Trabajador).options(joinedload(Trabajador.servicios)).\
        where(Trabajador.id == id).one()
    return db_trabajador


@app.get("/Trabajadores")
async def get_trabajadores(db: Session = Depends(get_db)):
    db_trabajadores = db.query(Trabajador.id).all()
    #db_authors = db.query(Author).options(joinedload(Author.books)).all()
    tags1 = [row[0] for row in db_trabajadores] 
    db_trabajadoresname = db.query(Trabajador.nombre).all()
    tat = [row[0] for row in db_trabajadoresname]
    #Ahora busco los trabajadores
    mi_lista = []
    users=''
    for i in range(0, len(tags1)):
       
       #users = users + str(db.query(Trabajador).get({"id": tags[i]}).id) + ' ' + db.query(Trabajador).get({"id": tags[i]}).nombre + '---'
       users = users +str([ s.id for s in db_trabajadores if s.id == tags1[i]]) + '-' + str([ tat[s.id-1] for s in db_trabajadores if s.id == tags1[i]]) + '---'
    users = users.split(sep='---', maxsplit=-1)
    #return {'Clave y Nombrs de Trabajador': users}
    return users

@app.get("/Usuarios")
async def get_usuarios(db: Session = Depends(get_db)):
    db_usuarios = db.query(Usuario.id).all()
    #db_authors = db.query(Author).options(joinedload(Author.books)).all()
    tags1 = [row[0] for row in db_usuarios] 
    db_usuariosname = db.query(Usuario.nombre).all()
    tat = [row[0] for row in db_usuariosname]
    #Ahora busco los trabajadores
    mi_lista = []
    users=''
    for i in range(0, len(tags1)):
       
       #users = users + str(db.query(Trabajador).get({"id": tags[i]}).id) + ' ' + db.query(Trabajador).get({"id": tags[i]}).nombre + '---'
       users = users +str([ s.id for s in db_usuarios if s.id == tags1[i]]) + '-' + str([ tat[s.id-1] for s in db_usuarios if s.id == tags1[i]]) + '---'
    users = users.split(sep='---', maxsplit=-1)
    return {'Clave y Nombre de Usuario': users}

@app.get("/Usuarios/{id}")
async def get_usuario(id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).\
        where(Usuario.id == id).one()
    return db_usuario

#### Actualización
@app.patch("/trabajadores/{trabajador_id}", response_model=TrabajadorPublic)
def update_trabajador(
    *,
    session: Session = Depends(get_session),
    trabajador_id: int,
    trabajador: TrabajadorUpdate,
):
    db_trabajador = session.get(Trabajador, trabajador_id)
    if not db_trabajador:
        raise HTTPException(status_code=404, detail="Trabajador not found")
    trabajador_data = trabajador.model_dump(exclude_unset=True)
    for key, value in trabajador_data.items():
        setattr(db_trabajador, key, value)
    session.add(db_trabajador)
    session.commit()
    session.refresh(db_trabajador)
    return db_trabajador

@app.patch("/Actualizo registro precio x hora en Tabla Asociativa")
def update_servicio_trabajador(
    *, 
    session: Session = Depends(get_session),
    servicioid: int, trabajadorid: int, 
    serviciotrabajador: Servicios_TrabajadoresUpdate,
):

    db_servicio_trabajador = session.query(Servicios_Trabajadores).get({"servicio_id": servicioid, "trabajador_id": trabajadorid})
    
    if not db_servicio_trabajador:  
        return("No existe ese Servicio con ese Trabajador")
    
    servicio_trabajador_data = serviciotrabajador.model_dump(exclude_unset=True)
    for key, value in servicio_trabajador_data.items():
        setattr(db_servicio_trabajador, key, value)
    session.add(db_servicio_trabajador)
    session.commit()
    session.refresh(db_servicio_trabajador)
    return db_servicio_trabajador
    
    #db.delete(usersi)
    #db.commit()
    #return(usersi)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
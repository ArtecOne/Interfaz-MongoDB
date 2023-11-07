import json
import motor.motor_asyncio as ms

# mongodb+srv://jimenezjavieret2121:Loquendo1252@cluster0.2stzbkr.mongodb.net/?retryWrites=true&w=majority

cliente = ms
database = ""
coleccion = ""


def set_db(string):
    global database
    database = string

def set_collection(string):
    global coleccion
    coleccion = string
    
def get_db():
    global database
    return database

async def conectar(uri):
    global cliente
    if not 'mongodb' in uri:
        return False
    
    try:
        cliente = cliente.AsyncIOMotorClient(uri)
    except:
        return False
    
    return True

async def mostrar_databases():
    global cliente
    nombres : list = await cliente.list_database_names()
    nombres.remove("admin") or nombres.remove("local")
    return nombres

async def mostrar_colecciones(db):
    global cliente
    lista : list = await cliente.get_database(db).list_collection_names()
    return lista

async def insertar(string):
    global cliente , database , coleccion
    
    docu = json.loads(string)
    
    await cliente[database][coleccion].insert_one(docu)
    
    return True

async def insert_app(string):
    return await insertar(string)
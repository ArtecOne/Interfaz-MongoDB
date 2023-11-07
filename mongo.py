import json
import motor.motor_asyncio as ms



cliente = ms

async def conectar(uri):
    global cliente
    
    if 'mongodb' in uri:
        cliente = cliente.AsyncIOMotorClient(uri)
        return True
    else:
        return False

async def insertar(string):
    global cliente
    
    docu = json.loads(string)
    
    db = cliente.Clase

    collection = db.Alumnos
    
    await collection.insert_one(docu)
    
    return True

async def insert_app(string):
    return await insertar(string)
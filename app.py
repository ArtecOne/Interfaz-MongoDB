import motor.motor_asyncio
import asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://javierjimenez:Loquendo1252@cluster0.2stzbkr.mongodb.net/?retryWrites=true&w=majority")

db = client.Clase

collection = db.Alumnos

async def insertar():
    document = {
        "name" : "Luis",
        "edad" : 17,
        "mesa" : 2
    }
    
    await collection.insert_one(document)
    
loop = client.get_io_loop()
loop.run_until_complete(insertar())
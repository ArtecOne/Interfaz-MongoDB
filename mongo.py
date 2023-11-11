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
    if not "mongo" in uri:
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

async def insert_app(string : str):
    global cliente , database , coleccion
    
    try:
        docu = json.loads(string.strip())
        await cliente[database][coleccion].insert_one(docu)
    except:
        return False
    
    return True

async def search_app(doc):
    global cliente , database, coleccion
    if not doc:
        return "t"
    
    documentos = []
    
    try:
        docu = json.loads(doc)
        async for docu in cliente[database][coleccion].find(docu):
            docu.pop("_id")
            documentos.append(docu)         
    except Exception as exc:
        return False
    
    return documentos

async def delete_app(doc):
    global cliente , database, coleccion
        
    try:
        docu = json.loads(doc)
        result = await cliente[database][coleccion].delete_many(docu)
    except:
        return False
        
    return result.deleted_count
            
    
async def update_app(query , docu , modo : str):
    global cliente , database , coleccion
    #modo u for update
    #modo r for replace
    if not(query and docu) or query == '{}' or docu == '{}':
        return False
    
    match modo:
        case "u":
            try:
                await delete_app(query)
                
                q : dict = json.loads(query)
                d : dict = json.loads(docu)
                
                q.update(d)
                
                print(q)
                
                await cliente[database][coleccion].insert_one(q)
            except:
                return False
        case "r":
            try:
                q : dict = json.loads(query)
                d : dict = json.loads(docu)

                await cliente[database][coleccion].replace_one(q , d)
            except:
                return False
        
    return True
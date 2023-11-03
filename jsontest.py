import json
import os
import asyncio
def crear_jjson(string_a):
    if os.path.exists("./json.data.json"):
        os.remove("json.data.json")
    
    async def crear_json(string_b):
            y = json.loads(string_b)
            with open(f"json.data.json" , "+a", encoding="utf-8") as file:
                await json.dump(y, file , ensure_ascii=False)

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(loop.create_task(crear_json(string_a)))
    except TypeError:
        loop.close()
        return True
    except json.JSONDecodeError:
        loop.close
        return False

#crear_json(x)
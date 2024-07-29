from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import dotenv_values

def conexion():
    config = dotenv_values(".env")
    uri = config.get('ATLAS_URI')
    client = MongoClient(uri, server_api=ServerApi('1'))
    database = client[config.get('DB_NAME')]
    return database[config.get('COLLECTION')]


def exportar_datos(datos:[]):
    collection = conexion()
    result = collection.insert_many(datos)
    print(f"Imagenes exportadas con exito. Total: {len(result)}")

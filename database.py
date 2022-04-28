from pymongo import MongoClient
import pymongo
import os
import certifi

if 'database_url' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()
    CONNECTION_STRING = os.environ.get('database_url')
else:
    CONNECTION_STRING = os.environ['database_url']
    
DBNAME = 'pikup'
DRIVERS_COLLECTION = 'drivers'
USERS_COLLECTION = 'users'
JOBS_COLLECTION = 'jobs'

# ------------------------------------------------------------------- #
# General Database methods

def getDatabase():
    client = pymongo.MongoClient(CONNECTION_STRING, tlsCAFile = certifi.where())
    return client[DBNAME]

def getCollection(collection):
    try:
        dbname = getDatabase()
        return dbname[collection]
    except Exception as e:
        print(str(e))
        return None

def insertOne(collection, insertDict):
  try:
    collection_name = getCollection(collection)
    result = collection_name.insert_one(insertDict)
    return result.inserted_id
  except Exception as e:
    print(str(e))
    return None

def getAll(collection, sort_by=None):
    try:
        collection_name = getCollection(collection)
        if sort_by:
          return collection_name.find(sort=[(sort_by, pymongo.ASCENDING)])
        else:
          return collection_name.find()
          
    except Exception as e:
        print(str(e))
        return None

def getOne(collection, key, val):
    try:
        collection = getCollection(collection)
        return collection.find_one({key : val})
          
    except Exception as e:
        print(str(e))
        return None
  

# ------------------------------------------------------------------- #

if __name__ == "__main__":

  testDict = {
    '_id' : 0,
    'first' : 'Peter',
    'last' : 'Skinner'
  }

  insertOne('users', testDict)


  
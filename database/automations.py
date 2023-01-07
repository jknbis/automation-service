from pymongo import MongoClient
import pandas as pd
import numpy as np
import pandas_ta as ta


# Connect to MongoDB
MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = 27017
LIST_OF_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
TIME_FRAMES_CONVERSION = ['5T', '15T', '30T',
                          '60T', '120T', '240T', '480T', '1D']
MONGO_CLIENT = MongoClient(MONGO_DB_HOST, MONGO_DB_PORT)
BOTS_DATABASE = MONGO_CLIENT.test
bots_collection = BOTS_DATABASE.get_collection('automations')
users_collection = BOTS_DATABASE.get_collection('users')

#function that get user api key and api secret form db
def get_user_api_key_secret(user_id):
    #from exhchangeAcoounts array find the user by account_id
    user = users_collection.find({"exchangeAccounts": {"$elemMatch": {"accountId": user_id}}})
     #create dictionary called response_dict
    response_dict = {
        "api_key": user[0]['exchangeAccounts'][0]['apiKey'],
        "api_secret": user[0]['exchangeAccounts'][0]['apiSecret'],
    }
    return response_dict


#Check the Database  only for 1m minute candles
def check_database(tf,symbol):
    if tf=="1T":
        db = MONGO_CLIENT['coins']
    else:
        db = MONGO_CLIENT[symbol+"USDT"]
    return db


#Check Collection name
def check_collection(tf,db,symbol):
    if tf=="1T":
        collection=db[symbol+"USDT"]
    else:
        collection = db[symbol+"USDT"+"_"+tf]
    return collection

#Check time frame
def check_tm(tf):
    if(tf=='1m'):
        tf='1T'
    elif(tf=='5m'):
        tf='5T'
    elif(tf=='15m'):
        tf='15T'
    elif(tf=='30m'):
        tf='30T'
    elif(tf=='1h'):
        tf='60T'
    elif(tf=='2h'):
        tf='120T'
    elif(tf=='4h'):
        tf='240T'
    elif(tf=='8h'):
        tf='480T'
    elif(tf=='1d'):
        tf='1D'
    return tf


# functiono that get candles according to timeframe
def get_candles(tf, symbol):
    tf=check_tm(tf)
    db=check_database(tf,symbol)
    collection=check_collection(tf,db,symbol)
    candles = collection.find({}).sort("timestamp", 1)
    return candles

#saving the event after it done
def save_event(bot_id,event_id,eventsArr):
    #update field fineshed in the eventsArr of bot obj
    for e in eventsArr:
        if e['eventId']==event_id:
            e['finished']=True
    bots_collection.find_one_and_update({'_id': bot_id}, {'$set': {'eventsArr': eventsArr}})
    

def update_status(bot_id, status):
    bots_collection.find_one_and_update({'_id': bot_id}, {'$set': {'status': status}})
    

#saving the action after it done
def save_action(bot_id,action,actionsArr):
    #update field finneshed in the eventsArr of bot obj
    for e in actionsArr:
        if e['actionId']==action:
            e['finished']=True
    bots_collection.find_one_and_update({'_id': bot_id}, {'$set': {'actionsArr': actionsArr}})

#getting the last candle 
def get_last_candle(tf, symbol):
    tf=check_tm(tf)
    db=check_database(tf,symbol)
    collection=check_collection(tf,db,symbol)
    last_candle = collection.find_one(sort=[("timestamp", -1)])
    return last_candle
  
#get bot by id
def retrieve_bot_by_id(id: str) -> dict:
    bot = bots_collection.find_one({"id": id})
    obj = {
        "id": str(bot['id']),
        "name": bot['name'],
        "usdt_balace": bot['usdt_balace'],
        "conditions": bot['conditions']
    }
    if bot:
        return obj

#get all the automations
def retrieve_all_automations() -> list:
    bots = bots_collection.find({})
    return bots

#get bots by user_id
#futture implemention
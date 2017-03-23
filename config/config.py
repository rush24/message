#!/usr/bin/env python
# coding: utf-8
from pymongo import MongoClient
from redis import ConnectionPool
from redis import Redis

settings = {
    "mongo": {
        "host": "mongodb://localhost/message",
        "port": 27017,
    },
    "OAUTH": {
        "session_key": "access_token",
    },
    "redis": {
        "host": "localhost",
        "port": 6379
    }

}


def redis_client():
    host, port = settings["redis"]["host"], settings["redis"]["port"]
    db = 0
    pool = ConnectionPool(host=host, port=port, db=db, max_connections=50)
    return Redis(connection_pool=pool)


redis_client = redis_client()


def mongo_client():
    return MongoClient(**settings["mongo"]).get_default_database()


mongo_client = mongo_client()

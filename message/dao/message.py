#!/usr/bin/env python
# coding: utf-8
import copy

from bson import ObjectId

from config.config import mongo_client


messages_col = mongo_client.messages


def mongo_id_to_str(obj):
    new_obj = copy.deepcopy(obj)
    id = new_obj.pop("_id")
    new_obj["id"] = str(id)
    return new_obj


class MessagesDao(object):

    @classmethod
    def save_message(cls, message):
        messages_col.insert_one(message)
        message["id"] = str(message['_id'])
        message.pop("_id")

    @classmethod
    def find(cls, query=None, sort_field='create_at', sort_direction=-1, limit=10):
        messages = messages_col.find(query).sort(sort_field, sort_direction).limit(limit)
        messages = [mongo_id_to_str(message) for message in messages]
        return messages

    @classmethod
    def delete(cls, id):
        messages_col.remove({"_id": ObjectId(id)})

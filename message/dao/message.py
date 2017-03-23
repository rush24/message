#!/usr/bin/env python
# coding: utf-8

from config.config import mongo_client


messages_col = mongo_client.messages


def hide_mongo_id(obj):
    if not obj:
        return obj
    if '_id' in obj:
        del obj['_id']
    return obj


class MessagesDao(object):

    @classmethod
    def save_message(cls, message):
        return messages_col.insert_one(message)

    @classmethod
    def find(cls, query=None, sort_field='create_at', sort_direction=-1, limit=10):
        messages = messages_col.find(query).sort(sort_field, sort_direction).limit(limit)
        messages = [hide_mongo_id(message) for message in messages]
        return messages
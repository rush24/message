#!/usr/bin/env python
# coding: utf-8
from config.config import mongo_client


user_col = mongo_client.users


class UserDao(object):

    @classmethod
    def find_user(cls, query=None):
        return user_col.find_one(query)

    @classmethod
    def save_user(cls, user):
        return user_col.insert_one(user)

    @classmethod
    def update_user(cls, user):
        return user_col.update_one(
            {"user_name": user['user_name']},
            {"$set": user}
        )
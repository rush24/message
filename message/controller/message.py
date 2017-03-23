#!/usr/bin/env python
# coding: utf-8
import time
import tornado.escape

from ..dao.message import MessagesDao
from ..dao.user import UserDao


class MessageHandler(object):

    @classmethod
    def handle(cls, user_name, message):
        message = tornado.escape.json_decode(message)
        type = message.get("type")
        if type == "get_friends":
            return MessageHandler.get_friends(user_name, message)
        elif type == "get_messages":
            return MessageHandler.get_messages(user_name, message)
        elif type == "send_message":
            return MessageHandler.send_message(user_name, message)
        elif type == "read_message":
            return MessageHandler.read_message(user_name, message)
        else:
            pass

    @classmethod
    def get_friends(cls, user_name, message):
        user = UserDao.find_user({"user_name": user_name})
        message = {
            "friends": user.get("friends"),
        }
        return user_name, message

    @classmethod
    def get_messages(cls, user_name, message):
        friend_name = str(message.get("friend_name"))
        max_ts = message.get("max_ts", 0)
        min_ts = message.get("min_ts", 0)
        size = message.get("size", 10)

        query = {
            "$or": [
                {
                    "from_user": friend_name,
                    "to_user": user_name
                },
                {
                    "from_user": user_name,
                    "to_user": friend_name
                }
            ],
            "create_at": {"$gt": int(min_ts)}
        }
        if max_ts:
            query.update({
                "create_at": {"$lt": int(max_ts)}
            })
        messages = MessagesDao.find(query, limit=size)
        message = {
            "messages": messages,
            "friend_name": friend_name
        }

        user = UserDao.find_user({"user_name": user_name})
        for friend_detail in user.get("friends"):
            if friend_detail.get("user_name") == friend_name:
                friend_detail["unread_count"] = 0
        UserDao.update_user(user)

        return user_name, message

    @classmethod
    def send_message(cls, user_name, message):
        message = {
            "from_user": user_name,
            "to_user": message.get("friend_name"),
            "content": message.get("content"),
            "create_at": int(time.time()),
        }

        MessagesDao.save_message(message)

        find_friend = False
        user = UserDao.find_user({"user_name": user_name})
        to_user = UserDao.find_user({"user_name": message.get("to_user")})
        for friend_detail in user.get("friends"):
            if friend_detail.get("user_name") == message.get("to_user"):
                find_friend = True
        if not find_friend:
            user.get("friends").append({
                "user_name": message.get("to_user"),
                "unread_count": 0,
            })
            UserDao.update_user(user)
            to_user.get("friends").append({
                "user_name": user_name,
                "unread_count": 0,
            })

        for friend_detail in to_user.get("friends"):
            if friend_detail.get("user_name") == user_name:
                friend_detail["unread_count"] += 1
                friend_detail["last_message"] = message.get("content")
                friend_detail["last_time"] = message.get("create_at")
        print to_user
        UserDao.update_user(to_user)

        del message['_id']
        message['type'] = "message"

        return message.get("to_user"), message

    @classmethod
    def read_message(cls, user_name, message):
        user = UserDao.find_user({"user_name": user_name})
        for friend_detail in user.get("friends"):
            if friend_detail.get("user_name") == message.get("friend_name"):
                friend_detail["unread_count"] = 0
        UserDao.update_user(user)
        return None, None

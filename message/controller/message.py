#!/usr/bin/env python
# coding: utf-8
import time
import tornado.escape

from ..dao.message import MessagesDao
from ..dao.user import UserDao


class MessageHandler(object):

    @classmethod
    def handle(cls, user_name, message, socket_pool):
        message = tornado.escape.json_decode(message)
        type = message.get("type")
        if type == "get_friends":
            MessageHandler.get_friends(user_name, message, socket_pool)
        elif type == "get_messages":
            MessageHandler.get_messages(user_name, message, socket_pool)
        elif type == "send_message":
            MessageHandler.send_message(user_name, message, socket_pool)
        elif type == "read_message":
            MessageHandler.read_message(user_name, message, socket_pool)
        elif type == "delete_message":
            MessageHandler.delete_message(user_name, message, socket_pool)
        else:
            pass

    @classmethod
    def get_friends(cls, user_name, message, socket_pool):
        user = UserDao.find_user({"user_name": user_name})
        message = {
            "type": message.get("type"),
            "friends": user.get("friends"),
        }

        to = socket_pool.get(user_name, None)
        if to:
            to.write_message(message)

    @classmethod
    def get_messages(cls, user_name, message, socket_pool):
        type = message.get("type")
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
        messages = MessagesDao.find(query, limit=int(size))
        message = {
            "type": type,
            "messages": messages,
            "friend_name": friend_name
        }

        user = UserDao.find_user({"user_name": user_name})
        for friend_detail in user.get("friends"):
            if friend_detail.get("user_name") == friend_name:
                friend_detail["unread_count"] = 0
        UserDao.update_user(user)

        to = socket_pool.get(user_name, None)
        if to:
            to.write_message(message)

    @classmethod
    def send_message(cls, user_name, message, socket_pool):
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
        UserDao.update_user(to_user)

        message['type'] = "message"

        to = socket_pool.get(message.get("to_user"), None)
        if to:
            to.write_message(message)
            to.write_message({
                "type": "get_friends",
                "friends": to_user.get("friends"),
            })

        # 再回发给消息发起者做回显，再将 from_user 处理是为了发起者能实时接收这条消息
        message['from_user'] = message['to_user']
        to = socket_pool.get(user_name, None)
        if to:
            to.write_message(message)

    @classmethod
    def read_message(cls, user_name, message, socket_pool):
        user = UserDao.find_user({"user_name": user_name})
        for friend_detail in user.get("friends"):
            if friend_detail.get("user_name") == message.get("friend_name"):
                friend_detail["unread_count"] = 0
        UserDao.update_user(user)

    @classmethod
    def delete_message(cls, user_name, message, socket_pool):
        MessagesDao.delete(message.get("id"))

        to_user = UserDao.find_user({"user_name": message.get("friend_name")})
        has_modified = False
        for friend_detail in to_user.get("friends"):
            if friend_detail.get("user_name") == user_name:
                if friend_detail["unread_count"] > 0:
                    friend_detail["unread_count"] -= 1
                    has_modified = True
        if has_modified:
            UserDao.update_user(to_user)

        to = socket_pool.get(message.get("friend_name"), None)
        if to:
            to.write_message({
                "type": "delete_message",
                "from_user": user_name,
                "id": message.get("id")
            })

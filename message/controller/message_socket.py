#!/usr/bin/env python
# coding: utf-8

import tornado.websocket

from config.config import redis_client, settings
from message import MessageHandler


class MessageSocketHandler(tornado.websocket.WebSocketHandler):

    socket_pool = dict()

    def open(self):
        oauth_token = self.get_secure_cookie(settings["OAUTH"]["session_key"])
        user_name = redis_client.get(oauth_token)
        MessageSocketHandler.socket_pool[user_name] = self

    def on_close(self):
        oauth_token = self.get_secure_cookie(settings["OAUTH"]["session_key"])
        user_name = redis_client.get(oauth_token)
        del MessageSocketHandler.socket_pool[user_name]

    def on_message(self, message):
        oauth_token = self.get_secure_cookie(settings["OAUTH"]["session_key"])
        user_name = redis_client.get(oauth_token)
        MessageHandler.handle(user_name, message, MessageSocketHandler.socket_pool)

    def check_origin(self, origin):
        return True

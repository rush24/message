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
        to_user, message = MessageHandler.handle(user_name, message)
        to = MessageSocketHandler.socket_pool.get(to_user, None) if to_user else None
        if to:
            to.write_message(message)

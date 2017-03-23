#!/usr/bin/env python
# coding: utf-8

import tornado.web
import json
from bson import json_util
from config.config import settings, redis_client


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        oauth_token = self.get_secure_cookie(settings["OAUTH"]["session_key"])
        user_name = redis_client.get(oauth_token)
        return user_name


class APIHandler(BaseHandler):

    def prepare(self):
        settings["current_user"] = self.get_current_user()

    def finish(self, chunk=None):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        return super(APIHandler, self).finish(chunk)

    def write(self, chunk):
        chunk = json.dumps(chunk, default=json_util.default)
        super(APIHandler, self).write(chunk)


class CheckHealthHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html", messages=[])

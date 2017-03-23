#!/usr/bin/env python
# coding: utf-8

import jsonschema
import time
import tornado.escape
from jsonschema import ValidationError
from tornado.web import HTTPError

from base import APIHandler
from config.config import settings, redis_client
from schemes import oauth_schema
from ..dao.user import UserDao
from ..util.tool import Tool


class LoginHandler(APIHandler):

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        try:
            jsonschema.validate(data, oauth_schema)
        except ValidationError as e:
            raise HTTPError(400, str(e))

        user_name = data['user_name']
        password = Tool.encode_by_md5(data['password'])

        user = UserDao.find_user({
            "user_name": user_name,
            "password": password
        })

        if not user:
            raise HTTPError(400, "wrong user_name or password")

        old_oauth_token = self.get_secure_cookie(settings["OAUTH"]["session_key"])
        if old_oauth_token:
            redis_client.delete(old_oauth_token)
        access_token = Tool.get_access_token(user_name)
        redis_client.set(access_token, user_name)
        self.set_secure_cookie(settings["OAUTH"]["session_key"], access_token)
        self.write({"message": "success"})

    def get(self):
        raise HTTPError(401, "need login")


class RegisterHandle(APIHandler):

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        try:
            jsonschema.validate(data, oauth_schema)
        except ValidationError as e:
            raise HTTPError(400, str(e))

        user_name = data['user_name']
        password = data['password']

        user = UserDao.find_user({"user_name": user_name})
        if user:
            raise HTTPError(400, "user_name exists")

        UserDao.save_user({
            "user_name": user_name,
            "password": Tool.encode_by_md5(password),
            "create_at": int(time.time()),
            "friends": [],
        })
        self.write({"user_name": user_name})

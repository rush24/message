#!/usr/bin/env python
# coding: utf-8

import hashlib

import time


class Tool(object):

    @classmethod
    def encode_by_md5(cls, data):
        return hashlib.md5(data).hexdigest()

    @classmethod
    def get_access_token(cls, user_name):
        access_token = user_name + str(time.time() * 1000)
        return cls.encode_by_md5(access_token)
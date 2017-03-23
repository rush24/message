#!/usr/bin/env python
# coding: utf-8
import os

import tornado.web
import tornado.httpserver
import tornado.ioloop
from urls import handlers


settings = {
    "cookie_secret": "fEW/0xRkRoy1zqYVIuBrDw==",
    "login_url": "/api/login",
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}


def main():
    server = tornado.httpserver.HTTPServer(
        tornado.web.Application(handlers, **settings))
    server.bind(9000)
    server.start()
    tornado.ioloop.IOLoop.instance().start()

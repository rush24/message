#!/usr/bin/env python
# coding: utf-8

oauth_schema = {
    "type": "object",
    "properties": {
        "user_name": {
            "type": "string"
        },
        "password": {
            "type": "string"
        },
    },
    "required": [
        "user_name",
        "password",
    ]
}

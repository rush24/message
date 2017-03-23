#!/usr/bin/env python
# coding: utf-8
from message.controller import base
from message.controller import friend
from message.controller import message_socket
from message.controller import oauth


handlers = [
    (r"/api/login", oauth.LoginHandler),
    (r"/api/register", oauth.RegisterHandle),
    (r"/api/friends", friend.FriendsHandler),
    (r"/api/add_friend/(?P<friend_name>[^/]+)", friend.FriendHandler),
    (r"/api/remove_friend/(?P<friend_name>[^/]+)", friend.FriendHandler),
    (r"/api/find_friend/(?P<friend_name>[^/]+)", friend.FriendHandler),
    (r"/api/message", message_socket.MessageSocketHandler),
    (r"/api/check_health", base.CheckHealthHandler),
]

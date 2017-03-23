#!/usr/bin/env python
# coding: utf-8

import tornado
from tornado.web import HTTPError

from base import APIHandler
from ..dao.user import UserDao


def get_friend_idx(user, f_name):
    f_idx = -1
    for idx, friend_detail in enumerate(user.get("friends")):
        if friend_detail.get('user_name') == f_name:
            f_idx = idx
            break
    return f_idx


class FriendsHandler(APIHandler):

    @tornado.web.authenticated
    def get(self):
        user_name = self.get_current_user()
        user = UserDao.find_user({"user_name": user_name})
        friends = user.get("friends")
        self.write(friends)


class FriendHandler(APIHandler):

    @tornado.web.authenticated
    def post(self, friend_name):
        user_name = self.get_current_user()
        friend = UserDao.find_user({"user_name": friend_name})
        if not friend:
            raise HTTPError(404, "friend no exists")

        user = UserDao.find_user({"user_name": user_name})

        find_friend = False
        for friend_detail in user.get("friends"):
            if friend_detail.get('user_name') == friend_name:
                find_friend = True
                break
        if find_friend:
            raise HTTPError(400, "you are friends already")

        user.get("friends").append({
            "user_name": friend_name,
            "unread_count": 0
        })
        UserDao.update_user(user)
        friend.get("friends").append({
            "user_name": user_name,
            "unread_count": 0
        })
        UserDao.update_user(friend)

        self.write({"message": "success"})

    @tornado.web.authenticated
    def delete(self, friend_name):
        user_name = self.get_current_user()

        friend = UserDao.find_user({"user_name": friend_name})
        if not friend:
            raise HTTPError(404, "friend no exists")

        user = UserDao.find_user({"user_name": user_name})

        friend_idx = get_friend_idx(user, friend_name)
        if friend_idx == -1:
            raise HTTPError(404, "You are not friends yet")
        del user.get("friends")[friend_idx]
        UserDao.update_user(user)

        me_idx = get_friend_idx(friend, user_name)
        del friend.get("friends")[me_idx]
        UserDao.update_user(friend)

        self.write({"message": "success"})

    @tornado.web.authenticated
    def get(self, friend_name):
        friend = UserDao.find_user({"user_name": friend_name})
        if not friend:
            raise HTTPError(404, "friend no exists")

        user_name = self.get_current_user()

        me_idx = get_friend_idx(friend, user_name)

        friend = {
            "user_name": friend.get("user_name"),
            "is_your_friend": me_idx != -1,
        }

        self.write(friend)

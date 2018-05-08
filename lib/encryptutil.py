#!/usr/bin/python
# -*- coding: UTF-8 -*-
# *************************************
# author:zhengqs
# create:201507
# desc: Config util
# usage
#
#
# *************************************

import hashlib
import time
import os
import sys
import getopt


class EncryptUtil(object):
    """
        加密工具类

    """

    def getEncrypt(self, password, access_key):
        tmp = ''
        m = 0;
        for i in range(0, len(password)):
            x = ord(password[i]) ^ ord(access_key[m])
            tmp += '%02X' % x
            m = m + 1
            if m == len(access_key):
                m = 0

        return tmp

    def getDecrypt(self, password, access_key):
        tmp = ''
        m = 0;

        for i in range(0, len(password), 2):
            x = password[i:i + 2]
            x = int(x, 16)
            x = x ^ ord(access_key[m])
            tmp += chr(x)
            m = m + 1
            if m == len(access_key):
                m = 0

        return tmp

    def getSign(self, timestamp, access_id, access_key):
        m2 = hashlib.md5()
        m2.update(timestamp + access_id + access_key)
        return m2.hexdigest()

    def checkTimestamp(timestamp, maxtime):
        tm1 = int(time.time())
        tm2 = int(timestamp)
        return tm1 - tm2 < maxtime


if __name__ == '__main__':
    _type = 'encrypt'
    _access_key = None
    _access_id = None
    _password = None
    opts, args = getopt.getopt(sys.argv[1:], "t:k:a:p:", ["help", "type=", "access_key=", "access_id=", "password="])
    for op, value in opts:
        if op in ("-t", "--type"):
            _type = value
        elif op in ("-k", "--access_key"):
            _access_key = value
        elif op in ("-a", "--access_id"):
            _access_id = value
        elif op in ("-p", "--password"):
            _password = value
        elif op in ("-h", "--help"):
            print 'this is help'
            sys.exit(0)

    encryptUtil = EncryptUtil()
    if _type == 'encrypt':
        if not _access_key or not _password:
            print 'Access_key and password must be entered'
            sys.exit(0)
        print 'encrypt:%s' % encryptUtil.getEncrypt(_password, _access_key)

    if _type == 'sign':
        if not _access_key or not _access_id:
            print 'Access_key and password must be entered'
            sys.exit(0)
        now = str(int(time.time()))
        print 'sign:%s' % encryptUtil.getSign(now, _access_id, _access_key)
        print 'timestamp:%s' % now


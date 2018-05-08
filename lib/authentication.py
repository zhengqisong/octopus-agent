# -*- coding: UTF-8 -*-
# *************************************
# author:zhengqs
# create:201707
# desc:
# **********************************
import time

from flask import Flask, request, g, make_response, jsonify, redirect
from functools import wraps
import ipaddr

from customexception import CustomAuthException
from encryptutil import EncryptUtil
from app.response import Response
from configutil import OctopusConfig


def session_require(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        # 现在是模拟登录，获取用户名，项目开发中获取session
        # username = request.args.get('username')
        #        username = 'admin'
        #        user = getattr(g, 'username', None)
        #        if user is None :
        #            print 'username is None'
        #        else :
        #            print g.username
        try:
            # 1.获取参数
            timestamp = request.args.get('timestamp')
            access_id = request.args.get('access_id')
            sign = request.args.get('sign')

            # 2.验证timestamp的有效性
            now = int(time.time())
            ltime = abs(now - int(timestamp))
            if ltime > 60 * 10:
                raise CustomAuthException('Timestamp timeout.')

            # 3.验证认证是否正确
            octopusConfig = OctopusConfig()
            apiOptions = octopusConfig.getApiOptions()

            _access_key = apiOptions.get("access_key")
            _access_id = apiOptions.get("access_id")
            _access_ips = apiOptions.get("access_ips")

            # print "remote addr %s" % request.remote_addr
            currentIp = ipaddr.IPv4Network(request.remote_addr)

            if not access_id or not _access_id or not _access_key or not _access_ips or access_id != _access_id:
                raise CustomAuthException('Authentication failed, access_id invalid.')

            ary_access_ip = _access_ips.split(";")
            ipAllow = False
            for tmp_ip in ary_access_ip:
                if currentIp and currentIp in ipaddr.IPNetwork(tmp_ip):
                    ipAllow = True
                    break
            if not ipAllow:
                raise CustomAuthException('Authentication failed, not allowed to access from ip %s,allow ip: %s.' % (
                request.remote_addr, _access_ips))

            util = EncryptUtil()
            mysign = util.getSign(timestamp, access_id, _access_key)
            mysign = mysign.lower()
            sign = sign.lower()
            if cmp(mysign, sign) != 0:
                raise CustomAuthException('Authentication failed, sign invalid.')

            # 4.exec business
            g.username = access_id
            return func(*args, **kwargs)

            # 判断用户名存在且用户名是什么的时候直接那个视图函数
            # if username and username == 'admin':
            #    g.username = username
            # args = (username,) + args
            #    return func(*args, **kwargs)
            # else:
            #    #如果没有就重定向到登录页面
            #    return redirect("login")
        except CustomAuthException, e:
            message = "error auth: %s" % str(e)
            return Response.make_json_response(message, success=False, code=-2)
        except Exception, ex:
            message = "error exec request: %s" % str(ex)
            return Response.make_json_response(message, success=False, code=-1)

    return decorator
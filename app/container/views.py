# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

from flask import request, g, make_response, jsonify, redirect
from authentication import session_require
from dockerutil import DockerUtil

from app.response import Response 
from app.container import container

@container.route('/list',methods=['GET'])
@session_require
def list():
    try:
        dockerUtil = DockerUtil()
        resContainerList = dockerUtil.getDockerPs(filters=request.args.getlist("filter"))
    
    except Exception,e:
        message = "error list container, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(resContainerList)

@container.route('/info',methods=['GET'])
@session_require
def inspect():
    try:
        dockerUtil = DockerUtil()
        containerInfo = dockerUtil.getDockerInspect(request.args.get("id"))
    except Exception,e:
        message = "error get container info, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(containerInfo)
    
@container.route('/stats',methods=['GET','POST'])
@session_require
def stats():
    try:
        dockerUtil = DockerUtil()
        stats = dockerUtil.getDockerStats(request.values.get("ids"))
    except Exception,e:
        message = "error stats container, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(stats)

@container.route('/logs',methods=['GET'])
@session_require
def logs():
    try:
        dockerUtil = DockerUtil()
        num = request.args.get("num")
        if num:
            num = int(num)
            
        logs = dockerUtil.getDockerLogs(request.values.get("id"), num)
    except Exception,e:
        message = "error get logs, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(logs)
   
@container.route('/truncatlogs',methods=['GET','POST'])
@session_require
def truncatlogs():
    try:
        dockerUtil = DockerUtil()
        message = dockerUtil.truncatDockerLogFile(request.values.get("id"))
    except Exception,e:
        message = "error truncat logs, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@container.route('/exec_command',methods=['GET','POST'])
@session_require
def exec_command():
    try:
        dockerUtil = DockerUtil()
        
        message = dockerUtil.getDockerExec(request.values.get("id"),request.values.get("cmd"))
    except Exception,e:
        message = "exec cmd `%s` error, ex:%s"%(request.values.get("cmd"), str(e))
        return Response.make_json_response(message,success=False, code=-1)
    
    return Response.make_json_response(message)

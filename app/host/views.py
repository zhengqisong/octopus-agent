# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

from flask import request, g, make_response, jsonify, redirect
from authentication import session_require
from dockerutil import DockerUtil
from hostutil import Host as HostUtil
import logging

from app.response import Response 
from app.host import host

@host.route('/docker/version',methods=['GET'])
@session_require
def dockerVersion():
    try:
        dockerUtil = DockerUtil()
        message = dockerUtil.getDockerVerion()
    
    except Exception,e:
        message = "error get docker version, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/docker/info',methods=['GET'])
@session_require
def dockerInfo():
    try:
        dockerUtil = DockerUtil()
        message = dockerUtil.getDockerInfo()
    
    except Exception,e:
        message = "error get docker info, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/docker/volumn/list_dangling',methods=['GET'])
@session_require
def dockerVolumnListDangling():
    try:
        dockerUtil = DockerUtil()
        message = dockerUtil.listDockerDanglingVolumn()
    
    except Exception,e:
        message = "error list dangling volumn, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/docker/volumn/rm_dangling',methods=['GET'])
@session_require
def dockerVolumnRmDangling():
    try:
        dockerUtil = DockerUtil()
        message = dockerUtil.rmDockerDanglingVolumn()
    
    except Exception,e:
        message = "error rm dangling volumn, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/hostname',methods=['GET'])
@session_require
def getHostname():
    try:
        hostUtil = HostUtil()
        message = hostUtil.getHostname()
    
    except Exception,e:
        message = "error get hostname, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/uname',methods=['GET'])
@session_require
def getUname():
    try:
        hostUtil = HostUtil()
        message = hostUtil.uname()
    
    except Exception,e:
        message = "error get uname, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/uptime',methods=['GET'])
@session_require
def uptime():
    try:
        hostUtil = HostUtil()
        message = hostUtil.get_uptime_stat()    
    except Exception,e:
        message = "error get uptime, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message) 

@host.route('/network/list',methods=['GET'])
@session_require
def networkList():
    try:
        hostUtil = HostUtil()
        message = hostUtil.network_list()
    
    except Exception,e:
        message = "error get network list, Ex:%s" % str(e)
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)
    
@host.route('/network/<string:ifname>/info',methods=['GET'])
@session_require
def networkInfo(ifname):
    try:
        hostUtil = HostUtil()
        message = hostUtil.networkinfo(ifname)
    
    except Exception,e:
        message = "error get network %s info, Ex:%s" % (ifname, str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)
    
    
@host.route('/cpu/info',methods=['GET'])
@session_require
def cpuinfo():
    try:
        hostUtil = HostUtil()
        message = hostUtil.get_cpuinfo_stat()
    
    except Exception,e:
        message = "error get cpu info, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)
    
@host.route('/cpu/loadavg',methods=['GET'])
@session_require
def loadavg():
    try:
        hostUtil = HostUtil()
        message = hostUtil.get_load_stat()
    
    except Exception,e:
        message = "error get cpu loadavg, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/disk/partitions',methods=['GET'])
@session_require
def diskPartitions():
    try:
        hostUtil = HostUtil()
        message = hostUtil.disk_partitions()
    
    except Exception,e:
        message = "error get disk partitions, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message) 
    
@host.route('/disk/stat',methods=['GET'])
@session_require
def diskstat():
    try:
        hostUtil = HostUtil()
        message = hostUtil.get_disk_stat()
    
    except Exception,e:
        message = "error get disk stat, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)      
    
@host.route('/disk/devicestat',methods=['GET'])
@session_require
def diskUsage():
    try:
        hostUtil = HostUtil()
        message = hostUtil.disk_usage(request.args.get("mountpoint"))
    
    except Exception,e:
        message = "error get disk device stat, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)      

@host.route('/disk/du',methods=['GET'])
@session_require
def diskPathDu():
    try:
        hostUtil = HostUtil()
        message = hostUtil.get_path_du(request.args.get("path"))
    
    except Exception,e:
        message = "error get disk device stat, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)  

@host.route('/mem/info',methods=['GET'])
@session_require
def memInfo():
    try:
        hostUtil = HostUtil()
        message = hostUtil.get_memory_stat()
    
    except Exception,e:
        message = "error get mem info, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)


@host.route('/image/list',methods=['GET'])
@session_require
def imageList():
    try:
        dockerUtil = DockerUtil()
        message = dockerUtil.getDockerImages()
    
    except Exception,e:
        message = "error get docker images list, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/sys/process/list',methods=['GET'])
@session_require
def getProcessList():
    
    try:
        hostUtil = HostUtil()
        message = hostUtil.processList()    
    except Exception,e:
        message = "error get sys process list, Ex:%s" % (str(e))
        return Response.make_json_response(message,success=False, code=-1)
        
    return Response.make_json_response(message)

@host.route('/sys/exec/command',methods=['GET','POST'])
@session_require
def execCommand():
    try:
        hostUtil = HostUtil()
        message = hostUtil.exec_command(request.values.get("cmd"))    
    except Exception,e:
        message = "error get sys process list, cmd(%s) Ex:%s" % (request.values.get("cmd"), str(e))
        return Response.make_json_response(message, success=False, code=-1)
        
    return Response.make_json_response(message)


# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201710
#desc: 
#**********************************
import re
import time
from datetime import datetime
import logging
import json
from threading import current_thread

from dockerutil import DockerUtil
from hostutil import Host
from mysqlsqlutil import MysqlSqlUtil

class RdsMongodbMonitorPlugin(object):
    def __init__(self, octopusd, paramter) :
        self.paramter = paramter
        self.octopusd = octopusd
        self.filters = paramter.get('filters')
        self.bss = paramter.get('bss')

        if paramter and paramter.get('hostname') :
            self.hostname = paramter.get('hostname')
        else :
            self.hostname = Host.getHostname()
        
        if paramter and paramter.get('containername') :
            self.containername = paramter.get('containername')
        else :
            self.containername = "{{name}}"
        
        if paramter and paramter.get('instance') :
            self.instance = paramter.get('instance')
        else :
            self.instance = None
        
        #if paramter and paramter.get('interval_time') :
        #    self.interval_time = paramter.get('interval_time')
        #else :
        #    self.interval_time = 0.5

        #{containerid:{cachetime:time, cachemap:{variabels:{},global_status:{}}}}
        self.status_cache = {}

    def get_now_utc_time(self):
        utc = datetime.utcnow()
        return datetime.strftime(utc, "%Y-%m-%dT%H:%M:%S.%fZ")
            
    def __get_variables(self, strinfo):
        return re.findall(r'\{\s*\{\s*(?P<name>.*?)\s*\}\s*\}', strinfo)
    
    def __replace_variable(self, key, value, strinfo):
        return re.sub(r'\{\s*\{\s*%s\s*\}\s*\}'%key, value, strinfo)
    
    def __convertVariables2String(self, varstring, containerInfo):
        if not varstring:
            return varstring
            
        variabels = self.__get_variables(varstring)
        if not variabels:
            return varstring
        
        variabels = list(set(variabels))
        for var in variabels:
            if var.lower() == 'id':
                varstring = self.__replace_variable(var, containerInfo['Id'],varstring)
            elif var.lower() == 'name':
                varstring = self.__replace_variable(var, containerInfo['name'],varstring)
            elif var.lower().startswith('env.'):
                evnval = ''
                evnname = var[4:]
                evns = containerInfo.get('envs')
                if evns:
                    evnval = evns.get(evnname)
                if evnval == None:
                    evnval = ''
                varstring = self.__replace_variable(var, evnval, varstring)
            elif var.lower().startswith('label.'):
                labelval = ''
                labelname = var[6:]
                labels = containerInfo.get('labels')
                if labels:
                    labelval = labels.get(labelname)
                if labelval == None:
                    labelval = ''
                varstring = self.__replace_variable(var, labelval, varstring)
        
        return varstring
        
    def run(self):
        try:
            logger = logging.getLogger("plugin.rdsmysql")
            dockerUtil = DockerUtil()
            #self.containername,self.instance
            
            containerList = dockerUtil.getDockerPs(filters=self.filters)

            utc_time = self.get_now_utc_time()

            thread = current_thread()
            print "before threadname:",thread.getName()
            containerId_list = []
            for containerInfo in containerList:
                containerId = ''
                try:
                    containerId = containerInfo['Id']
                    containerStatus = containerInfo['status']
                    containerId_list.append(containerId)

                    _host = self.__convertVariables2String(self.containername, containerInfo)
                    _instance = self.__convertVariables2String(self.instance, containerInfo)

                    if _instance == None:
                        _instance = ''
                    _bss = self.bss
                    monitor_cmd = containerInfo.get("envs").get("BEE_MONITOR_CMD")
                    if not monitor_cmd:
                        continue

                    #status
                    monitor_res = dockerUtil.getDockerExec(containerId, monitor_cmd)
                    monitor_res = json.loads(monitor_res)
                    #send message
                    event = {"time": utc_time, "containerid": containerId, "node": self.hostname, "bss": _bss,
                             "host": _host, "instance": _instance, "type": "business"}
                    event.update(monitor_res)

                    self.octopusd.sendMessage(self.paramter['output'], event)

                except Exception, containerEx:
                    logger.error("process containerId=%s was error,err: %s." %(containerId, str(containerEx)))
        except Exception, ex:
            logger.error("run was error,err: %s." % str(containerEx))

# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************
import re
import time
from datetime import datetime

from dockerutil import DockerUtil
from hostutil import Host

class ContainerPlugin(object):
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
        
        self.cacheStatsList = None
        self.cacheStatsTime = None
    
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
            dockerUtil = DockerUtil()
            #self.containername,self.instance
            
            containerList = dockerUtil.getDockerPs(filters=self.filters)
            ids = ""
            for info in containerList:
                ids +=" "+info['Id']
            
            #get stats first
            #if not self.cacheStatsList
            #    statsInfo1 = dockerUtil.getDockerStats(ids)
            #    self.cacheStatsTime = time.time()
            #    statsList1 = {}
            #    for statInfo in statsInfo1:
            #        statsList1[statInfo['id']] = statInfo
            #    self.cacheStatsList = statsList1
                
            #get stats second
            newStatsInfo = dockerUtil.getDockerStats(ids)
            # containerList=[{"Id":cId, "name":name, "status":status, "created":created, "imageId":imageId, "imageName":imageName, "envs":envs, "mounts":mounts, "logPath":logPath ,"networkMode":networkMode, "portBindings":portBindings, "labels":labels}]
            #statsInfo=[{"id":statInfo[0],"cpu":statInfo[1],"mem":statInfo[2],"netin":statInfo[3],"netout":statInfo[4],"blockin":statInfo[5],"bolckout":statInfo[6]}]
            
            newStatsList = {}
            
            for statInfo in newStatsInfo:
                newStatsList[statInfo['id']] = statInfo
                
            utc_time = self.get_now_utc_time()
            
            for containerInfo in containerList:
                containerId =  containerInfo['Id']
                containerStatus =  containerInfo['status']
                #
                _node = self.hostname
                _host = self.__convertVariables2String(self.containername, containerInfo)
                _instance = self.__convertVariables2String(self.instance, containerInfo)
                if _instance == None:
                    _instance = ''
                _bss = self.bss
                
                #send status
                _type = 'status'
                _type_instance = containerStatus
                _value = 1 if containerStatus.lower() in ['created','restarting','running'] else 0
                
                event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":_type,"type_instance":_type_instance,"value":_value}
                self.octopusd.sendMessage(self.paramter['output'], event)
                
                if not newStatsList.get(containerId):
                    continue
                
                cpu = newStatsList[containerId]['cpu']
                mem = newStatsList[containerId]['mem']
                netin = newStatsList[containerId]['netin']
                netout = newStatsList[containerId]['netout']
                blockin = newStatsList[containerId]['blockin']
                blockout = newStatsList[containerId]['blockout']
                
                # send cpu
                event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'cpu',"type_instance":'usage_rate',"value":cpu}
                self.octopusd.sendMessage(self.paramter['output'], event)
                # send mem
                event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'mem',"type_instance":'usage_rate',"value":mem}
                self.octopusd.sendMessage(self.paramter['output'], event)
                # send netin
                event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'net',"type_instance":'netin',"value":netin}
                self.octopusd.sendMessage(self.paramter['output'], event)
                # send netout
                event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'net',"type_instance":'netout',"value":netout}
                self.octopusd.sendMessage(self.paramter['output'], event)
                # send blockin
                event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'blockio',"type_instance":'blockin',"value":blockin}
                self.octopusd.sendMessage(self.paramter['output'], event)
                # send blockout
                event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'blockio',"type_instance":'blockout',"value":blockout}
                self.octopusd.sendMessage(self.paramter['output'], event)
                
                if self.cacheStatsList and self.cacheStatsList.get(containerId):                
                    cacheNetin = self.cacheStatsList[containerId]['netin']
                    cacheNetout = self.cacheStatsList[containerId]['netout']
                    cacheBlockin = self.cacheStatsList[containerId]['blockin']
                    cacheBlockout = self.cacheStatsList[containerId]['blockout']
                    #netininc
                    netininc = netin-cacheNetin
                    if netininc >= 0:
                        event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'net',"type_instance":'netininc',"value":round(float(netininc), 2)}
                        self.octopusd.sendMessage(self.paramter['output'], event)                
                    #netoutinc
                    netoutinc = netout - cacheNetout
                    if netininc >= 0:
                        event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'net',"type_instance":'netoutinc',"value":round(float(netoutinc), 2)}
                        self.octopusd.sendMessage(self.paramter['output'], event)
                    #blockininc
                    blockininc = blockin - cacheBlockin
                    if blockininc >= 0:
                        event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'blockio',"type_instance":'blockininc',"value":round(float(blockininc), 2)}
                        self.octopusd.sendMessage(self.paramter['output'], event)
                    #blockoutinc
                    blockoutinc = blockout - cacheBlockout
                    if blockoutinc >= 0:
                        event = {"time":utc_time, "containerid":containerId, "node":self.hostname, "bss":_bss, "host":_host, "instance":_instance, "type":'blockio',"type_instance":'blockoutinc',"value":round(float(blockoutinc), 2)}
                        self.octopusd.sendMessage(self.paramter['output'], event)
                    
            self.cacheStatsList = newStatsList
            if len(newStatsList) <= 0:
                self.cacheStatsList = None
        except Exception,ex:
            print ex


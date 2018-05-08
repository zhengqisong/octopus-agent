# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************
from hostutil import Host
from datetime import datetime

class HostDfPlugin(object):
    def __init__(self, octopusd, paramter) :
        self.paramter = paramter
        self.octopusd = octopusd
        if paramter and paramter.get('hostname') :
            self.hostname = paramter.get('hostname')
        else :
            self.hostname = Host.getHostname()
        self.disk = paramter.get('disk')
    
    def get_now_utc_time(self):
        utc = datetime.utcnow()
        return datetime.strftime(utc, "%Y-%m-%dT%H:%M:%S.%fZ")
        
    def run(self):
        try:
            utc_time = self.get_now_utc_time()
            disks = self.disk.split(",")
            for disk in disks:
                if not disk:
                    continue
                diskInfo = Host.disk_usage(disk)
                disk = disk.replace("/","_")
                if disk.startswith('_'):
                   disk = disk[1:]
                   if len(disk)==0:
                       disk = 'root'
                event = {"time":utc_time, "host":self.hostname, "type":"df","instance":disk,"type_instance":"usage_rate","value":diskInfo['usedRate']}
                self.octopusd.sendMessage(self.paramter['output'], event)
                
                event = {"time":utc_time, "host":self.hostname, "type":"df","instance":disk, "type_instance":"free_size","value":diskInfo['freeSize']}
                self.octopusd.sendMessage(self.paramter['output'], event)
            
        except Exception,ex:
            print ex

class HostDuPlugin(object):
    def __init__(self, octopusd, paramter) :
        self.paramter = paramter
        self.octopusd = octopusd
        if paramter and paramter.get('hostname') :
            self.hostname = paramter.get('hostname')
        else :
            self.hostname = Host.getHostname()
        self.path = paramter.get('path')
    
    def get_now_utc_time(self):
        utc = datetime.utcnow()
        return datetime.strftime(utc, "%Y-%m-%dT%H:%M:%S.%fZ")
        
    def run(self):
        try:
            utc_time = self.get_now_utc_time()
            paths = self.path.split(",")
            for path in paths:
                if not path:
                    continue
                pathSize = Host.get_path_du(path)
                path = path.replace("/","_")
                if path.startswith('_'):
                   path = path[1:]
                event = {"time":utc_time, "host":self.hostname, "type":"du","instance":path,"type_instance":"total","value":pathSize}
                self.octopusd.sendMessage(self.paramter['output'], event)
            
        except Exception,ex:
            print ex
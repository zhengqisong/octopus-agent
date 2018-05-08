# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

from hostutil import Host
from datetime import datetime

class HostInterfacePlugin(object):
    def __init__(self, octopusd, paramter) :
        self.paramter = paramter
        self.octopusd = octopusd
        if paramter and paramter.get('hostname') :
            self.hostname = paramter.get('hostname')
        else :
            self.hostname = Host.getHostname()
        self.interface = paramter.get('interface')
    
    def get_now_utc_time(self):
        utc = datetime.utcnow()
        return datetime.strftime(utc, "%Y-%m-%dT%H:%M:%S.%fZ")
        
    def run(self):
        try:
            utc_time = self.get_now_utc_time()
            interfaces = self.interface.split(",")
            for interface in interfaces:
                if not interface:
                    continue
                netRate = Host.get_net_rate(interface)
                
                event = {"time":utc_time, "host":self.hostname, "type":"interface","instance":interface,"type_instance":"bandwidth","value":netRate['rate']}
                self.octopusd.sendMessage(self.paramter['output'], event)
                
        except Exception,ex:
            print ex
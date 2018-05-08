# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************
import json
import socket

class OutputUdpPlugin(object):
    def __init__(self, paramter):
        self.paramter = paramter
        self.address = (paramter['ip'], paramter['port'])
        self.sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def run(self, message):
        if type(message) != type('ass') :
            message = json.dumps(message)
            
        #print "OutputStdOutPlugin:%s" % message
        self.sc.sendto(message, self.address)
        return "ok"
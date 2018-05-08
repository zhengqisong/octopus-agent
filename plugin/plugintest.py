# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

class InputTestPlugin(object):
    def __init__(self, octopusd, paramter):
        self.paramter = paramter
        self.octopusd = octopusd
        #print octopusd
        #print paramter
        
    
    def run(self):
        self.octopusd.sendMessage(self.paramter['output'], "test plugin send message....")
        
        
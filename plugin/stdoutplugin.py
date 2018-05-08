# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************
import json

class OutputStdOutPlugin(object):
    def __init__(self, paramter):
        self.paramter = paramter        
    
    def run(self, message):
        if type(message) != type('ass') :
            message = json.dumps(message)
        
        print "OutputStdOutPlugin:%s" % message
        return "ok"
# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

class Octopusd(object):
    def __init__(self, pluginManager):
        self.pluginManager = pluginManager
    
    def sendMessage(self, pluginId, message):
        outputPlugin = self.pluginManager.get_output_plugin(pluginId)
        if not outputPlugin:
            raise ImportError("send output plugin id not exist, id:%s" % pluginId)
        outputPlugin.getObj().run(message)
        return "ok"

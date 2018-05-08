# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************
from octopusutils import import_object, import_class, import_module
from octopusd import Octopusd

class Plugin(object):
    def __init__(self, manager, config):
        #_id, filepath, name, _type,
        self.id= config['id']
        self.name = config['name']
        self.filepath = config['filepath']
        self.type = config['type']
        self.manager = manager
        self.config = config
        self.obj = None
    
    def getId(self):
        return self.id
    
    def getType(self):
        return self.type
    
    def getName(self):
        return self.name
    
    def getConfig(self):
        return self.config
    
    def getObj(self):
        if self.obj :
           return self.obj
        
        paramter = None
        if 'paramter' in self.config.keys() :
            paramter = self.config['paramter']
        
        if self.type.lower() == "input":
            octopusd = Octopusd(self.manager)
            self.obj = import_object(self.filepath, octopusd, paramter)
            return self.obj
        elif self.type.lower() == "output":
            self.obj = import_object(self.filepath, paramter)
            return self.obj
        raise ImportError("plugin type must in [input, output], id:%s" % self.id)
    
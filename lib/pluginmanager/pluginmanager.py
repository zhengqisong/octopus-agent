# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************
import json

from flask_apscheduler import APScheduler

from plugin import Plugin

class PluginManager(object):
    def __init__(self):
        self.input_plugin = {}
        self.output_plugin = {}
        self.scheduler = APScheduler()
    
    def load_conf(self, app, configfile):
        #print configfile 
        file_object = open(configfile)
        all_the_text = None
        try:
            all_the_text = file_object.read()            
        finally:
            file_object.close()
    
        config = json.loads(all_the_text)
        _key = config.keys();
        if "input" in _key:
            plugin_input = config['input']
            for i in range(len(plugin_input)):
                self.register_plugin(Plugin(self, plugin_input[i]))
        
        if "output" in _key:
            plugin_input = config['output']
            for i in range(len(plugin_input)):
                self.register_plugin(Plugin(self, plugin_input[i]))
                
        self.scheduler.init_app(app)
        self.scheduler.start()
        
        
    def register_plugin(self, plugin):
        if plugin==None or plugin.getType() ==None:
            print "error"
            return
        if plugin.getType().lower() == 'input':
            self.input_plugin[plugin.getId()] = plugin
            
            plugObj = plugin.getObj()
            plugConfig = plugin.getConfig()
            trigger = plugConfig.get('trigger')

            if plugConfig.get('seconds'):
                seconds = int(plugConfig.get('seconds'))
                #trigger= date, interval or cron
                self.scheduler.add_job(func=plugObj.run,id=plugin.getId(), trigger=trigger,seconds=seconds)
            else:
                self.scheduler.add_job(func=plugObj.run,id=plugin.getId(), trigger=trigger)
        elif plugin.getType().lower() == 'output':
            self.output_plugin[plugin.getId()] = plugin
            plugObj = plugin.getObj()
    
    def get_output_plugin(self, pluginId):
        if pluginId in self.output_plugin.keys():
            return self.output_plugin[pluginId]
        else:
            return None
    
    def get_input_plugin(self, pluginId):
        if pluginId in self.input_plugin.keys():
            return self.input_plugin[pluginId]
        else:
            return None
              
        
    
        
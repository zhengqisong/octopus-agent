# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************
import json
import socket
import threading
import time
import Queue
import logging
import logging.config

class OutputTcpPlugin(object):
    def __init__(self, paramter):
        self.logger = logging.getLogger("octopus.plugin.outputtcpplugin")
        self.paramter = paramter
        self.message = None
        cachesize = paramter.get("cachesize")
        if cachesize == None:
            cachesize = 500
        self.queue = Queue.Queue(maxsize = cachesize)
        self.host = self.paramter.get('ip')
        self.port = self.paramter.get('port')
        self.sock = self.doConnect()
        if not self.sock:
            raise Exception('can not connect server(%s,%d).' % (self.host, self.port))
        t = threading.Thread(target=self.send2server)
        t.setDaemon(True)
        t.start()
        self.logger.info('OutputTcpPlugin is running tcp server(%s:%d)' % (self.host, self.port))
        
    def doConnect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            sock.settimeout(10)
            sock.connect((self.host, self.port))
            sock.settimeout(None)
        except :
            #sock = None
            pass
        return sock
    
    def send2server(self):
        message = None
        while(True):
            try:
                if message == None:
                    message = self.queue.get()
                self.sock.sendall('%s\r\n'%message)
                message = None
            except socket.error, e:
                self.logger.warn('send tcp data to (%s:%d) sock error' % (self.host, self.port))
                try:
                    if self.sock:
                        self.sock.close()
                except:
                    pass
                self.sock = self.doConnect()                    
                time.sleep(1)
                
    def sendMessage(self, message):
        self.message = message
        try:
            if self.paramter.get('block') == True:
                self.queue.put(message)
            else:
                self.queue.put_nowait(message)
        except Queue.Full,ex:
            return 'error'
        return 'ok'
        
    def run(self, message):
        try:
            if type(message) != type('ass') :
                message = json.dumps(message)
            
            return self.sendMessage(message)
        except:
            return "error"

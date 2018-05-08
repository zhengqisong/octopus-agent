# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'allowed_host:job1',
            'args': (1, 2),
            'trigger': 'interval',
            'seconds': 10
        }
    ]

    #SCHEDULER_ALLOWED_HOSTS = ['my_servers_name']
    #SCHEDULER_API_ENABLED = True
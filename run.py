#!/usr/bin/python
# -*- coding: UTF-8 -*-
# *************************************
# author:zhengqs
# create:201707
# desc:
# ***********************************

import os
import sys
import getopt
import logging
import logging.config

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# if not BASE_DIR:
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, os.path.join(BASE_DIR, 'lib'))
# print os.path.dirname(os.path.realpath(__file__)), os.path.join(BASE_DIR, 'lib')
# sys.path.insert(0, os.path.join(BASE_DIR, 'plugin'))

# print os.path.join(BASE_DIR, 'lib')
# argv = sys.argv
from flask_apscheduler import APScheduler
from flask import Flask
from config import Config
from pluginmanager.pluginmanager import PluginManager
from hostutil import Host as HostUtil
from configutil import OctopusConfig

# from app.test import test
from app.container import container
from app.host import host

app = Flask(__name__,
            # template_folder='templates', #指定模板路径，可以是相对路径，也可以是绝对路径。
            # static_folder='static',  #指定静态文件前缀，默认静态文件路径同前缀
            # static_url_path='/opt/auras/static',     #指定静态文件存放路径。
            )

# app.register_blueprint(test, url_prefix='/test')    #注册asset蓝图，并指定前缀
app.register_blueprint(container, url_prefix='/container')  # 注册asset蓝图，并指定前缀
app.register_blueprint(host, url_prefix='/host')  # 注册asset蓝图，并指定前缀


def usage():
    print 'Usage:'
    print '\tpython run.py [OPTION]'
    print 'Options:'
    print '\t-i,--ip IP\t\tlistener ip,default is 0.0.0.0'
    print '\t-p,--port PORT\t\tlistener PORT,default 33601'
    print '\t-l,--log logfile\tlog file name'
    print '\t-f,--config config\tLoad the octopus config from a specific file'
    # print '\t--log.level config\tSet the log level for logstash. Possible values are:'
    # print '\t\t\t\t  - fatal'
    # print '\t\t\t\t  - error'
    # print '\t\t\t\t  - warn'
    # print '\t\t\t\t  - info'
    # print '\t\t\t\t  - debug'
    # print '\t\t\t\t  - trace'
    # print '\t\t\t\t(default: "warn")'
    print '\t-v,--version\t\tEmit the version of octopus and its friends,then exit.'
    print '\t-h,--help\t\tprint help'


def printVersion():
    print 'Octopus version 0.1.1, build python 2.7.5'


if __name__ == '__main__':
    # argv = sys.argv
    # if argv == None:
    #    raise Exception("error,config error.")
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf/octopus.conf")
    octopusConfig = OctopusConfig()

    octopusConfig.load(config_file)
    apiOptions = octopusConfig.getApiOptions()
    ip = apiOptions.get("ip")
    port = apiOptions.get("port")

    octopusdOptions = octopusConfig.getOctopusdOptions()
    logfile = octopusdOptions.get("log")
    scheduleConfig = octopusdOptions.get("config")
    if logfile and not logfile.startswith("/"):
        logfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf", logfile)
    if scheduleConfig and not scheduleConfig.startswith("/"):
        scheduleConfig = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf", scheduleConfig)

    config = {}

    config['ip'] = ip if not ip else '0.0.0.0'
    config['port'] = int(port) if not port == None else 33601
    config['log'] = logfile if not logfile == None else None
    config['config'] = scheduleConfig if not scheduleConfig == None else None

    config['logLevel'] = 'warn'
    opts, args = getopt.getopt(sys.argv[1:], "hl:i:p:f:v", ["help", "ip=", "port=", "log=", "config=", "log.level="])

    for op, value in opts:
        if op in ("-i", "--ip"):
            config['ip'] = value
        elif op in ("-p", "--port"):
            config['port'] = value
        elif op in ("-l", "--log"):
            config['log'] = value
        elif op in ("-f", "--config"):
            config['config'] = value
        elif op in ("log.level",):
            config['logLevel'] = value
        elif op in ("-v", "--version"):
            printVersion()
            sys.exit(0)
        elif op in ("-h", "--help"):
            usage()
            sys.exit(0)
    if config['log']:
        logging.config.fileConfig(config['log'])

    logger = logging.getLogger("octopus.server")
    # app.config.from_object(Config())
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    pluginManager = PluginManager()
    pluginManager.load_conf(app, config.get('config'))
    logger.info('successfully started server %s:%d' % (config['ip'], int(config['port'])))

    app.run(host=config['ip'], port=config['port'],
            threaded=True)  # 运行flask http程序，host指定监听IP，port指定监听端口，调试时需要开启debug模式。

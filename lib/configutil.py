#!/usr/bin/python
# -*- coding: UTF-8 -*-
# *************************************
# author:zhengqs
# create:201507
# desc: Config util
# usage
#
#
# *************************************

import os
import fcntl
import ConfigParser


class CaseConfigParser(ConfigParser.ConfigParser):
    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class ConfigUtil:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, "r+")

    def get_option(self, section, option):
        '''
        获取参数项的值
        '''
        config = CaseConfigParser()
        config.read(self.filename)
        return config.get(section, option)

    def has_option(self, section, option):
        '''
        判断参数项是否存在
        True：存在，False：不存在
        '''
        config = CaseConfigParser()
        config.read(self.filename)
        if not config.has_section(section):
            return False
        return config.has_option(section, option)

    def set_option(self, section, option, value):
        '''
        设置选项参数，如果存在就更新，否则增加，section不存在将增加
        '''
        # 锁定文件，防止冲突
        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)
        try:
            config = CaseConfigParser()
            config.read(self.filename)
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, option, value)
            self.write(config)
        finally:
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)

    def remove_option(self, section, option):
        '''
        删除选项参数
        '''
        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)
        try:
            config = CaseConfigParser()
            config.read(self.filename)
            if config.has_section(section) and config.has_option(section, option):
                config.remove_option(section, option)
                self.write(config)
        finally:
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)

    def get_section_options(self, section):
        '''
        列出所有section下的参数项
        @return {option:value,option:value}
        '''
        obj = {}
        config = CaseConfigParser()
        config.read(self.filename)
        # print 'ConfigUtil.get_section_options:section:'+section+'\n'
        if config.has_section(section):
            # print 'ConfigUtil.get_section_options:has section\n'
            options = config.options(section)
            for option in options:
                value = config.get(section, option)
                obj[option] = value
        return obj

    def add_section_options(self, section, options):
        '''
        同时向section中添加多个option
        @param options {option1:value,option2:value}
        '''
        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)
        try:
            config = CaseConfigParser()
            config.read(self.filename)
            if not config.has_section(section):
                config.add_section(section)
            for key in options.keys():
                config.set(section, key, options[key])
            self.write(config)
        finally:
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)

    def sections(self):
        '''
        列出所有的section,返回数组
        '''
        config = CaseConfigParser()
        config.read(self.filename)
        return config.sections()

    def has_section(self, section):
        '''
        判断section是否存在
        '''
        obj = {}
        config = CaseConfigParser()
        config.read(self.filename)
        return config.has_section(section)

    def add_section(self, section):
        '''
        增加section，如果存在直接返回，否则增加
        '''
        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)
        try:
            config = CaseConfigParser()
            config.read(self.filename)
            if not config.has_section(section):
                config.add_section(section)
                self.write(config)
        finally:
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)

    def remove_section(self, section):
        '''
        删除section项目,如果有option，将同时删除
        '''
        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)
        try:
            config = CaseConfigParser()
            config.read(self.filename)
            config.remove_section(section)
            self.write(config)
        finally:
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)

    def write(self, config):
        fp = open(self.filename, 'w')
        config.write(fp)
        fp.flush()
        fp.close


class OctopusConfig:
    def __init__(self):
        pass

    def load(self, _file):
        global _global_config
        _global_config = None
        global global_config_file
        global_config_file = None
        if _global_config == None:
            # cf =os.path.join(os.path.split(os.path.realpath(os.path.dirname(os.path.realpath(__file__))))[0],"conf/octopus.conf")
            config = CaseConfigParser()
            config.read(_file)
            _global_config = config
            global_config_file = _file

    def __getSection(self, section):
        obj = {}
        if _global_config.has_section(section):
            options = _global_config.options(section)
            for option in options:
                value = _global_config.get(section, option)
                obj[option] = value
        return obj

    def getApiOptions(self):
        apiOptions = self.__getSection("api")
        octopus_agent_access_key = os.environ.get("OCTOPUS_AGENT_ACCESS_KEY")
        octopus_agent_access_id = os.environ.get("OCTOPUS_AGENT_ACCESS_ID")
        octopus_agent_access_ips = os.environ.get("OCTOPUS_AGENT_ACCESS_IPS")

        # print "octopus_agent_access_ips:%s" % octopus_agent_access_ips
        if octopus_agent_access_key:
            apiOptions['access_key'] = octopus_agent_access_key
        if octopus_agent_access_id:
            apiOptions['access_id'] = octopus_agent_access_id
        if octopus_agent_access_ips:
            apiOptions['access_ips'] = octopus_agent_access_ips
        # print "octopus_agent_access_ips:%s" % apiOptions.get('access_ips')
        # print "octopus_agent_access_key:%s" % apiOptions.get('access_key')
        return apiOptions

    def getOctopusdOptions(self):
        octopusdOptions = self.__getSection("octopusd")
        octopus_agent_scheduler_file = os.environ.get("OCTOPUS_AGENT_SCHEDULER_FILE")
        octopus_agent_log_file = os.environ.get("OCTOPUS_AGENT_LOG_FILE")

        if octopus_agent_scheduler_file:
            apiOptions['config'] = octopus_agent_access_key
        if octopus_agent_log_file:
            apiOptions['log'] = octopus_agent_log_file

        return octopusdOptions
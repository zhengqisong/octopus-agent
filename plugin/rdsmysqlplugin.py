# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201710
#desc: 
#**********************************
import re
import time
from datetime import datetime
import logging
import json
from threading import current_thread

from dockerutil import DockerUtil
from hostutil import Host
from mysqlsqlutil import MysqlSqlUtil
class RdsMysqlMonitorPlugin(object):
    def __init__(self, octopusd, paramter) :
        self.paramter = paramter
        self.octopusd = octopusd
        self.filters = paramter.get('filters')
        self.bss = paramter.get('bss')

        if paramter and paramter.get('hostname') :
            self.hostname = paramter.get('hostname')
        else :
            self.hostname = Host.getHostname()
        
        if paramter and paramter.get('containername') :
            self.containername = paramter.get('containername')
        else :
            self.containername = "{{name}}"
        
        if paramter and paramter.get('instance') :
            self.instance = paramter.get('instance')
        else :
            self.instance = None
        
        #if paramter and paramter.get('interval_time') :
        #    self.interval_time = paramter.get('interval_time')
        #else :
        #    self.interval_time = 0.5

        #{containerid:{cachetime:time, cachemap:{variabels:{},global_status:{}}}}
        self.status_cache = {}

    def get_now_utc_time(self):
        utc = datetime.utcnow()
        return datetime.strftime(utc, "%Y-%m-%dT%H:%M:%S.%fZ")
            
    def __get_variables(self, strinfo):
        return re.findall(r'\{\s*\{\s*(?P<name>.*?)\s*\}\s*\}', strinfo)
    
    def __replace_variable(self, key, value, strinfo):
        return re.sub(r'\{\s*\{\s*%s\s*\}\s*\}'%key, value, strinfo)
    
    def __convertVariables2String(self, varstring, containerInfo):
        if not varstring:
            return varstring
            
        variabels = self.__get_variables(varstring)
        if not variabels:
            return varstring
        
        variabels = list(set(variabels))
        for var in variabels:
            if var.lower() == 'id':
                varstring = self.__replace_variable(var, containerInfo['Id'],varstring)
            elif var.lower() == 'name':
                varstring = self.__replace_variable(var, containerInfo['name'],varstring)
            elif var.lower().startswith('env.'):
                evnval = ''
                evnname = var[4:]
                evns = containerInfo.get('envs')
                if evns:
                    evnval = evns.get(evnname)
                if evnval == None:
                    evnval = ''
                varstring = self.__replace_variable(var, evnval, varstring)
            elif var.lower().startswith('label.'):
                labelval = ''
                labelname = var[6:]
                labels = containerInfo.get('labels')
                if labels:
                    labelval = labels.get(labelname)
                if labelval == None:
                    labelval = ''
                varstring = self.__replace_variable(var, labelval, varstring)
        
        return varstring
        
    def run(self):
        try:
            logger = logging.getLogger("plugin.rdsmysql")
            dockerUtil = DockerUtil()
            #self.containername,self.instance
            
            containerList = dockerUtil.getDockerPs(filters=self.filters)

            utc_time = self.get_now_utc_time()

            thread = current_thread()
            print "before threadname:",thread.getName()
            containerId_list = []
            delList = []
            for containerInfo in containerList:
                containerId = ''
                try:
                    containerId = containerInfo['Id']
                    containerStatus = containerInfo['status']
                    containerId_list.append(containerId)

                    _host = self.__convertVariables2String(self.containername, containerInfo)
                    _instance = self.__convertVariables2String(self.instance, containerInfo)

                    if _instance == None:
                        _instance = ''
                    _bss = self.bss
                    rootpwd = containerInfo.get("envs").get("MYSQL_ROOT_PASSWORD")
                    if not rootpwd:
                        continue

                    #status
                    global_status = dockerUtil.getDockerExec(containerId, "mysql -uroot -p%s -e \"%s\"" % (
                        rootpwd, MysqlSqlUtil.getGlobalStatusSql(['Slave_running','Uptime','Questions','Com_select','Com_insert','Com_update',
                                                                  'Com_delete','com_commit','com_rollback','Threads_connected','Aborted_clients',
                                                                  'Aborted_connects','Innodb_buffer_pool_pages_total','Innodb_buffer_pool_pages_free',
                                                                  'Innodb_buffer_pool_pages_data','Innodb_buffer_pool_pages_dirty','Innodb_row_lock_time',
                                                                  'Innodb_row_lock_current_waits','Innodb_row_lock_waits','Innodb_data_reads',
                                                                  'Innodb_data_writes','Innodb_os_log_fsyncs','Open_tables','Opened_tables','Open_files',
                                                                  'Opened_files'])))
                    global_status = MysqlSqlUtil.analysisVariablesResult(global_status)

                    # print global_status.get("uptime")

                    #variables
                    variables = dockerUtil.getDockerExec(containerId, "mysql -uroot -p%s -e \"%s\"" % (
                        rootpwd, MysqlSqlUtil.getVariablesSql(['server_uuid','max_connections','max_connect_errors','Threads_connected',
                                                               'table_open_cache','open_files_limit'])))

                    variables = MysqlSqlUtil.analysisVariablesResult(variables)

                    #masterstatus
                    masterstatus = None
                    #if global_status.get("slave_running") and global_status.get("slave_running").lower()=='off':
                    masterstatus = dockerUtil.getDockerExec(containerId, "mysql -uroot -p%s -e \"%s\"" % (
                        rootpwd, MysqlSqlUtil.getMasterStatusSql()))
                    masterstatus = MysqlSqlUtil.analysisKeyValueResult(masterstatus)

                    if masterstatus and len(masterstatus) > 0:
                        masterstatus = masterstatus[0]
                        global_status["slave_running"] = 'off'

                    #slavestatus
                    slavestatus = None
                    #if global_status.get("slave_running") and global_status.get("slave_running").lower() == 'on':

                    slavestatus = dockerUtil.getDockerExec(containerId, "mysql -uroot -p%s -e \"%s\"" % (
                        rootpwd, MysqlSqlUtil.getSlaveStatusSql()))
                    slavestatus = MysqlSqlUtil.analysisKeyValueResult(slavestatus)
                    if slavestatus and len(slavestatus) > 0:
                        slavestatus = slavestatus[0]
                        global_status["slave_running"] = 'on'


                    #sumConnectErrors
                    sumConnectErrors = dockerUtil.getDockerExec(containerId, "mysql -uroot -p%s -e \"%s\"" % (
                        rootpwd, MysqlSqlUtil.getSumConnectErrorsSql()))
                    sumConnectErrors = MysqlSqlUtil.analysisKeyValueResult(sumConnectErrors)
                    if sumConnectErrors:
                        sumConnectErrors = sumConnectErrors[0].get('sum_connect_errors')
                    else:
                        sumConnectErrors = 0

                    #节点信息
                    current_time = int(time.time())
                    nodeInfo = self.nodeinfo(variables, global_status, masterstatus, slavestatus)
                    #print nodeInfo

                    #吞吐量
                    throughputInfo = self.throughput(containerId, global_status, current_time)
                    #print throughputInfo

                    #连接信息
                    connectsInfo = self.connects(variables, global_status, sumConnectErrors)
                    #print connectsInfo

                    #innodb信息
                    innodbsInfo = self.innodbs(containerId, global_status, current_time)
                    #print innodbsInfo

                    #文件打开数信息
                    cursorInfo = self.cursor(containerId, variables, global_status, current_time)
                    #print cursorInfo

                    # {containerid:{cachetime:time, cachemap:{variabels:{},global_status:{}}}}
                    self.status_cache[containerId] = {"cachetime": current_time, "cachemap": {"variabels":variables, "global_status": global_status}}

                    #send message
                    event = {"time": utc_time, "containerid": containerId, "node": self.hostname, "bss": _bss,
                             "host": _host, "instance": _instance, "type": "business"}
                    event.update(nodeInfo)
                    event.update(throughputInfo)
                    event.update(connectsInfo)
                    event.update(innodbsInfo)
                    event.update(cursorInfo)

                    self.octopusd.sendMessage(self.paramter['output'], event)

                except Exception, containerEx:
                    logger.exception(containerEx)
                    logger.error("process containerId=%s was error,err: %s." %(containerId, str(containerEx)))
                    logger.error(nodeInfo)
                    logger.error(throughputInfo)
                    logger.error(connectsInfo)
                    logger.error(innodbsInfo)
                    logger.error(cursorInfo)
                    delList.append(containerId)

        except Exception, ex:
            logger.error("run was error,err: %s." % str(containerEx))
            logger.exception(ex)

        #移除失效的cache信息
        cache_contaierId_list = self.status_cache.keys()
        for containerId in cache_contaierId_list:
            if not containerId in containerList:
                delList.append(containerId)

        for containerId in delList:
            if containerId in cache_contaierId_list:
                del self.status_cache[containerId]


    def nodeinfo(self, variables, global_status, masterstatus, slavestatus):
        nodetype = 'node'
        server_uuid = variables.get("server_uuid")
        master_uuid = ''
        syncstatus = 'yes'
        binlogfile = ''
        binlogpos = 0
        sbm = 0
        uptime = 0

        uptime = int(global_status.get("Uptime".lower()))
        if global_status.get("slave_running") and global_status.get("slave_running").lower() == 'off':
            nodetype = 'master'
        elif global_status.get("slave_running") and global_status.get("slave_running").lower() == 'on':
            nodetype = 'slave'

        if nodetype == 'slave' and slavestatus:
            master_uuid = slavestatus.get('Master_UUID'.lower())
            syncstatus = slavestatus.get('Slave_IO_Running'.lower()).lower()
            binlogfile = slavestatus.get('Master_Log_File'.lower()).lower()
            binlogpos = int(slavestatus.get('Read_Master_Log_Pos'.lower()).lower())
            sbm = int(slavestatus.get('Seconds_Behind_Master'.lower()).lower())
        elif nodetype == 'master' and masterstatus:
            binlogfile = masterstatus.get('File'.lower()).lower()
            binlogpos = int(masterstatus.get('Position'.lower()).lower())

        return {"nodetype":nodetype, "server_uuid":server_uuid, "master_uuid":master_uuid, "uptime":uptime,
                "syncstatus":syncstatus, "binlogfile":binlogfile, "binlogpos":binlogpos, "sbm":sbm}

    def throughput(self, containerId, global_status, current_time):
        uptime = 0
        questions = 0
        reads = 0
        writes = 0
        com_rol = 0
        time_long = 0

        QPS = 0
        TPS = 0
        RPS = 0
        WPS = 0

        uptime = int(global_status.get("Uptime".lower()))
        questions = int(global_status.get("Questions".lower()))
        reads = int(global_status.get("Com_select".lower()))
        writes = int(global_status.get("Com_insert".lower())) + int(global_status.get("Com_update".lower())) + int(global_status.get("Com_delete".lower()))
        com_rol = int(global_status.get("com_commit".lower())) + int(global_status.get("com_rollback".lower()))

        #{containerid:{cachetime:time, cachemap:{variabels:{},global_status:{}}}}
        # containerId
        container_cache = self.status_cache.get(containerId)
        if container_cache == None:
            time_long = uptime
            QPS = round(questions/time_long * 1.0, 2)
            TPS = round(com_rol / time_long * 1.0, 2)
            RPS = round(reads / time_long * 1.0, 2)
            WPS = round(writes / time_long * 1.0, 2)
        else:
            time_long = current_time - int(container_cache.get("cachetime"))
            #print '<<<', questions, reads, writes, com_rol, time_long, '>>>'
            lst_global_status = container_cache.get("cachemap").get("global_status")
            lst_questions = int(lst_global_status.get("Questions".lower()))
            lst_reads = int(lst_global_status.get("Com_select".lower()))
            lst_writes = int(lst_global_status.get("Com_insert".lower())) + int(lst_global_status.get("Com_update".lower())) + int(
                lst_global_status.get("Com_delete".lower()))
            lst_com_rol = int(lst_global_status.get("com_commit".lower())) + int(lst_global_status.get("com_rollback".lower()))

            QPS = round((questions - lst_questions) * 1.0 / time_long, 2)
            TPS = round((com_rol - lst_com_rol) * 1.0 / time_long, 2)
            RPS = round((reads - lst_reads) * 1.0 / time_long, 2)
            WPS = round((writes - lst_writes) * 1.0 / time_long, 2)

        return {"qps":QPS,"tps":TPS, "rps":RPS, "wps":WPS}

    def connects(self, variables, global_status, sumConnectErrors):
        max_connections = 0
        threads_connected = 0
        max_connect_errors = 0
        sum_connect_errors = 0
        aborted_clients = 0
        aborted_connects = 0
        TCPR = 0
        ECPR = 0

        max_connections = int(variables.get("max_connections"))
        max_connect_errors = int(variables.get("max_connect_errors"))
        threads_connected = int(global_status.get("threads_connected"))
        aborted_clients = int(global_status.get("aborted_clients"))
        aborted_connects = int(global_status.get("aborted_connects"))
        sum_connect_errors = int(sumConnectErrors)

        TCPR = round(threads_connected/max_connections*100.0, 2)
        ECPR = round(sum_connect_errors/max_connect_errors*100.0, 2)

        return {"tcpr":TCPR, "ecpr":ECPR, "maxconnections": max_connections, "currentconnects":threads_connected,
                "abortedclients":aborted_clients, "abortedconnects":aborted_connects}

    def innodbs(self, containerId, global_status, current_time):
        uptime = 0
        innodb_buffer_pool_pages_free = 0
        innodb_buffer_pool_pages_total = 0
        innodb_buffer_pool_pages_data = 0
        innodb_buffer_pool_pages_dirty = 0
        innodb_row_lock_time = 0
        innodb_row_lock_current_waits = 0
        innodb_row_lock_waits = 0
        innodb_data_reads = 0
        innodb_data_writes = 0
        innodb_os_log_fsyncs = 0

        FPPR = 0
        DPPR = 0
        innodb_row_lock_time = 0
        innodb_row_lock_waits = 0

        uptime = int(global_status.get("Uptime".lower()))
        innodb_buffer_pool_pages_free = int(global_status.get("innodb_buffer_pool_pages_free"))
        innodb_buffer_pool_pages_total = int(global_status.get("innodb_buffer_pool_pages_total"))
        innodb_buffer_pool_pages_data = int(global_status.get("innodb_buffer_pool_pages_data"))
        innodb_buffer_pool_pages_dirty = int(global_status.get("innodb_buffer_pool_pages_dirty"))
        innodb_row_lock_time = int(global_status.get("innodb_row_lock_time"))
        innodb_row_lock_current_waits = int(global_status.get("innodb_row_lock_current_waits"))
        innodb_row_lock_waits = int(global_status.get("innodb_row_lock_waits"))
        innodb_data_reads = int(global_status.get("innodb_data_reads"))
        innodb_data_writes = int(global_status.get("innodb_data_writes"))
        innodb_os_log_fsyncs = int(global_status.get("innodb_os_log_fsyncs"))

        FPPR = round((innodb_buffer_pool_pages_free / innodb_buffer_pool_pages_total) * 100.0, 2)
        DPPR = round((innodb_buffer_pool_pages_dirty / innodb_buffer_pool_pages_total) * 100.0, 2)

        # {containerid:{cachetime:time, cachemap:{variabels:{},global_status:{}}}}
        # containerId
        container_cache = self.status_cache.get(containerId)
        if container_cache == None:
            time_long = uptime

            innodb_row_lock_time = round(innodb_row_lock_time * 1.0 / time_long, 2)
            innodb_row_lock_waits = round(innodb_row_lock_waits * 1.0 / time_long, 2)
            innodb_data_reads = round(innodb_data_reads * 1.0 / time_long, 2)
            innodb_data_writes = round(innodb_data_writes * 1.0 / time_long, 2)
            innodb_os_log_fsyncs = round(innodb_os_log_fsyncs * 1.0 / time_long, 2)

        else:
            time_long = current_time - int(container_cache.get("cachetime"))
            # print '----', innodb_row_lock_time, innodb_row_lock_waits, innodb_data_reads, innodb_data_writes, innodb_os_log_fsyncs,time_long,'----'
            lst_global_status = container_cache.get("cachemap").get("global_status")
            lst_innodb_row_lock_time = int(lst_global_status.get("innodb_row_lock_time".lower()))
            lst_innodb_row_lock_waits = int(lst_global_status.get("innodb_row_lock_waits".lower()))
            lst_innodb_data_reads = int(lst_global_status.get("innodb_data_reads".lower()))
            lst_innodb_data_writes = int(lst_global_status.get("innodb_data_writes".lower()))
            lst_innodb_os_log_fsyncs = int(lst_global_status.get("innodb_os_log_fsyncs".lower()))

            innodb_row_lock_time = round((innodb_row_lock_time - lst_innodb_row_lock_time) * 1.0 / time_long, 2)
            innodb_row_lock_waits = round((innodb_row_lock_waits - lst_innodb_row_lock_waits) * 1.0 / time_long, 2)
            innodb_data_reads = round((innodb_data_reads - lst_innodb_data_reads) * 1.0 / time_long, 2)
            innodb_data_writes = round((innodb_data_writes - lst_innodb_data_writes) * 1.0 / time_long, 2)
            innodb_os_log_fsyncs = round((innodb_os_log_fsyncs - lst_innodb_os_log_fsyncs) * 1.0 / time_long, 2)

        return {"fppr": FPPR, "dppr": DPPR, "innodb_row_lock_time": innodb_row_lock_time,
                "innodb_row_lock_waits": innodb_row_lock_waits, "innodb_data_reads": innodb_data_reads,
                "innodb_data_writes": innodb_data_writes, "innodb_os_log_fsyncs": innodb_os_log_fsyncs}

    def cursor(self, containerId, variables, global_status, current_time):
        uptime = 0
        open_tables = 0
        opened_tables = 0
        open_files = 0
        opened_files = 0

        table_open_cache = 0
        open_files_limit = 0

        OTR = 0
        OFR = 0

        uptime = int(global_status.get("Uptime".lower()))
        open_tables = int(global_status.get("open_tables"))
        opened_tables = int(global_status.get("opened_tables"))
        open_files = int(global_status.get("open_files"))
        opened_files = int(global_status.get("opened_files"))

        table_open_cache = int(variables.get("table_open_cache"))
        open_files_limit = int(variables.get("open_files_limit"))

        OTR = round((open_tables / table_open_cache) * 100.0, 2)
        OFR = round((open_files / open_files_limit) * 100.0, 2)


        # {containerid:{cachetime:time, cachemap:{variabels:{},global_status:{}}}}
        # containerId
        container_cache = self.status_cache.get(containerId)
        if container_cache == None:
            time_long = uptime

            opened_tables = round(opened_tables * 1.0 / time_long, 2)
            opened_files = round(opened_files * 1.0 / time_long, 2)

        else:
            time_long = current_time - int(container_cache.get("cachetime"))
            #print '----', innodb_row_lock_time, innodb_row_lock_waits, innodb_data_reads, innodb_data_writes, innodb_os_log_fsyncs, time_long, '----'
            lst_global_status = container_cache.get("cachemap").get("global_status")
            lst_opened_tables = int(lst_global_status.get("opened_tables".lower()))
            lst_opened_files = int(lst_global_status.get("opened_files".lower()))

            opened_tables = round((opened_tables - lst_opened_tables) * 1.0 / time_long, 2)
            opened_files = round((opened_files - lst_opened_files) * 1.0 / time_long, 2)

        return {"otr": OTR, "ofr": OFR, "opened_tables": opened_tables, "opened_files": opened_files}


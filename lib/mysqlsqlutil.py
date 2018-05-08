#*************************************
#author:zhengqs
#create:201710
#desc: 
#**********************************

import os,sys
from command import Command

class MysqlSqlUtil:
    
    def __init__(self):
        pass
    
    @staticmethod
    def getVariablesSql(variable_names=None):
        if not variable_names:
            sql = 'show variables\G'
        else:
            sql = "show variables where variable_name in ('"+"','".join(variable_names)+"')\G"
        return sql
    
    @staticmethod
    def analysisVariablesResult(sqlres):
        rows = sqlres.split("\r\n")
        column_name = None
        column_value = None
        variables = {}
        for row in rows:
            if row.find("Using a password on the command")>0:
                continue
            coloumns = row.split(":")
            if len(coloumns) != 2:
                continue
            coloumns[0] = coloumns[0].strip().lower()
            coloumns[1] = coloumns[1].strip().lower()
            
            if coloumns[0] == 'variable_name':
                column_name = coloumns[1].strip().lower()
            elif coloumns[0] == 'value':
                column_value = coloumns[1].strip()
                variables[column_name] = column_value
        return variables
        
    @staticmethod
    def getGlobalStatusSql(variable_names=None):
        sql = 'show global status\G'
        if not variable_names:
            sql = 'show global status\G'
        else:
            sql = "show global status where variable_name in ('"+"','".join(variable_names)+"')\G"
        return sql
    
    @staticmethod
    def getMasterStatusSql():
        sql = 'show master status\G'
        return sql
    
    @staticmethod
    def getSlaveStatusSql():
        sql = 'show slave status\G'
        return sql
    
    @staticmethod
    def getSumConnectErrorsSql():
        sql = 'select sum_connect_errors from performance_schema.host_cache order by sum_connect_errors desc limit 1\G'
        return sql
    
    @staticmethod
    def analysisKeyValueResult(sqlres):
        rows = sqlres.split("\r\n")        
        column_row = None
        row_list = []
        for row in rows:
            if row.find("Using a password on the command")>0:
                continue
            if row.find(". row **********")>0:
                if column_row:
                    row_list.append(column_row)
                column_row = {}   
            else:
                coloumns = row.split(":", 1)
                if len(coloumns) != 2:
                    continue
                column_row[coloumns[0].lower().strip()] = coloumns[1].strip()
                
        if column_row:
            row_list.append(column_row)
            
        return row_list

if __name__=='__main__':
    sql = MysqlSqlUtil.getSumConnectErrorsSql()
    cmd = Command()
    print 'docker exec -t 9b9be16761fa mysql -uroot -pzc53vvzj -e \"'+sql+'\"'
    code, res = cmd.subprocess_popen('docker exec -t 9b9be16761fa mysql -uroot -pzc53vvzj -e \"'+sql+'\"', timeout=30)
    if code == 0:
        print MysqlSqlUtil.analysisKeyValueResult(res)
    else:
        print 'exec sql error: '+res

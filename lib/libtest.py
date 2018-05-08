from dockerutil import DockerUtil
from hostutil import Host
import json
import os
import sys
import time

#if os.path.exists('/.dockerinit'):
#    os.chroot("/rootfs")
    
aa = DockerUtil()
dockerInfo = aa.getDockerPs(['status=running','env=CAMEL_MONGODB_LABEL_DATAPATH=/data/mongo/055e8476b83f49b994d7d6cad126bd05'])

print json.dumps(dockerInfo)
time0 = time.time()
ids = ""
for info in dockerInfo:
    ids +=" "+info['Id']
    
dockerInfo = aa.getDockerStats(ids)
time1 = time.time()
print json.dumps(dockerInfo)

#time.sleep(2)

dockerInfo2 = aa.getDockerStats(ids)
time2 = time.time()
print json.dumps(dockerInfo2)
print time1, time2, time0
timelong = time2 - time0
print timelong,(time1-time0)> 0

netin1 = dockerInfo[0]['netin']
netin2 = dockerInfo2[0]['netin']



#dockerInfo = aa.truncatDockerLogFile('b083408e6bfe')
#dockerInfo = aa.getDockerExec('eae9b7f34f4','ls / -l')

#print json.dumps(dockerInfo)
#print dockerInfo

#cpuinfo = SystemStat.get_cpuinfo_stat()
#print json.dumps(cpuinfo)

#cpuinfo = SystemStat.get_cpu_rate()
#print json.dumps(cpuinfo)

#info = Host.uname()

#info = Host.getHostname()
#print info
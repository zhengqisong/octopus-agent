#!/usr/bin/python
# -*- coding: UTF-8 -*-
# *************************************
# author:zhengqs
# create:201410
# desc: sysmonitor util

import os
import platform
import time
import re
import logging
import commands
from command import Command


class SystemStat(object):
    # cpu统计信息,processor：核序号，physical id物理cpu序号，cpu MHz主频，model name型号
    @staticmethod
    def get_cpuinfo_stat():
        cpu = []
        cpuinfo = {}
        f = open("/proc/cpuinfo")
        lines = f.readlines()
        f.close()

        for line in lines:
            if line == '\n':
                cpu.append(cpuinfo)
                cpuinfo = {}
            if len(line) < 2: continue
            name = line.split(':')[0].rstrip()
            var = line.split(':')[1]
            cpuinfo[name] = var.strip()
        return cpu

    # cpu负载统计
    @staticmethod
    def get_load_stat():
        loadavg = {}
        f = open("/proc/loadavg")
        con = f.read().split()
        f.close()
        # 1、5、15分钟内的平均进程数
        loadavg['lavg_1'] = con[0]
        loadavg['lavg_5'] = con[1]
        loadavg['lavg_15'] = con[2]
        # 正在运行的进程/总进程数
        loadavg['nr'] = con[3]
        # 最后一次运行的进程ID
        loadavg['last_pid'] = con[4]
        return loadavg

    # 时间统计,运行时间day，hour，minute，second，空闲率freeRate
    @staticmethod
    def get_uptime_stat():
        uptime = {}
        f = open("/proc/uptime")
        con = f.read().split()
        f.close()

        all_sec = float(con[0])
        MINUTE, HOUR, DAY = 60, 3600, 86400
        uptime['day'] = int(all_sec / DAY)
        uptime['hour'] = int((all_sec % DAY) / HOUR)
        uptime['minute'] = int((all_sec % HOUR) / MINUTE)
        uptime['second'] = int(all_sec % MINUTE)
        uptime['runTime'] = all_sec
        # uptime['Free rate'] = float(con[1]) / float(con[0])

        cpus = os.popen('cat /proc/cpuinfo |grep processor|wc -l', 'r').readlines()
        uptime['freeRate'] = round(float(con[1]) * 100 / ((float(con[0])) * float(cpus[0])), 2)

        return uptime

    # 磁盘列表
    @staticmethod
    def disk_partitions(all=False):
        phydevs = []
        f = open("/proc/filesystems", "r")
        for line in f:
            if not line.startswith("nodev"):
                phydevs.append(line.strip())

        retlist = []
        f = open('%s/etc/fstab' % SystemInfo.getRootfs(), "r")
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue

            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phydevs:
                continue
            if device == 'none':
                device = ''

            disk = dict(
                zip(
                    ('device', 'mountpoint', 'fstype'),
                    (device, mountpoint, fstype)
                )
            )
            retlist.append(disk)
        return retlist

        # 指定磁盘的使用率

    @staticmethod
    def disk_usage(path):
        """
        Return disk usage associated with path.
        @path mountpoint,eg:/home,通过disk_partitions查询出来的挂载点
        """
        st = os.statvfs("%s%s" % (SystemInfo.getRootfs(), path))
        free = (st.f_bavail * st.f_frsize)
        total = (st.f_blocks * st.f_frsize)
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        try:
            percent = ret = (float(used) / total) * 100
        except ZeroDivisionError:
            percent = 0
            # NB: the percentage is -5% than what shown by df due to
        # reserved blocks that we are currently not considering:
        # http://goo.gl/sWGbH
        disk = dict(
            zip(
                ('totalSize', 'usedSize', 'freeSize', 'usedRate'),
                (total, used, free, "%.2f" % percent)
            )
        )
        return disk

    # 磁盘使用情况
    @staticmethod
    def get_disk_stat():
        disks = []
        partitions_list = SystemStat.disk_partitions()
        for partition in partitions_list:
            usage = SystemStat.disk_usage(partition['mountpoint'])
            disks.append(
                {"device": partition['device'], "mountpoint": partition['mountpoint'], "fstype": partition['fstype']
                    , "totalSize": usage['totalSize'], "usedSize": usage['usedSize'], "freeSize": usage['freeSize'],
                 "usedRate": usage['usedRate']})

        return disks

    # 内存使用统计
    @staticmethod
    def get_memory_stat():
        mem = {}
        f = open("/proc/meminfo")
        lines = f.readlines()
        f.close()

        for line in lines:
            if len(line) < 2: continue
            name = line.split(':')[0]
            var = line.split(':')[1].split()[0]
            mem[name] = long(var) * 1024.0
        mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
        mem['MemUsedPerc'] = round((100 * mem['MemUsed']) / mem['MemTotal'], 2)
        return mem

    # cpu运行状态统计
    @staticmethod
    def cpu_stat(cpu_name=None):
        cpus = []
        f = open("/proc/stat")
        lines = f.readlines()
        f.close()

        for line in lines:
            if 'cpu' not in line:
                continue

            cpu = {}
            con = line.split()
            if len(con) == 8:
                cpu = dict(
                    zip(
                        ('cpu', 'user', 'nice', 'sys', 'idle', 'iowait', 'irq', 'softirq', 'stealstolen', 'guest'),
                        (con[0], long(con[1]), long(con[2]), long(con[3]), long(con[4]), long(con[5]), long(con[6]),
                         long(con[7]), long(0), long(0))
                    )
                )
            else:
                cpu = dict(
                    zip(
                        ('cpu', 'user', 'nice', 'sys', 'idle', 'iowait', 'irq', 'softirq', 'stealstolen', 'guest'),
                        (con[0], long(con[1]), long(con[2]), long(con[3]), long(con[4]), long(con[5]), long(con[6]),
                         long(con[7]), long(con[8]), long(con[9]))
                    )
                )
            if cpu_name not in (None, '') and cpu_name == cpu['cpu']:
                return cpu
            cpus.append(cpu)
        return cpus

    # cpu使用率cpu1是第一次读取的cpu信息，cpu2是第二次读取的cpu信息
    @staticmethod
    def cpu_rate(cpu1, cpu2):
        if len(cpu1) != 10:
            return -1
        dlta_user_cpu = cpu2['user'] - cpu1['user']
        dlta_nice_cpu = cpu2['nice'] - cpu1['nice']
        dlta_sys_cpu = cpu2['sys'] - cpu1['sys']
        dlta_idle_cpu = cpu2['idle'] - cpu1['idle']
        dlta_iowait_cpu = cpu2['iowait'] - cpu1['iowait']
        dlta_irq_cpu = cpu2['irq'] - cpu1['irq']
        dlta_softirq_cpu = cpu2['softirq'] - cpu1['softirq']
        dlta_stealstolen_cpu = cpu2['stealstolen'] - cpu1['stealstolen']
        dlta_guest_cpu = cpu2['guest'] - cpu1['guest']
        sum = dlta_user_cpu + dlta_nice_cpu + dlta_sys_cpu + dlta_idle_cpu + dlta_iowait_cpu + dlta_irq_cpu + dlta_softirq_cpu + dlta_stealstolen_cpu + dlta_guest_cpu
        cpu_now_used = float(sum - dlta_idle_cpu) * 100 / float(sum)
        return round(cpu_now_used, 2)

    # 获取cpu使用率
    @staticmethod
    def get_cpu_rate(cpu_name='cpu', interval_time=0.5):
        cpu1 = SystemStat.cpu_stat(cpu_name)
        time.sleep(interval_time)
        cpu2 = SystemStat.cpu_stat(cpu_name)
        return SystemStat.cpu_rate(cpu1, cpu2)

    # 网卡流量
    @staticmethod
    def get_net_rate(ifname):
        if not ifname:
            return None

        net1 = SystemInfo.networkinfo(ifname)
        time.sleep(1)
        net2 = SystemInfo.networkinfo(ifname)

        netRate = {}
        netRate['interface'] = ifname
        netRate['rate'] = ((net2['rxBytes'] - net2['rxBytes']) + (net2['txBytes'] - net1['txBytes'])) * 8

        return netRate

    # 目录大小统计
    @staticmethod
    def get_path_du(path):
        (status, lines) = commands.getstatusoutput("du -s %s%s|awk '{print $1}'" % (SystemInfo.getRootfs(), path))
        if status != 0:
            raise Exception(lines)

        return long(lines.strip())


class SystemInfo(object):
    def __init__(self):
        pass

    # 判断是否在容器中
    @staticmethod
    def getRootfs():
        if SystemInfo.isInContainer():
            return '/rootfs'
        else:
            return ''

    # 判断是否在容器中
    @staticmethod
    def isInContainer():
        return os.path.exists('/.dockerinit')

    # 越狱到rootfs
    @staticmethod
    def chrootfs(rootfs):
        os.chroot(rootfs)

        # 读取主机名称

    @staticmethod
    def getHostname():
        f = open("%s/etc/hostname" % SystemInfo.getRootfs())
        lines = f.read()
        f.close()
        return lines.strip()

    # 读取主机信息
    @staticmethod
    def uname():
        uname_ary = platform.uname()
        uname = {}
        uname = dict(
            zip(
                ('system', 'node', 'release',
                 'version', 'machine', 'processor'),
                uname_ary
            )
        )
        return uname

    # 获取网卡列表
    @staticmethod
    def network_list():
        net = []
        (status, lines) = commands.getstatusoutput("ls %s/sys/class/net/ -l|awk '{print $9}'" % SystemInfo.getRootfs())
        if status != 0:
            raise Exception(lines)

        lines = lines.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith("docker") or line.startswith("loopback") or line.startswith("veth"):
                continue
            net.append(line)

        return net

    # 读取指定网口信息
    @staticmethod
    def networkinfo(ifname):
        network = {"name": ifname, "status": "down", "rxBytes": 0, "txBytes": 0, "rxPackets": 0, "txPackets": 0}
        file_object = open("%s/sys/class/net/%s/operstate" % (SystemInfo.getRootfs(), ifname))
        try:
            network['status'] = file_object.read().strip()
        finally:
            file_object.close()

        file_object = open("%s/sys/class/net/%s/statistics/rx_bytes" % (SystemInfo.getRootfs(), ifname))
        try:
            network['rxBytes'] = long(file_object.read().strip())
        finally:
            file_object.close()

        file_object = open("%s/sys/class/net/%s/statistics/tx_bytes" % (SystemInfo.getRootfs(), ifname))
        try:
            network['txBytes'] = long(file_object.read().strip())
        finally:
            file_object.close()

        file_object = open("%s/sys/class/net/%s/statistics/rx_packets" % (SystemInfo.getRootfs(), ifname))
        try:
            network['rxPackets'] = long(file_object.read().strip())
        finally:
            file_object.close()

        file_object = open("%s/sys/class/net/%s/statistics/tx_packets" % (SystemInfo.getRootfs(), ifname))
        try:
            network['txPackets'] = long(file_object.read().strip())
        finally:
            file_object.close()

        return network

    # 读取指定网口信息
    @staticmethod
    def processList():
        #        net = []
        command = "ps -e -o user,pid,ppid,stime,pcpu,pmem,rss,vsz,stat,time,comm"
        #        command = "ps -e -o user,pid,ppid,stime,pcpu,pmem,rss,vsz,stat,time,comm|awk '{print \$1,\$2,\$3,\$4,\$5,\$6,\$7,\$8,\$9,\$10,\$11}'"
        #        (status,lines) = commands.getstatusoutput("" % command)
        #        if status != 0:
        #            raise Exception(lines)
        #
        res = []
        message = SystemInfo.exec_command(command)
        lines = message["res"]
        lines = lines.split('\n')
        for line in lines:
            line = line.split(None, 10)
            res.append(line)
        return res

    @staticmethod
    def exec_command(command, timeout=50):
        # command = command.replace("$","\$")
        cmd = Command()
        if SystemInfo.isInContainer():
            # (status,lines) = commands.getstatusoutput('python %s/command.pyc %s "%s"' % (os.path.dirname(os.path.realpath(__file__)), SystemInfo.getRootfs(), command))
            (status, lines) = cmd.subprocess_popen('python %s/command.pyc %s "%s" %d' % (
            os.path.dirname(os.path.realpath(__file__)), SystemInfo.getRootfs(), command, timeout), timeout=timeout)

        else:
            (status, lines) = cmd.subprocess_popen(command, timeout=timeout)
        if status != 0:
            raise Exception(lines)

        return {"command": command, "res": lines}


class Host(SystemStat, SystemInfo):
    def __init__(self):
        pass
# -*- coding: UTF-8 -*-
# *************************************
# author:zhengqs
# create:201707
# desc:
# **********************************

import os, sys
import datetime
import time
import commands
import re
import json

from command import Command
from hostutil import Host


class DockerUtil:
    def __init__(self):
        self.docker = 'docker'
        self.rootfs = Host.getRootfs()

    def __to_kb(self, value):
        ''
        try:
            value = value.upper();
            if value.endswith("MB"):
                value = float(value.replace("MB", '')) * 1024
            if value.endswith("MIB"):
                value = float(value.replace("MIB", '')) * 1000
            elif value.endswith("GB"):
                value = float(value.replace("GB", '')) * 1024 * 1024
            elif value.endswith("GIB"):
                value = float(value.replace("GIB", '')) * 1000 * 1000
            elif value.endswith("KB"):
                value = float(value.replace("KB", ''))
            elif value.endswith("KIB"):
                value = float(value.replace("KIB", ''))
            elif value.endswith("B"):
                value = float(value.replace("B", '')) / 1024
            else:
                return value

            return round(float(value), 2)
        except:
            return 0

    # show docker version
    def getDockerVerion(self):
        (status, lines) = commands.getstatusoutput("%s -v" % self.docker)
        if status != 0:
            raise Exception(lines)
        return lines

    # show docker version [1,10,1]
    def getDockerVerionAry(self):
        lines = self.getDockerVerion()
        (major, version, number) = re.findall(r"(\d+)\.(\d+)\.(\d+)", lines)[0]
        return (int(major), int(version), int(number))

    # check docker version >= version
    def isAfterDockerVerion(self, f_version):
        (major, version, number) = self.getDockerVerionAry()
        (v_major, v_version, v_number) = re.findall(r"(\d+)\.(\d+)\.(\d+)", f_version)[0]
        (v_major, v_version, v_number) = (int(v_major), int(v_version), int(v_number))

        if major > v_major or (major == v_major and version > v_version) or (
                    major == v_major and version == v_version and number >= v_number):
            return True

        return False

    # show docker info
    def getDockerInfo(self):
        (status, lines) = commands.getstatusoutput("%s info" % self.docker)
        if status != 0:
            raise Exception(lines)
        lines = lines.split('\n')
        dockerInfo = {}
        for line in lines:
            ary = line.split(':', 1)
            if len(ary) != 2:
                continue
            dockerInfo[ary[0].strip()] = ary[1].strip()
        dockerInfo['Pool Blocksize'] = self.__to_kb(dockerInfo.get('Pool Blocksize'))
        dockerInfo['Data Space Used'] = self.__to_kb(dockerInfo.get('Data Space Used'))
        dockerInfo['Data Space Total'] = self.__to_kb(dockerInfo.get('Data Space Total'))
        dockerInfo['Data Space Available'] = self.__to_kb(dockerInfo.get('Data Space Available'))
        dockerInfo['Metadata Space Used'] = self.__to_kb(dockerInfo.get('Metadata Space Used'))
        dockerInfo['Metadata Space Total'] = self.__to_kb(dockerInfo.get('Metadata Space Total'))
        dockerInfo['Metadata Space Available'] = self.__to_kb(dockerInfo.get('Metadata Space Available'))
        dockerInfo['Total Memory'] = self.__to_kb(dockerInfo.get('Total Memory'))
        dockerInfo['Base Device Size'] = self.__to_kb(dockerInfo.get('Base Device Size'))
        dockerInfo['CPUs'] = int(dockerInfo.get('CPUs'))

        return dockerInfo

    # inspect image or container
    def getDockerInspect(self, inspectId):
        (status, lines) = commands.getstatusoutput("%s inspect %s" % (self.docker, inspectId))
        if status != 0:
            return None

        imageInfo = json.loads(lines)
        if not imageInfo:
            return imageInfo
        return imageInfo[0]

    # get docker images
    def getDockerImages(self):
        (status, lines) = commands.getstatusoutput("%s images --no-trunc -q" % self.docker)
        if status != 0:
            raise Exception(lines)
        lines = lines.split('\n')
        dockerImage = []
        if len(lines) < 0:
            return dockerImage;

        lines = list(set(lines))
        lines = ' '.join(lines)
        (status, lines) = commands.getstatusoutput(
            "%s inspect --format='{{.Id}}\t{{json .RepoTags}}\t{{.VirtualSize}}\t{{.Created}}' %s" % (
            self.docker, lines))

        if status != 0:
            raise Exception(lines)

        lines = lines.split('\n')

        for imageInfo in lines:
            imageInfo = imageInfo.split('\t')

            imageId = imageInfo[0]
            repoTags = imageInfo[1]
            virtualSize = float(imageInfo[2])
            created = imageInfo[3];

            repoTags = json.loads(repoTags)
            if len(repoTags) == 0:
                dockerImage.append({"imageId": imageId, "name": "", "created": created, "virtualSize": virtualSize})
            else:
                for name in repoTags:
                    dockerImage.append(
                        {"imageId": imageId, "name": name, "created": created, "virtualSize": virtualSize})

        return dockerImage

    # stats container resource
    # id uses a space partition
    def getDockerStats(self, ids):
        dockerStats = []
        if not ids:
            return dockerStats
        (status, lines) = commands.getstatusoutput(
            "%s stats --no-stream=True %s| sed 's?/? / ?g' | awk '{print $1,$2,$8,$9$10,$12$13,$14$15,$17$18}'" % (
            self.docker, ids))

        if status != 0:
            raise Exception(lines)

        lines = lines.split('\n')

        if len(lines) < 0:
            return dockerStats

        for line in lines:
            statInfo = line.split()
            if statInfo[0] == 'CONTAINER':
                continue
            if len(statInfo) < 5:
                continue
            if len(statInfo) == 5:
                statInfo.append('0B')
                statInfo.append('0B')

            # 处理各个字段
            # statInfo={id,cpu,mem,netin,netout,blockin,blockout}
            statInfo[1] = float(statInfo[1].replace('%', ''))
            statInfo[2] = float(statInfo[2].replace('%', ''))
            statInfo[3] = self.__to_kb(statInfo[3])
            statInfo[4] = self.__to_kb(statInfo[4])
            statInfo[5] = self.__to_kb(statInfo[5])
            statInfo[6] = self.__to_kb(statInfo[6])
            dockerStats.append(
                {"id": statInfo[0], "cpu": statInfo[1], "mem": statInfo[2], "netin": statInfo[3], "netout": statInfo[4],
                 "blockin": statInfo[5], "blockout": statInfo[6]})
        return dockerStats

    # ps inspect some column info
    def getDockerPsInspect(self, ids):
        flag = False
        if self.isAfterDockerVerion('1.9.1'):
            (status, lines) = commands.getstatusoutput(
                "%s inspect --format='{{.Id}}\t{{.Name}}\t{{.State.Status}}\t{{.Created}}\t{{.Image}}\t{{.Config.Image}}\t{{json .Config.Env}}\t{{json .Mounts}}\t{{.LogPath}}\t{{.HostConfig.NetworkMode}}\t{{json .HostConfig.PortBindings}}\t{{json .Config.Labels}}' %s" % (
                self.docker, ids))
        else:
            flag = True
            (status, lines) = commands.getstatusoutput(
                "%s inspect --format='{{.Id}}\t{{.Name}}\t{{.State.Running}}\t{{.Created}}\t{{.Image}}\t{{.Config.Image}}\t{{json .Config.Env}}\t[]\t{{.LogPath}}\t{{.HostConfig.NetworkMode}}\t{{json .HostConfig.PortBindings}}\t{{json .Config.Labels}}' %s" % (
                self.docker, ids))

        if status != 0:
            raise Exception(lines)
        lines = lines.split('\n')
        containerList = []
        for line in lines:
            containerInfo = line.split('\t')
            cId = containerInfo[0]
            name = containerInfo[1][1:]
            status = containerInfo[2]
            created = containerInfo[3]
            imageId = containerInfo[4]
            imageName = containerInfo[5]
            envs = containerInfo[6]
            mounts = containerInfo[7]
            logPath = containerInfo[8]
            networkMode = containerInfo[9]
            portBindings = containerInfo[10]
            labels = containerInfo[11]

            if flag == True:
                if not status:
                    status = "";
                if status.lower() == 'true':
                    status = 'running'
                else:
                    status = 'exited'

            try:
                envs = json.loads(envs)
                if not envs:
                    envs = {}
                else:
                    envs_ary_tmp = {}
                    for env in envs:
                        env_ary = env.split('=', 1)
                        env_key = env_ary[0];
                        env_val = '';
                        if len(env_ary) == 2:
                            env_val = env_ary[1]
                        envs_ary_tmp[env_key.strip()] = env_val.strip()
                    envs = envs_ary_tmp
            except:
                envs = []

            try:
                mounts = json.loads(mounts)
                if not mounts:
                    mounts = []
            except:
                mounts = []

            try:
                portBindings = json.loads(portBindings)
                if not portBindings:
                    portBindings = {}
            except:
                portBindings = {}

            try:
                labels = json.loads(labels)
                if not labels:
                    labels = {}
            except:
                labels = {}

            containerList.append({"Id": cId, "name": name, "status": status, "created": created, "imageId": imageId,
                                  "imageName": imageName, "envs": envs, "mounts": mounts, "logPath": logPath,
                                  "networkMode": networkMode, "portBindings": portBindings, "labels": labels})
        return containerList

    # ps container
    # filters[]
    #  - status=(created|restarting|running|paused|exited)
    #  - label=<key> or label=<key>=<value>
    #  - ancestor=(<image-name>[:tag])
    #  - env=<key> or env=<key>=<value>
    def getDockerPs(self, filters=None):
        filter_str = '';
        filter_ary = []
        if filters:
            for f in filters:

                _type = f.split('=', 1)[0].strip()
                if _type == 'status' or _type == 'label':
                    filter_str += " -f '%s'" % f
                else:
                    filter_ary.append({"type": _type, "value": f.split('=', 1)[1]})

        (status, lines) = commands.getstatusoutput("%s ps --no-trunc -q %s" % (self.docker, filter_str))

        if status != 0:
            raise Exception(lines)
        lines = lines.split('\n')
        dockerImage = []

        if len(lines) <= 0:
            return dockerImage;

        lines = list(set(lines))
        lines = ' '.join(lines)
        if lines.strip() == '':
            return dockerImage
        containerList = self.getDockerPsInspect(lines)
        resContainerList = []
        if len(filter_ary) < 1:
            resContainerList = containerList
        else:
            for container in containerList:
                flag = True
                for f in filter_ary:
                    _type = f['type']
                    _value = f['value']
                    if _type == 'env':
                        env_tmp = _value.split('=', 1)
                        if not container['envs']:
                            flag = False
                            break
                        if len(env_tmp) == 1 and env_tmp[0].strip() not in container['envs'].keys():
                            flag = False
                            break
                        if len(env_tmp) == 2 and env_tmp[1].strip() != container['envs'].get(env_tmp[0].strip()):
                            flag = False
                            break
                    elif _type == 'ancestor':
                        imageName = container['imageName']
                        imgeRes = ''
                        if imageName.find('/') > 0:
                            imgeRes = imageName.split('/', 1)[0]
                            imageName = imageName.split('/', 1)[1]
                        imageTag = imageName
                        imageVer = 'latest'

                        if imageName.find(':') > 0:
                            imageTag = imageName.split(':', 1)[0]
                            imageVer = imageName.split(':', 1)[1]

                        findRes = ''
                        if _value.find('/') > 0:
                            findRes = _value.split('/', 1)[0]
                            _value = _value.split('/', 1)[1]

                        findTag = _value
                        findVer = ''

                        if _value.find(':') > 0:
                            findTag = _value.split(':', 1)[0]
                            findVer = _value.split(':', 1)[1]

                        if findRes and imgeRes and findRes != imgeRes:
                            flag = False
                            break

                        if imageTag != findTag:
                            flag = False
                            break

                        if findVer and findVer != imageVer:
                            flag = False
                            break

                if flag == True:
                    resContainerList.append(container)

        return resContainerList

    # show container logs
    def getDockerLogs(self, container, num):
        if not num or num < 1 or num > 500:
            num = 500
        (status, lines) = commands.getstatusoutput("%s logs --tail=%d %s" % (self.docker, num, container))
        if status != 0:
            raise Exception(lines)
        return lines

    # exec command in container
    def getDockerExec(self, container, cmd, timeout=50):
        # (status,lines) = commands.getstatusoutput("%s exec -t %s %s" % (self.docker, container, cmd))
        commd = Command()

        (status, lines) = commd.subprocess_popen("%s exec -t %s %s" % (self.docker, container, cmd), timeout=timeout)
        if status != 0:
            raise Exception(lines)
        return lines

    # truncat container log file, support mesos and docker log
    def truncatDockerLogFile(self, container):
        containerList = self.getDockerPsInspect(container)
        if not containerList or len(containerList) != 1:
            raise Exception('container(%s) invalid' % container)

        containerInfo = containerList[0]
        logPath = containerInfo.get('logPath')
        mounts = containerInfo.get('mounts')

        # truncat docker logPath file
        cmd = "";
        if logPath:
            cmd += ";cat /dev/null >%s%s" % (self.rootfs, logPath)

            # (status,lines) = commands.getstatusoutput("cat /dev/null >%s" % logPath)
            # if status != 0:
            #    raise Exception(lines)

        if mounts and len(mounts) > 0:
            for mount in mounts:
                if "/mnt/mesos/sandbox" == mount.get("Destination"):
                    cmd += ";cat /dev/null >%s%s/stderr" % (self.rootfs, mount.get("Source"))
                    cmd += ";cat /dev/null >%s%s/stdout" % (self.rootfs, mount.get("Source"))

                    # (status,lines) = commands.getstatusoutput("cat /dev/null >%s/stderr" % mount.get("Source"))
                    # if status != 0:
                    #    raise Exception(lines)
                    # (status,lines) = commands.getstatusoutput("cat /dev/null >%s/stdout" % mount.get("Source"))
                    # if status != 0:
                    #    raise Exception(lines)
        if cmd:
            (status, lines) = commands.getstatusoutput(cmd[1:])
            if status != 0:
                raise Exception(lines)
        return 'ok'

    def listDockerDanglingVolumn(self):
        (status, lines) = commands.getstatusoutput("%s volume ls -qf dangling=true" % self.docker)
        if status != 0:
            raise Exception(lines)
        if not lines and len(lines) > 0:
            lines = lines.split("\n")
        else:
            lines = []
        return lines

    # rm dangling volumn(批量删除孤单的volumes)
    def rmDockerDanglingVolumn(self):
        v_lt = self.listDockerDanglingVolumn()
        if not v_lt:
            return 'ok'
        (status, lines) = commands.getstatusoutput(
            "%s volume rm $(%s volume ls -qf dangling=true)" % (self.docker, self.docker))
        if status != 0:
            raise Exception(lines)
        return 'ok'


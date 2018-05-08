#!/usr/bin/python
# -*- coding: UTF-8 -*-
# *************************************
# author:zhengqs
# create:201708
# desc:
# ***********************************

import os
import sys
import time
import commands
from subprocess import Popen, PIPE, STDOUT


class Command(object):
    # 采用commands执行命令
    @staticmethod
    def command(command):
        retcode, output = commands.getstatusoutput(command)
        return retcode, output

    # 采用subprocess执行命令
    @staticmethod
    def subprocess_popen(command, shell=True, cwd=None, sync=True, timeout=None):
        if not sync:
            process = Popen(command, shell=True, cwd=cwd)
            return (0, '')

        p = Popen(command, shell=shell, stdout=PIPE, stderr=PIPE, cwd=cwd)
        t_beginning = time.time()
        seconds_passed = 0
        while True:
            if p.poll() is not None:
                res = p.communicate()
                exitcode = p.poll() if p.poll() else 0
                if exitcode == 0:
                    return exitcode, res[0]
                else:
                    return exitcode, res[1] + res[0]
            seconds_passed = (time.time() - t_beginning)
            if timeout and seconds_passed > int(timeout):
                p.terminate()
                exitcode, err = 128, 'exec command error'
                return exitcode, err
            time.sleep(0.1)

if __name__ == '__main__':
    argv = sys.argv
    # 越狱到主机
    os.chroot(argv[1])
    # (status,lines) = commands.getstatusoutput(argv[2])
    # if status != 0:
    #    raise Exception(lines)
    # print lines

    cmd = Command()
    status, message = cmd.subprocess_popen(argv[2], timeout=argv[3])
    if status != 0:
        sys.stderr.write(message)
    else:
        sys.stdout.write(message)

    exit(status)

Short Description
=================
````
Octopus agent is a application that is used to collect containers, hosts, such as CPU, MEM, disk, net, diskio, and external API.
````

Full Description
================

##主机部署模式
直接程序部署主机上，部署方式

````
tar zxvf octopus-agent.tar.gz
mkdir /opt/modules
mv octopus-agent /opt/modules/
````
###scheduler.json
配置scheduler.json文件

###octopus.conf
修改配置/opt/modules/octopus-agent/conf/octopus.conf文件

###启动程序
需要python2.7.5版本，需要安装python的组件Flask，Flask-APScheduler，ipaddr，安装方法pip install Flask
····
python /opt/modules/octopus-agent/run.py
····

##docker 容器模式

### 安装octopus-agent镜像
````
docker load -i octopus-agent-image-0.01.tar.gz
````

### 启动程序
需要安装docker服务，支持1.7以上版本，建议1.10.3或以上版本
····
docker run --name octopus-agent -v /:/rootfs:rw -v /usr/bin/docker-current:/usr/bin/docker:rw -v /var/run/docker.sock:/var/run/docker.sock:rw -p 80:80 -d octopus-agent:0.01
····

###octopus配置修改
---------
#### 1.环境变量方式修改

|环境变量名称                 | 默认值                                 | 说明                            |
| --------------------------- | -------------------------------------  | ------------------------------  |
|OCTOPUS_AGENT_ACCESS_KEY     | o2ldsd9323udae20dsad32w3k3             | api连接加密key                  |
|OCTOPUS_AGENT_ACCESS_ID      | octopus_agent_api_id                   | api连接加密id                   |
|OCTOPUS_AGENT_ACCESS_IPS     | 127.0.0.1                              | 允许访问IP，默认只能本机访问    |
|OCTOPUS_AGENT_SCHEDULER_FILE |                                        | 默认不启动计划任务              |
|OCTOPUS_AGENT_LOG_FILE       | logging.conf                           | 系统日志配置文件                |

#### 环境变量使用
docker run --name octopus-agent -v /home/zhengqs/octopus/octopus-agent/conf/test11.json:/opt/modules/octopus-agent/conf/scheduler.json:ro -v /:/rootfs:rw -v /usr/bin/docker-current:/usr/bin/docker:rw -v /var/run/docker.sock:/var/run/docker.sock:rw -p 33601:80 -e "OCTOPUS_AGENT_ACCESS_IPS=10.1.101.66;192.168.137.1" -e "OCTOPUS_AGENT_ACCESS_KEY=abcdefghijklmn" -d octopus-agent:0.01

#### 2.挂在方式
在本地创建octopus.conf配置文件，通过-v /etc/octopus-agent/octopus.conf:/opt/modules/octopus-agent/conf/octopus.conf:ro 方式过载到容器中。

#### 3.容器cp方式
首先创建容器，然后在本地创建octopus.conf配置文件，再通过docker cp octopus.conf octopus-agent:/opt/modules/octopus-agent/conf/octopus.conf拷贝到容器中，最后重启容器docker restart octopus-agent.

### 设置计划任务

通过docker cp方式将计划任务配置文件拷贝到容器
````
可以通过docker cp scheduler.json octopus-agent:/opt/modules/octopus-agent/conf/scheduler.json
````
通过docker run -v 方式挂在文件
····
docker run --name octopus-agent -v /etc/scheduler.json:/opt/modules/octopus-agent/conf/scheduler.json:ro -v /:/rootfs:rw -v /usr/bin/docker-current:/usr/bin/docker:rw -v /var/run/docker.sock:/var/run/docker.sock:rw -p 80:80 -d octopus-agent:0.01
····


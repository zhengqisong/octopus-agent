FROM flask:0.12

MAINTAINER zhengqsa@digitalchina.com

ENV  TZ Asia/Shanghai

RUN mkdir -p /opt/modules

ADD target/octopus-agent.tar.gz /opt/modules/

ENTRYPOINT ["python", "/opt/modules/octopus-agent/run.py"]

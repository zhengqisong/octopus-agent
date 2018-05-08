#!/bin/bash

res=`python -m compileall .`

if [ -f "./target/octopus-agent.tar.gz" ] ; then 
  rm -f ./target/octopus-agent.tar.gz
fi
echo 'begin build octopus agent'
res=`tar zcvf ./target/octopus-agent.tar.gz ../octopus-agent --exclude=app/*.py --exclude=lib/*.py --exclude=target --exclude=build.sh 2>&1`
 
echo 'build end'

#docker build

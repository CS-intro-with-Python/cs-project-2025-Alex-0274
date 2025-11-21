#!/bin/bash
set -e
docker rm -f $(docker ps -a -q)
docker rmi -f $(docker images -aq)
docker network prune --force
docker builder prune --force

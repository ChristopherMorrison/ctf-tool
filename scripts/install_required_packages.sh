#!/usr/bin/env sh
# Recommended dependencies for running the CHALLENGES on debian 10/ubuntu 18
apt update
apt-get install -y \
    docker-compose \
    docker.io \
    iproute2 \
    cron \
    socat \
    python2.7 \
    python3 python3-pip \
    zip unzip \
    libc6-i386

#!/usr/bin/env sh
# Recommended dependencies for running the CHALLENGES on debian 10/ubuntu 18
apt update
apt-get install -y \
    docker-compose \
    socat \
    iproute2 \
    cron \
    zip \
    unzip \
    python2.7 \
    python3 \
    libc6-i386 \
    zip unzip

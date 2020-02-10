#!/usr/bin/env sh
apt update
apt-get install -y \
    socat \
    iproute2 \
    docker.io \
    docker-compose \
    zip \
    unzip \
    python2.7 \
    python3 \
    python3-pip \
    libc6-i386

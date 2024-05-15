# syntax=docker/dockerfile:1
FROM dcastro93/dpss:alpine_base

# RUN echo "http://dl-cdn.alpinelinux.org/alpine/latest-stable/main" > /etc/apk/repositories
RUN echo "http://dl-cdn.alpinelinux.org/alpine/latest-stable/community" >> /etc/apk/repositories
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

RUN \
  apk add --update \
    alpine-sdk \
    gcc \
    gfortran \
    python3-dev \
    build-base \
    wget \
    curl \
    freetype-dev \
    obfs4proxy \
    libpng-dev \
    openblas-dev \
    dbus-glib \
    libcanberra-gtk3

RUN python3 -m pip install --upgrade pip \
  && python3 -m pip install --no-cache-dir --user \
    numpy \
    bs4

# docker
RUN apk add --update docker openrc
RUN apk del alpine-sdk build-base
RUN rc-update add docker boot
# RUN service docker start

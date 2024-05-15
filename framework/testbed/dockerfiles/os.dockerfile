# syntax=docker/dockerfile:1
FROM dcastro93/dpss:alpine_base
RUN \
  apk add --update \
    alpine-sdk \
    libsodium-dev 

RUN apk add --update docker openrc
RUN rc-update add docker boot

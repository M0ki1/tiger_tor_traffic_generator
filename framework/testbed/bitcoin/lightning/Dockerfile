FROM alpine:latest

WORKDIR /root
RUN apk update && apk add --virtual \
	.build-deps \
	ca-certificates \
	alpine-sdk \
	autoconf \
	automake \
	git \
	libtool \
	gmp-dev \
	sqlite-dev \
	python3 \
	py3-mako \
	net-tools \
	zlib-dev \
	libsodium \
	gettext \
&& git clone https://github.com/ElementsProject/lightning.git \
	&& cd lightning \
	&& git submodule update --init --recursive \
&& ./configure && make && make install && cd .. && rm -fr lightning \
&&  apk del \
    .build-deps

RUN apk tor gmp libgcc libsodium sqlite-libs zlib
COPY torrc /etc/tor/torrc



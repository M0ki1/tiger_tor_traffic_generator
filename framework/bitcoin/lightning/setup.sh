#!/bin/bash

LIGHTNING_VERSION=0.1

mkdir -p data
cd data
if [ ! -f latest.zip ]
then
	wget https://prunednode.today/latest.zip
	unzip latest.zip
	cd ..
fi

docker build --no-cache -t dcastro93/lightning:${LIGHTNING_VERSION} .
docker push dcastro93/lightning:${LIGHTNING_VERSION}

docker pull elementsproject/lightningd
docker run --rm -d --name lightningd elementsproject/lightningd 
docker exec lightningd bash -c "echo \"$(cat torrc)\" | tee /etc/tor/torrc"
docker exec lightningd apt update
docker exec lightningd apt install tor -y
docker exec -u debian-tor lightningd bash -c "tor &"
sleep 30s
}




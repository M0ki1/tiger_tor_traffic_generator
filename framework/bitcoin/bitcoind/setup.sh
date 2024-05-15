#!/bin/bash

BITCOIND_VERSION=0.1

mkdir -p data
cd data
if [ ! -f latest.zip ]
then
	wget https://prunednode.today/latest.zip
	unzip latest.zip
	cd ..
fi

docker build --no-cache -t dcastro93/bitcoind:${BITCOIND_VERSION} .
docker push dcastro93/bitcoind:0.1

# to update the block chain:
function update_block_chain {
docker run --rm -v $(pwd)/data:/bitcoin/.bitcoin --name=bitcoind-node -d \
     -p 8333:8333 \
     -p 127.0.0.1:8332:8332 \
     kylemanna/bitcoind
docker exec bitcoind-node bash -c "echo \"$(cat torrc)\" | tee /etc/tor/torrc"
docker exec bitcoind-node apt update
docker exec bitcoind-node apt install tor -y
docker exec -u debian-tor bitcoind-node bash -c "tor &"
sleep 30s
docker logs bitcoind-node | grep "Got service ID" | sed -n "s/^.*advertising\ service\ \(.*\)\$/\1/p" > onion.txt
}




#!/bin/bash

docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker image rm torp-onion-service
docker build -t torp-onion-service .
for i in $(seq 1 $1);
do
    echo "------ ONION NODE $i ------"
    rm web/hostname web/hs_ed25519_public_key web/hs_ed25519_secret_key
    docker run -v $(pwd)/web:/web --entrypoint /generate.sh torp-onion-service torp
    mkdir onion_addresses_v3/node$i
    cp web/hostname web/hs_ed25519_public_key web/hs_ed25519_secret_key onion_addresses_v3/node$i/
done
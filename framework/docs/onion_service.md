#
```
git clone https://github.com/opsxcq/docker-tor-hiddenservice-nginx.git
cd docker-tor-hiddenservice-nginx/
docker build -t strm/tor-hiddenservice-nginx .
```

* Get access to the container terminal:
```
docker run -it --rm -v $(pwd)/web:/web        --entrypoint /bin/bash strm/tor-hiddenservice-nginx
apt-get update
apt-get install nano
```

* Change files

* Restart services:
```
/etc/init.d/nginx restart
/etc/init.d/nginx status
```

* Setup onion service:
```
chown -R $USER:$USER /var/www
cp www/index.html /var/www/html/
mkdir ~/onion_service_torpedo
chmod 700 ~/onion_service_torpedo/
```

* Edit torrc file

* Restart tor:
```
/etc/init.d/tor restart
```

##
```
apt-get update
apt-get install autoconf
apt-get install make
apt-get install libsodium-dev
apt-get install gcc

```

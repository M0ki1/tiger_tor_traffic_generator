# Torpedo

First of all, make sure the `backend/.env` file exists and is populated.

To run the app (it takes a while):

```bash
ansible-playbook run_collection_webapp.yml -i inventory.cfg --tags "complete_setup"
```

It may look like the `[Build nginx docker image]` task is stuck (if it takes over a minute to complete). If that's the case, check in a separate terminal if the 3 containers are already running and `Ctrl + C` the setup.

```bash
docker container ls
```

When the setup is finished, type `localhost` on a browser to access it.

When done with the server, stop and delete all containers and images with:

```bash
ansible-playbook run_collection_webapp.yml -i inventory.cfg --tags "remove_all_images"
```

## In a different terminal:

To populate the database, first copy data to container:

```bash
docker cp database/populate.sql webapp-db-1:/tmp/populate.sql
```

Connect to the container with bash and execute:

```bash
psql -U torpedo_user -d torpedo_db < /tmp/populate.sql
```

If needed, access db terminal(password -> torpedo_password) with:

```bash
psql -U torpedo_user -W torpedo_db
```

## To add data to Database

"timestamp": 772873729, "size": 400, "sourceIp": "263.127.127.198", "sourcePort": 82, "destIp": "782.928.292.167", "destPort": 83

```bash
curl -d '{"csNodeIp": "263.127.127.198", "entryNodeIp": "782.928.292.167", "type": "SERVICE", "packets": [{"timestamp": 772873729, "size": 400, "sourceIp": "263.127.127.198", "sourcePort": 82, "destIp": "782.928.292.167", "destPort": 83}]}' -H "Content-Type: application/json" -X POST http://localhost:3000/api/flows
```


## Help with docker networks

https://stackoverflow.com/questions/24319662/from-inside-of-a-docker-container-how-do-i-connect-to-the-localhost-of-the-mach


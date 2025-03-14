# cs22

Repo for COMP0022

Collaborators: Lucia, Nikita, Josh

## Docker

To create the image for the fastapi app, run `docker build -t fastapi-app .`

`docker-compose up -d` is the command to get the postgresql container running. There is a network 'cs22', so all containers that are deployed are under the same network and don't interact with any other containers that may be running. 

`docker-compose down` will stop all the containers running and the network. To stop an individual container you can run the command `docker stop <container_name_or_id>`

We will add to the docker compose file as the project goes on so that our app and other services we require can be deployed.

## Migrations

`./migrations.sh` will run the individual python scripts for tables to be created in the db and for data to be loaded in.

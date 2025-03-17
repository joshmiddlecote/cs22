# cs22

Repo for COMP0022

Collaborators: Lucia, Nikita, Josh

## Docker

To create the image for the fastapi app, run `docker build -t fastapi-app .`
To create the image for the migrations container, run `docker build -t migrations-runner .`

Both images have to be build from the corresponding directories. You must wait for the migrations container to exit, or display `Migrations finished`, otherwise there wont be any data to display!

`docker-compose up -d` is the command to get all containers running. There is a network 'cs22', so all containers that are deployed are under the same network and don't interact with any other containers that may be running. 

`docker-compose down` will stop all the containers running and the network. To stop an individual container you can run the command `docker stop <container_name_or_id>`

## App

The webapp can be viewed on `localhost`, no ports are necessary as nginx forwards on your request to the container

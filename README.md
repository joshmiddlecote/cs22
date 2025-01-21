# cs22

Repo for COMP0022

Collaborators: Lucia, Nikita, Josh

## Docker

`docker-compose up -d` is the command to get the postgresql container running. There is a network 'cs22', so all containers that are deployed are under the same network and don't interact with any other containers that may be running. 

`docker-compose down` will stop all the containers running and the network. To stop an individual container you can run the command `docker stop <container_name_or_id>`

We will add to the docker compose file as the project goes on so that our app and other services we require can be deployed.

## Branching

Branching strategy is very important in industry. Normally there are different branches for different environments. You will have your local branch for dev. A staging branch for QA. Then main will be production code. For this project lets just use a main branch and then local branches for individual development. All code changes should go through a Pull Request (PR) and both of the other team members must approve it for it to be merged.

### Misc

Docker App run command:

docker run -v "$PWD:/app" -w /app python:3.10 python hello_world.py

For this to run you have to be in the directory of the app

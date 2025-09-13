#!/bin/bash
docker rmi boids_simulation
docker build -t boids_simulation .
docker rm -f boids_simulation
docker build -t boids_simulation --progress plain .
docker run --rm --name boids_simulation -p 9999:9999 --mount type=bind,source="$(pwd)",target=/home/jovyan -it boids_simulation jupyter lab --port=9999 --notebook-dir=/home/jovyan/
# Simulation von Schwarmbewegungen mithilfe des Boid-Modells von Reynolds

Dieses Projekt wurde im Kontext des Fachpraktikums "Scientific Programming in Python" der Fern-Universität in Hagen erstellt. 

# Erstellen des Docker-Containers

### Variante 1: Mithilfe des beigelegten Shell-Skripts

Bei dieser Variante müssen lediglich die Projektdateien geladen werden, um daraufhin das Shell-Skript zu starten.

### Variante 2: Manuelle Einrichtung des Docker-Containers

#!/bin/bash

Entfernen von Container, falls dieser vorhanden ist:
```docker rm -f boids_simulation```

Entfernen von altem Image, falls bereits vorhanden:
```docker rmi boids_simulation```

Image neu aufbauen anhand von Dockerfile:
```docker build -t boids_simulation .```

Container erstellen und laufen lassen:
```docker run --rm --name boids_simulation -p 9999:9999 --mount type=bind,source="$(pwd)",target=/home/jovyan -it boids_simulation jupyter lab --port=9999 --notebook-dir=/home/jovyan/```

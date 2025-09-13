# Simulation von Schwarmbewegungen mithilfe des Boid-Modells von Reynolds

Dieses Projekt wurde im Kontext des Fachpraktikums "Scientific Programming in Python" der Fern-Universität in Hagen erstellt. 

# Einrichten des Projekts

## Erstellen und Starten des Docker-Containers

### Variante 1: Mithilfe des beigelegten Shell-Skripts

Bei dieser Variante müssen lediglich die Projektdateien geladen werden, um daraufhin das Shell-Skript zu starten.
Das Shell-Skript ist darauf ausgerichtet, alte Images oder Container dieses Projekts zu löschen, um diese dann neu zu erstellen. Das dient dazu, Änderungen im Dockerfile schnell wirksam zu machen.

Falls dieses Verhalten nicht gewünscht ist, können die folgenden Zeilen aus dem Shell-Skript entfernt werden:

```docker rm -f boids_simulation```

```docker rmi boids_simulation```

### Variante 2: Manuelle Einrichtung des Docker-Containers

Image neu aufbauen anhand von Dockerfile:

```docker build -t boids_simulation .```

Container erstellen und laufen lassen:

```docker run --rm --name boids_simulation -p 9999:9999 --mount type=bind,source="$(pwd)",target=/home/jovyan -it boids_simulation jupyter lab --port=9999 --notebook-dir=/home/jovyan/```

Der Link zur Jupyter-Lab-Umgebung sollte daraufhin in der Konsole erscheinen. 



## Starten der Simulation

In der Jupyter-Lab-Umgebung sollte nun ein neues Terminal geöffnet werden. In diesem Terminal kann dann der folgende Befehl ausgeführt werden:

```python3 main.py```

Daraufhin wird ein Schwarm von Boids simuliert. Das Ergebnis der Simulation ist eine .gif-Datei, die im Ordner ```output``` abgelegt wird.

## Verändern der Schwarm-Konfiguration

Falls Verhaltens-Parameter für den Schwarm angepasst werden sollen (bspw. die Gewichtung der Verhaltensregeln), können dafür Konstanten in der ```config.py```-Datei angepasst werden. Die Simulation kann nach Änderungen der Parameter in der ```config.py```-Datei wieder ganz normal über den Befehl ```python3 main.py``` gestartet werden.

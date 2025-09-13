import numpy as np


def generate_cell_range_array(xmax: int, ymax: int, view_distance: float, flock_size: int, seed=123):
    ''' Erstellt einen dreidimensionalen Array (Gitterhöhe x Gitterbreite x 2) als Hilfestellung für das Spatial Grid.
    In dem Array werden Start- und Endindizes der Boids innerhalb einer nach der Zell-Positionen sortierten Liste der Boids gespeichert, um damit jeweils zu repräsentieren,
    welche Boids sich innerhalb eines Zeitschrittes in einer Zelle befinden.
    Die Indizes werden mit -1 initialisiert, um zu repräsentieren, dass zu den jeweiligen Zellen zuerst noch keine Boids zugeordnet sind.
    :param xmax: Höhe des Simulationsfelds.
    :param ymax: Breite des Simulationsfelds.
    :param view_distance: Maximale Distanz von Boids zueinander, damit diese noch als benachbart erkannt werden.
    :return: Array für Indexbereiche von Boids. '''

    # Erstellen des Grids
    grid_width = int(xmax // view_distance) + 1
    grid_height = int(ymax // view_distance) + 1
    return np.full((grid_height, grid_width, 2), fill_value=-1, dtype=int)


def generate_cell_position_array(flock_size):
    ''' Erstellt eine für eine gegebene Größe eines Schwarms einen zweidimensionalen Array,
        welcher dazu dient, die Zelle zu bestimmen, in welcher sich die Boids befinden.
        Ein Array mit Datentyp int wird zurückgegeben, da es sich bei den Zellpositionen eh nur um Ganzzahlen handelt.
        :param flock_size: Größe des Schwarms.
        :return: Mit Nullen gefüllter Array für Speicherung von Zellpositionen. '''
    return np.zeros(shape=(flock_size, 2), dtype=int)

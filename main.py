import numpy as np
from timeit import repeat

from tree import Tree
from config import XMAX, YMAX, VIEW_DISTANCE_SQUARED, VIEW_DISTANCE, FLOCK_SIZE, STEPS_TOTAL
import visualizer
from array_generator import generate_cell_position_array, generate_cell_range_array
from boid_logic import separation_kd, separation_sg, alignment_kd, alignment_sg, cohesion_kd, cohesion_sg, \
    limit_forces, limit_speed, send_boids_back_to_field, separation_np, alignment_np, cohesion_np
from spatial_grid_logic import update_cell_position_array, sort_flock_by_cell_position, fill_cell_range_array


def main_np(flock_size, steps_total):
    '''
    Führt die Boids-Simulation in der optimierten Variante mit numpy aus.
    :param flock_size: Größe des Schwarms.
    :param steps_total: Anzahl Zeitschritte.
    :return: Array mit der Position aller Boids zu allen Zeitschritten
    '''

    # Festgelegter Zufall
    rng = np.random.default_rng(seed=42)

    # Array, das Positonen aller Boids zu allen Zeitschritten speichert
    position_array = np.zeros(shape=(steps_total, flock_size, 2))
    # Array, das Geschwindkeit aller Boids zu allen Zeitschritten speichert
    speed_array = np.zeros(shape=(steps_total, flock_size, 2))

    # Initiale Positionen
    position_array[0, :, :] = rng.random((1, flock_size, 2)) * XMAX

    # Initiale Geschwindigkeiten
    speed_array[0, :, :] = (rng.random((1, flock_size, 2)) - 0.5) * 3

    # Simulationsschritte
    for current_step in range(1, steps_total):
        # Werte aus dem letzten Zeitschritt sind die Basis für die Berechnung des aktuellen Zeitschritts
        last_position_array = position_array[current_step - 1, :, :]
        last_speed_array = speed_array[current_step - 1, :, :]

        # Hier werden die Ergebnisse aus dem aktuellen Zeitschritt gespeichert
        current_position_array = position_array[current_step, :, :]
        current_speed_array = speed_array[current_step, :, :]

        # Einmalige Berechnung von Offsets und Distanzen, die in den Regeln benötigt werden

        differences = np.zeros((flock_size, flock_size, 3))
        diff = last_position_array[:, np.newaxis, :] - last_position_array[np.newaxis, :, :]

        differences[:, :, :2] = diff
        differences[:, :, 2] = differences[:, :, 0] ** 2 + differences[:, :, 1] ** 2

        # Anwenden der Regeln
        alignment_np(last_speed_array, current_speed_array, differences)
        cohesion_np(last_position_array, current_speed_array, differences)
        separation_np(current_speed_array, differences)

        # Begrenzung der Kräfte
        current_speed_array = limit_forces(current_speed_array)
        # Aktualisieren der Geschwindkeiten anhand der Ergebnisse der Regeln
        current_speed_array[:] = last_speed_array + current_speed_array

        # Begrenzung der Geschwindikeiten
        current_speed_array = limit_speed(current_speed_array)

        # Aktualisieren der Positonen anhand der Geschwindikeit
        current_position_array[:] = last_position_array + last_speed_array

        # Anwenden der Raumbegrenzungsregeln
        send_boids_back_to_field(last_position_array, current_position_array, last_speed_array, current_speed_array)

    return position_array


def main_sg(flock_size, steps_total):
    '''
    Führt die Boids-Simulation in der optimierten Variante mit Spatial Grid aus.
    :param flock_size: Größe des Schwarms.
    :param steps_total: Anzahl der Zeitschritte.
    :return: Array mit den Positionen aller Boids zu allen Zeitschritten.
    '''
    # Erzeugen von Zufallsgenerator
    rng = np.random.default_rng(seed=42)

    # Erstellen des position_arrays und des speed_arrays
    position_array = np.zeros(shape=(steps_total, flock_size, 2))
    speed_array = np.zeros(shape=(steps_total, flock_size, 2))

    # Initialisierung von Positionen
    position_array[0, :, :] = rng.random((1, flock_size, 2)) * XMAX

    # Initialisierung von Geschwindigkeiten
    speed_array[0, :, :] = (rng.random((1, flock_size, 2)) - 0.5) * 3

    # Zellenzuordnungstabelle initialisieren
    cell_position_array = generate_cell_position_array(flock_size)

    # Range-Tabelle initialisieren (überall (-1, -1))
    cell_range_array = generate_cell_range_array(XMAX, YMAX, VIEW_DISTANCE_SQUARED, flock_size)

    # Zellzuordnungstabelle initialisieren vor erstem Schritt
    update_cell_position_array(position_array[0, :, :], cell_position_array)

    # Eigentliche Simulation
    for current_step in range(1, steps_total):
        # Werte aus dem letzten Schritt zwischenspeichern
        last_position_array = position_array[current_step - 1, :, :]
        last_speed_array = speed_array[current_step - 1, :, :]

        # Werte aus aktuellem Schritt zwischenspeichern
        current_position_array = position_array[current_step, :, :]
        current_speed_array = speed_array[current_step, :, :]

        # Aktualisierung des Spatial Grids
        update_cell_position_array(last_position_array, cell_position_array)
        sort_flock_by_cell_position(last_position_array, last_speed_array, cell_position_array)
        fill_cell_range_array(cell_position_array, cell_range_array)

        # Separation
        separation_sg(last_position_array, current_speed_array, cell_position_array, cell_range_array,
                      flock_size)
        # Alignment
        alignment_sg(last_position_array, last_speed_array, current_speed_array, cell_position_array, cell_range_array,
                     flock_size)
        # Cohesion
        cohesion_sg(last_position_array, current_speed_array, cell_position_array, cell_range_array,
                    flock_size)

        # Begrenzung der Kräfte
        current_speed_array = limit_forces(current_speed_array)

        current_speed_array[:] = last_speed_array + current_speed_array

        # Geschwindigkeitslimit
        current_speed_array = limit_speed(current_speed_array)

        # Position anhand aktualisierter Geschwindigkeit anpassen
        current_position_array[:] = last_position_array + last_speed_array

        # Falls nötig Boids vom Rand abprallen lassen
        send_boids_back_to_field(last_position_array, current_position_array, last_speed_array, current_speed_array)
    return position_array


def main_kdt(flock_size, steps_total):
    '''
    Führt die Boids-Simulation in der optimierten Variante mithilfe des in SciPy implementierten KD-Baums aus.
    :param flock_size: Größe des Schwarms.
    :param steps_total: Anzahl Zeitschritte.
    :return: Array mit der Position aller Boids zu allen Zeitschritten
    '''

    Tree.update_k(flock_size)

    # Festgelegter Zufall
    rng = np.random.default_rng(seed=42)
    # Array, das Positonen aller Boids zu allen Zeitschritten speichert
    position_array = np.zeros(shape=(steps_total, flock_size, 2))
    # Array, das Geschwindkeit aller Boids zu allen Zeitschritten speichert
    speed_array = np.zeros(shape=(steps_total, flock_size, 2))

    # Initiale Positionen
    position_array[0, :, :] = rng.random((1, flock_size, 2)) * XMAX

    # Initiale Geschwindigkeiten
    speed_array[0, :, :] = (rng.random((1, flock_size, 2)) - 0.5) * 3

    # Simulationsschritte
    for current_step in range(1, steps_total):
        # Werte aus dem letzten Zeitschritt als Basis für die Berechnungen im aktuellen Zeitschritts verwenden
        last_position_array = position_array[current_step - 1, :, :]
        last_speed_array = speed_array[current_step - 1, :, :]

        # Hier werden die Ergebnisse aus dem aktuellen Zeitschritt gespeichert
        current_position_array = position_array[current_step, :, :]
        current_speed_array = speed_array[current_step, :, :]

        # Aufbau bzw. Aktualisierung des KD-Baums
        Tree.update_kdtree(last_position_array)

        distance = VIEW_DISTANCE
        # Initialisierung der Liste als Container für die in den nächsten Schritten berechnete Arrays mit Indizes und
        # Distanzen der Nächsten-Nachbarn
        l = []
        # Iterativer Aufruf der Klassenmethode der Klasse Tree zur Bestimmung der Nächsten-Nachbarn und der jeweiligen Distanzen
        for i in range(0, len(last_position_array)):
            l.append(
                Tree.get_nearest_neighbor(x=last_position_array[i][0], y=last_position_array[i][1], distance=distance))
        # Anwenden der Regeln
        separation_kd(last_position_array, current_speed_array, l)
        alignment_kd(last_position_array, last_speed_array, current_speed_array, l)
        cohesion_kd(last_position_array, current_speed_array, l)

        # Begrenzung der Kräfte
        current_speed_array = limit_forces(current_speed_array)
        # Aktualisieren der Geschwindkeiten anhand der Ergebnisse der Regeln
        current_speed_array[:] = last_speed_array + current_speed_array

        # Geschwindigkeitslimit
        current_speed_array = limit_speed(current_speed_array)

        # Position anhand aktualisierter Geschwindigkeit anpassen
        current_position_array[:] = last_position_array + last_speed_array

        # Falls nötig zum Feld zurückkehren
        send_boids_back_to_field(last_position_array, current_position_array, last_speed_array, current_speed_array)

    return position_array


if __name__ == "__main__":
    times = np.array([])

    times = np.append(times, np.average(repeat(stmt=(lambda: main_np(FLOCK_SIZE, 1)),
                                               repeat=1,
                                               number=1)))

    times = np.append(times, np.average(repeat(setup=(lambda: main_sg(1, 1)), stmt=(lambda: main_sg(FLOCK_SIZE, 1)),
                                               repeat=1,
                                               number=1)))

    times = np.append(times, np.average(repeat(stmt=(lambda: main_kdt(FLOCK_SIZE, 1)),
                                               repeat=1,
                                               number=1)))
    match np.argmin(times):
        case 0:
            visualizer.visualize(main_np(FLOCK_SIZE, STEPS_TOTAL))
        case 1:
            visualizer.visualize(main_sg(FLOCK_SIZE, STEPS_TOTAL))
        case 2:
            visualizer.visualize(main_kdt(FLOCK_SIZE, STEPS_TOTAL))

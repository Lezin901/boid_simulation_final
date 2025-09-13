import numpy as np
from numba import njit

from config import VIEW_DISTANCE_SQUARED, SEPARATION_DISTANCE_SQUARED, SEPARATION_STRENGTH, \
    ALIGNMENT_DISTANCE_SQUARED, ALIGNMENT_STRENGTH, COHESION_DISTANCE_SQUARED, COHESION_STRENGTH, SEPARATION_DISTANCE, \
    ALIGNMENT_DISTANCE, COHESION_DISTANCE, XMAX, YMAX, MAX_FORCE_SQUARED, MAX_SPEED_SQUARED

from spatial_grid_logic import get_possible_neighbour_index_list


def separation_sg(last_position_array, current_speed_array, cell_position_array, cell_range_array,
                  flock_size):
    '''
    Anwendung der Separation-Regeln in der Spatial-Grid-Variante.
    :param last_position_array: Positionen der Boids im letzten Zeitschritt.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param cell_position_array: Zellpositionen der Boids.
    :param cell_range_array: Array mit Indexbereichen, die Zellen repräsentieren.
    :param flock_size: Größe des Schwarms.
    '''
    separation_force_array = np.zeros_like(current_speed_array)

    for i in range(len(last_position_array)):

        # Liste der Indizes möglicher Nachbarn mit der Spatial-Grid-Optimierung ermitteln
        possible_neighbours = get_possible_neighbour_index_list(cell_position_array, i, cell_range_array, XMAX, YMAX,
                                                                VIEW_DISTANCE_SQUARED,
                                                                flock_size)
        # Aktuell betrachteten Boid ausschließen
        possible_neighbours = possible_neighbours[possible_neighbours != i]

        off = last_position_array[i] - last_position_array[possible_neighbours]
        dist = off[:, 0] ** 2 + off[:, 1] ** 2

        # Anwenden der Regel
        dist[dist > SEPARATION_DISTANCE_SQUARED] = 0
        offset = off * np.divide(1.0, dist ** 2, out=np.zeros_like(dist), where=dist != 0)[:, np.newaxis]
        separation_force_array[i] = np.add.reduce(offset)

        # Normieren
        norm = np.linalg.norm(separation_force_array[i])
        if norm != 0:
            separation_force_array[i] = (separation_force_array[i] / norm) * SEPARATION_STRENGTH

    # Geschwindigkeitsänderungen durch seperation-Regel aufaddieren
    current_speed_array[:] += separation_force_array


def alignment_sg(last_position_array, last_speed_array, current_speed_array, cell_position_array, cell_range_array,
                 flock_size):
    '''
    Anwenden der Alignment-Regeln in der Spatial-Grid-Variante.
    :param last_position_array: Positionen der Boids im letzten Zeitschritt.
    :param last_speed_array: Geschwindigkeiten im letzten Schritt.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param cell_position_array: Zellpositionen der Boids.
    :param cell_range_array: Array mit Indexbereichen, die Zellen repräsentieren.
    :param flock_size: Größe des Schwarms.
    '''

    alignment_force_array = np.zeros_like(current_speed_array)
    for i in range(len(last_position_array)):

        # Liste der Indizes möglicher Nachbarn mit der Spatial-Grid-Optimierung ermitteln
        possible_neighbours = get_possible_neighbour_index_list(cell_position_array, i, cell_range_array, XMAX, YMAX,
                                                                VIEW_DISTANCE_SQUARED,
                                                                flock_size)
        # Aktuell betrachteten Boid ausschließen
        possible_neighbours = possible_neighbours[possible_neighbours != i]

        # Berechnen von Offsets und Distanzen zu möglichen Nachbarn
        off = last_position_array[i] - last_position_array[possible_neighbours]
        dist = off[:, 0] ** 2 + off[:, 1] ** 2

        filter_arr = dist < ALIGNMENT_DISTANCE_SQUARED
        last_speed_array_filtered = last_speed_array[possible_neighbours]
        acc_speed = np.add.reduce(last_speed_array_filtered[filter_arr])
        neighbour_count = len(last_speed_array_filtered[filter_arr])

        # Anwenden der Regel
        if neighbour_count > 0:
            acc_speed /= neighbour_count
            acc_speed -= last_speed_array[i]

            norm = np.linalg.norm(acc_speed)
            if norm != 0:
                acc_speed = acc_speed / norm

            acc_speed *= ALIGNMENT_STRENGTH

        alignment_force_array[i] = acc_speed

    # Geschwindigkeitsänderungen durch alignment-Regel aufaddieren
    current_speed_array[:] += alignment_force_array


def cohesion_sg(last_position_array, current_speed_array, cell_position_array, cell_range_array,
                flock_size):
    '''
    Anwenden der Cohesion-Regeln in der numpy-optimieten Variante
    :param last_position_array: Positionen der Boids im letzten Zeitschritt.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param cell_position_array: Zellpositionen der Boids.
    :param cell_range_array: Array mit Indexbereichen, die Zellen repräsentieren.
    :param flock_size: Größe des Schwarms.
    '''

    cohesion_force_array = np.zeros_like(current_speed_array)
    for i in range(len(last_position_array)):
        # Liste der Indizes möglicher Nachbarn mit der Spatial-Grid-Optimierung ermitteln
        possible_neighbours = get_possible_neighbour_index_list(cell_position_array, i, cell_range_array, XMAX, YMAX,
                                                                VIEW_DISTANCE_SQUARED,
                                                                flock_size)
        # Aktuell betrachteten Boid ausschließen
        possible_neighbours = possible_neighbours[possible_neighbours != i]

        # Berechnen von Offsets und Distanzen zu möglichen Nachbarn
        off = last_position_array[i] - last_position_array[possible_neighbours]
        dist = off[:, 0] ** 2 + off[:, 1] ** 2

        # Anwenden der Regel
        filter_arr = dist < COHESION_DISTANCE_SQUARED
        last_position_array_filtered = last_position_array[possible_neighbours]
        acc_pos = np.add.reduce(last_position_array_filtered[filter_arr])
        neighbour_count = len(last_position_array_filtered[filter_arr])

        if neighbour_count > 0:
            acc_pos /= neighbour_count
            acc_pos -= last_position_array[i]

            norm = np.linalg.norm(acc_pos)
            if norm != 0:
                acc_pos = acc_pos / norm

            acc_pos *= COHESION_STRENGTH

        cohesion_force_array[i] = acc_pos
    # Geschwindigkeitsänderungen durch cohesion-Regel aufaddieren
    current_speed_array[:] += cohesion_force_array


def separation_kd(last_position_array, current_speed_array, dist_list):
    '''
    Anwenden der Separation-Regeln in der optimierten Variante mithilfe des in SciPy implementierten KD-Baums aus.
    :param last_position_array: Positionen der Boids im letzten Zeitschritt.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param dist_list: Liste mit vorberechneten Arrays mit Angaben zu Indizes und Distanz der Nächsten-Nachbarn
    :return:
    '''

    # speichert das Ergebnis der Regelanwendung
    separation_force_array = np.zeros_like(current_speed_array)

    # Iterative Bestimmung der Geschwindigkeitsänderung durch die Anwendungder seperation-Regel für jeden einzelnen Boid
    for i in range(len(last_position_array)):

        # Reduzierung der separation Distanz
        index = dist_list[i][
                    0] < SEPARATION_DISTANCE
        possible_neighbours = dist_list[i][1].astype(int)[index].astype(int)

        # Berechnen aller Offsets
        off = last_position_array[i] - last_position_array[possible_neighbours]
        dist = dist_list[i][0][index]

        offset = off * np.divide(1.0, dist ** 2, out=np.zeros_like(dist), where=dist != 0)[:, np.newaxis]

        separation_force_array[i] = np.add.reduce(offset)

        # Normieren des Ergebnisses
        norm = np.linalg.norm(separation_force_array[i])
        if norm != 0:
            separation_force_array[i] = (separation_force_array[i] / norm) * SEPARATION_STRENGTH

    # Geschwindigkeitsänderungen durch seperation-Regel aufaddieren
    current_speed_array[:] += separation_force_array


def alignment_kd(last_position_array, last_speed_array, current_speed_array, dist_list):
    '''
    Anwenden der Alignment-Regeln in der optimierten Variante mithilfe des in SciPy implementierten KD-Baums aus.
    :param last_position_array: Positionen der Boids im letzten Zeitschritt.
    :param last_speed_array: Geschwindigkeiten im letzten Schritt.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param dist_list: Liste mit vorberechneten Arrays mit Angaben zu Indizes und Distanz der Nächsten-Nachbarn.
    '''

    # speichert das Ergebnis der Regelanwendung
    alignment_force_array = np.zeros_like(current_speed_array)

    # Iterative Bestimmung der Geschwindigkeitsänderung durch die Anwendungder alignment-Regel für jeden einzelnen Boid
    for i in range(len(last_position_array)):
        # Reduzierung der alignment Distanz
        index = dist_list[i][
                    0] < ALIGNMENT_DISTANCE

        possible_neighbours = dist_list[i][1].astype(int)[index].astype(int)

        last_speed_array_filtered = last_speed_array[possible_neighbours]

        # Aufsummieren der Geschwindikeiten
        acc_speed = np.add.reduce(last_speed_array_filtered)
        neighbour_count = len(last_speed_array_filtered)

        if neighbour_count > 0:
            # Berechnen des Geschwindikeitsdurchschnitts
            acc_speed /= neighbour_count
            acc_speed -= last_speed_array[i]
            # Normieren des Ergebnisses
            norm = np.linalg.norm(acc_speed)
            if norm != 0:
                acc_speed = acc_speed / norm

            acc_speed *= ALIGNMENT_STRENGTH

        alignment_force_array[i] = acc_speed

    # Geschwindigkeitsänderungen durch alignment-Regel aufaddieren
    current_speed_array[:] += alignment_force_array


def cohesion_kd(last_position_array, current_speed_array, dist_list):
    '''
    Anwenden der Cohesion-Regeln in der optimierten Variante mithilfe des in SciPy implementierten KD-Baums aus.
    :param last_position_array: Positionen der Boids im letzten Zeitschritt.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param dist_list: Liste mit vorberechneten Arrays mit Angaben zu Indizes und Distanz der Nächsten-Nachbarn.
    '''

    # speichert das Ergebnis der Regelanwendung
    cohesion_force_array = np.zeros_like(current_speed_array)
    # Iterative Bestimmung der Geschwindigkeitsänderung durch die Anwendungder cohesion-Regel für jeden einzelnen Boid
    for i in range(len(last_position_array)):

        # Reduzierung der cohesion Distanz
        index = dist_list[i][
                    0] < COHESION_DISTANCE

        possible_neighbours = dist_list[i][1].astype(int)[index].astype(int)
        last_position_array_filtered = last_position_array[possible_neighbours]
        # Aufsummieren der Positionen
        acc_pos = np.add.reduce(last_position_array_filtered)
        neighbour_count = len(last_position_array_filtered)

        if neighbour_count > 0:
            # Berechnen des Positionsdurchschnitts
            acc_pos /= neighbour_count
            acc_pos -= last_position_array[i]
            # Normieren des Ergebnisses
            norm = np.linalg.norm(acc_pos)
            if norm != 0:
                acc_pos = acc_pos / norm

            acc_pos *= COHESION_STRENGTH

        cohesion_force_array[i] = acc_pos

    # Geschwindigkeitsänderungen durch cohesion-Regel aufaddieren
    current_speed_array[:] += cohesion_force_array


def separation_np(current_speed_array, differences):
    '''
    Anwendung der Separation-Regeln in der numpy-optimierten Variante. Wird als letztes angewandt, da differnces
    verändert werden kann.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param differences: vorberechnetes Array mit Offsets und Distanzen
    '''

    # Filtern aller zu großen Distanzen
    condition = differences[:, :, 2] > SEPARATION_DISTANCE_SQUARED
    differences[:, :, 2][condition] = 0

    # Berechnen aller Offsets
    offset = differences[:, :, :2] * np.divide(1.0, differences[:, :, 2] ** 2, out=np.zeros_like(differences[:, :, 2]),
                                               where=differences[:, :, 2] != 0)[:, :, np.newaxis]

    # Aufsummieren der Offsets
    separation_force_array = np.add.reduce(offset)

    # Normieren des Ergebnisses
    norm = np.linalg.norm(separation_force_array, axis=1)
    separation_force_array = np.divide(separation_force_array, norm[:, np.newaxis], out=separation_force_array,
                                       where=norm[:, np.newaxis] != 0) * SEPARATION_STRENGTH

    # Regelergebnis zum Gesamtergebnis hinzufügen
    current_speed_array[:] += separation_force_array * -1


def alignment_np(last_speed_array, current_speed_array, differences):
    '''
    Anwenden der Alignment-Regeln in der numpy-optimieten Variante.
    :param last_speed_array: Geschwindigkeiten im letzten Schritt.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param differences: Vorberechnetes Array mit Offsets und Distanzen.
    :return:
    '''

    alignment_force_array = np.zeros_like(current_speed_array)

    # Filtern zu großer Distanzen
    filter_arr = differences[:, :, 2] < ALIGNMENT_DISTANCE_SQUARED
    np.fill_diagonal(filter_arr, False)
    # Zählen der Nachbarn
    neighbour_count = filter_arr.sum(axis=1)
    neighbour_count = neighbour_count[:, np.newaxis]

    mask = filter_arr[:, :, np.newaxis]
    # Aufsummieren der Geschwindikeiten
    acc_speed = np.sum(last_speed_array * mask, axis=1)
    # Berechnen des Geschwindikeitsdurchschnitts
    acc_speed = np.divide(acc_speed, neighbour_count, out=np.zeros_like(acc_speed), where=neighbour_count != 0)
    acc_speed = np.subtract(acc_speed, last_speed_array, out=np.zeros_like(acc_speed), where=acc_speed != 0)

    # Normieren des Ergebnisses
    norm = np.linalg.norm(acc_speed, axis=1)
    alignment_force_array = np.divide(acc_speed, norm[:, np.newaxis], out=acc_speed,
                                      where=norm[:, np.newaxis] != 0) * ALIGNMENT_STRENGTH

    # Regelergebnis zum Gesamtergebnis hinzufügen
    current_speed_array[:] += alignment_force_array


def cohesion_np(last_position_array, current_speed_array, differences):
    '''
    Anwenden der Cohesion-Regeln in der numpy-optimieten Variante.
    :param last_position_array: Positionen der Boids im letzten Zeitschritt.
    :param current_speed_array: Aktuelle Geschwindigkeiten.
    :param differences: Vorberechnetes Array mit Offsets und Distanzen.
    :return:
    '''

    # Filtern zu großer Distanzen
    filter_arr = differences[:, :, 2] < COHESION_DISTANCE_SQUARED
    np.fill_diagonal(filter_arr, False)

    # Zählen der Nachbarn
    neighbour_count = filter_arr.sum(axis=1)
    neighbour_count = neighbour_count[:, np.newaxis]

    mask = filter_arr[:, :, np.newaxis]
    # Aufsummieren der Positionen
    acc_pos = np.sum(last_position_array * mask, axis=1)

    # Berechnen der durchschnittlichen Position
    acc_pos = np.divide(acc_pos, neighbour_count, out=np.zeros_like(acc_pos), where=neighbour_count != 0)
    acc_pos = np.subtract(acc_pos, last_position_array, out=np.zeros_like(acc_pos), where=acc_pos != 0)

    # Normieren des Ergebnisses
    norm = np.linalg.norm(acc_pos, axis=1)
    cohesion_force_array = np.divide(acc_pos, norm[:, np.newaxis], out=acc_pos,
                                     where=norm[:, np.newaxis] != 0) * COHESION_STRENGTH

    # Regelergebnis zum Gesamtergebnis hinzufügen
    current_speed_array[:] += cohesion_force_array


def limit_speed(current_speed_array):
    ''' Bearbeitet den Geschwindigkeits-Array der Boids so,
    dass Boids mit zu hoher Geschwindigkeit (größer als MAX_SPEED) in Geschwindigkeit begrenzt werden. Die Methode arbeitet inplace.
    :param current_speed_array: Array mit Geschwindigkeiten der Boids. '''
    lengths = current_speed_array[:, 0] ** 2 + current_speed_array[:, 1] ** 2
    mask = lengths > MAX_SPEED_SQUARED

    current_speed_array[mask] = current_speed_array[mask] / np.sqrt(lengths[mask][:, np.newaxis])
    return current_speed_array


def limit_forces(current_speed_array):
    ''' Bearbeitet den übergebenen Geschwindigkeits-Array so,
    dass die auf die Boids wirkenden Kräfte bei zu hohen Werten limitiert werden.
    Die Methode unterscheidet sich eigentlich nicht von der limit_speed-Methode, wird im Kontext aber anders genutzt. Die Werte werden inplace geändert.
    :param current_speed_array: Array mit Geschwindigkeiten der Boids'''
    lengths = current_speed_array[:, 0] ** 2 + current_speed_array[:, 1] ** 2
    mask = lengths > MAX_FORCE_SQUARED
    current_speed_array[mask] = current_speed_array[mask] / np.sqrt(lengths[mask][:, np.newaxis])
    return current_speed_array


@njit
def send_boids_back_to_field(last_position_array, current_position_array, last_speed_array, current_speed_array):
    ''' Behandelt Kollisionen der Boids mit dem Rand des Simulationsfeldes. Die Boids prallen wie Bälle vom Rand ab.
    :param last_position_array: Positionen der Boids im letzten Zeitschritt.
    :param current_position_array: Positionen der Boids im aktuellen Zeitschritt.
    :param last_speed_array: Geschwindigkeiten der Boids im letzten Schritt.
    :param current_speed_array: Geschwindigkeiten der Boids im aktuellen Schritt.'''

    # Linke Wand
    behind_left_wall = last_position_array[:, 0] < 0
    current_position_array[behind_left_wall, 0] = np.absolute(last_position_array[behind_left_wall, 0])
    current_speed_array[behind_left_wall, 0] = last_speed_array[behind_left_wall, 0] * -1
    current_position_array[behind_left_wall, 0] += 1

    # Rechte Wand
    behind_right_wall = last_position_array[:, 0] > XMAX
    current_position_array[behind_right_wall, 0] = 2 * XMAX - last_position_array[behind_right_wall, 0]
    current_speed_array[behind_right_wall, 0] = last_speed_array[behind_right_wall, 0] * -1
    current_position_array[behind_right_wall, 0] -= 1

    # Boden
    under_floor = last_position_array[:, 1] < 0
    current_position_array[under_floor, 1] = np.absolute(last_position_array[under_floor, 1])
    current_speed_array[under_floor, 1] = last_speed_array[under_floor, 1] * -1
    current_position_array[under_floor, 1] += 1

    # Decke
    over_ceiling = last_position_array[:, 1] > YMAX
    current_position_array[over_ceiling, 1] = 2 * YMAX - last_position_array[over_ceiling, 1]
    current_speed_array[over_ceiling, 1] = last_speed_array[over_ceiling, 1] * -1
    current_position_array[over_ceiling, 1] -= 1

import numpy as np
from numba import njit

from config import VIEW_DISTANCE_SQUARED


@njit
def update_cell_position_array(position_array, cell_position_array):
    '''Ordnet den Boids anhand ihrer Position einer Zelle zu. Die Methode arbeitet inplace.
    :param position_array: Positionen der Boids.
    :param cell_position_array: Zugeordnete Zellen. '''
    cell_position_array[:, 0] = position_array[:, 0] // VIEW_DISTANCE_SQUARED
    cell_position_array[:, 1] = position_array[:, 1] // VIEW_DISTANCE_SQUARED


def sort_flock_by_cell_position(position_array, speed_array, cell_position_array):

    ''' Sortiert den position_array, den speed_array und den cell_position_array anhand der Zellpositionen um (die Methode arbeitet inplace).
    Wir sortieren zuerst nach x-Zelle, dann nach y-Zelle. Diese Sortierung dient dazu,
    dass Indexbereiche für die Boids angegeben werden können, welche die Zellen im Spatial Grid repräsentieren.
    :param position_array: Positionen der Boids.
    :param speed_array: Geschwindigkeiten der Boids.
    :param cell_position_array: Zellpositionen der Boids.'''

    # Sortierte Indizes erhalten
    # (lexsort könnte hier durch argsort ersetzt werden, damit alles numba kompatibel wird)
    sort_indices = np.lexsort((cell_position_array[:, 1], cell_position_array[:, 0]))

    # Arrays mithilfe der Indizes umsortieren
    position_array[:] = position_array[sort_indices]
    speed_array[:] = speed_array[sort_indices]
    cell_position_array[:] = cell_position_array[sort_indices]


@njit
def fill_cell_range_array(cell_position_array, cell_range_array):
    ''' Aktualisiert die Werte des cell_range_arrays mit neuen Indexbereichen,
    nachdem die Boids anhand ihrer zugeordneten Zellen umsortiert wurden.
    :param cell_position_array: Zellpositionen der Boids.
    :param cell_range_array: Array mit Indexbereichen, die Zellen repräsentieren.
    '''

    # Zurücksetzen des cell_range_arrays
    # (Entfernen der Zuordnung von Boids zu Zellen)
    cell_range_array[:] = -1

    # last_cell wird mit erstem Eintrag aus cell_map initialisiert
    last_cell = (int(cell_position_array[0, 0]), int(cell_position_array[0, 1]))
    start_index = 0
    for i in range(1, len(cell_position_array)):
        current_cell = (int(cell_position_array[i, 0]), int(cell_position_array[i, 1]))

        if current_cell != last_cell:
            cell_x, cell_y = last_cell
            cell_range_array[cell_x, cell_y, 0] = start_index
            cell_range_array[cell_x, cell_y, 1] = i
            start_index = i
            last_cell = current_cell

    # Letzte Zelle setzen
    cell_x, cell_y = last_cell
    cell_range_array[cell_x, cell_y, 0] = start_index
    cell_range_array[cell_x, cell_y, 1] = len(cell_position_array)


@njit
def get_index_list_by_cell(cell_x, cell_y, cell_range_array):
    ''' Gibt eine Liste mit Indizes in der sortierten Liste der Boids zurück. Die Index-Liste repräsentiert alle Boids, die sich innerhalb einer Zelle befinden.
    :param cell_x: x-Position der gefragten Zelle.
    :param cell_y: y-Position der gefragen Zelle.
    :param cell_range_array: Array mit Indexbereichen, die Zellen repräsentieren.
    :return: Eine Liste von Indizes der Boids, die sich innerhalb der angefragten Zelle befinden. '''

    start = cell_range_array[cell_x, cell_y, 0]
    end = cell_range_array[cell_x, cell_y, 1]
    return list(range(start, end))


@njit
def get_possible_neighbour_index_list(cell_position_array, index, cell_range_array, XMAX, YMAX,
                                      VIEW_DISTANCE, flock_size):
    ''' Findet für einen Boid die Indizes der benachbarten Boids im Simulationsfeld.
     :param cell_position_array: Zellpositionen der Boids.
     :param index: Index des Boids, dessen Nachbarn gesucht werden sollen.
     :param cell_range_array: Array mit Indexbereichen, die Zellen repräsentieren.
     :param position_array: Positionen der Boids.
     :param XMAX: Breite des Simulationsfeldes.
     :param YMAX: Höhe des Simulationsfeldes.
     :param VIEW_DISTANCE: Sichtweite, innerhalb der Nachbarn gefunden werden sollen.
     :param flock_size: Größe des Schwarms.
     :return: Array mit Indizes von Boids, welche mit dem entsprechenden Boid benachbart sind. '''

    max_neighbours = flock_size
    neighbours = np.empty(max_neighbours, dtype=np.int32)
    count = 0

    cell_x, cell_y = cell_position_array[index]

    for x in range(max(0, cell_x - 1), min(cell_x + 2, XMAX // VIEW_DISTANCE + 1)):
        for y in range(max(0, cell_y - 1), min(cell_y + 2, YMAX // VIEW_DISTANCE + 1)):
            candidate_indices = get_index_list_by_cell(x, y, cell_range_array)
            for i in range(len(candidate_indices)):
                neighbours[count] = candidate_indices[i]
                count += 1

    return neighbours[:count]

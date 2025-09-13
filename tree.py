import numpy as np
from scipy.spatial import KDTree
from config import FLOCK_SIZE


'''Die folgende Klasse stellt Klassenmethoden für die Operationen in einem KD-Baum bereit'''
class Tree:

    tree: KDTree = None
    '''Anzahl der Boids'''
    k = int(FLOCK_SIZE)

    @classmethod
    def update_kdtree(cls,points):
        '''
        Initialisierung der Variable tree zum Aufbau bzw. Auktualisierung des KD-Baums.
        :param points:
        '''
        Tree.tree = KDTree(points)

    @classmethod
    def update_k(cls, k):
        Tree.k = k

    @classmethod
    def get_nearest_neighbor(cls, x, y, distance):
        '''
        Initialisierung der Variable tree zum Aufbau bzw. Auktualisierung des KD-Baums.
        :param x:
        :param k:
        :param distance_upper_bound:
        :param workers:
        :return Array mit jeweils einem Index und Distanzarray:
        '''

        dist, ind = Tree.tree.query(x=[x, y], k=Tree.k, distance_upper_bound=distance, workers=-1)
        dist = np.extract((dist!=np.inf),dist)

        ind = np.extract(ind != Tree.k, ind)
        dist_ind = np.array([dist,ind])

        return dist_ind
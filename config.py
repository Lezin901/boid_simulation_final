FLOCK_SIZE = 50
'''Größe des Schwarms'''

STEPS_TOTAL = 100
'''Anzahl der simulierten Schritte'''

XMAX = 200
'''Breite des Simulationsfelds '''

YMAX = 200
'''Höhe des Simulationsfeldes '''

MAX_FORCE = 0.15
''' Maximal wirkende Kraft. '''

MAX_FORCE_SQUARED = MAX_FORCE ** 2
''' Quadrierte maximal wirkende Kraft. '''

MAX_SPEED = 5
''' Maximale Geschwindigkeit der Boids. '''

MAX_SPEED_SQUARED = MAX_SPEED ** 2
''' Quadrierte maximale Geschwindigkeit der Boids. '''

VIEW_DISTANCE = 40
''' Muss größer als alle anderen Distanzen sein, 
da sie teils für eine Vorfilterung für die Bestimmung von Nachbarn benutzt wird. '''
VIEW_DISTANCE_SQUARED = VIEW_DISTANCE ** 2
''' Quadrierte Sichtweite der Boids. '''

SEPARATION_STRENGTH = 0.14
'''Intensität der Verhaltensregel "Separation". '''
SEPARATION_DISTANCE = 8.0
'''Sichtweite pro Boid für Verhaltensregel "Separation". '''
SEPARATION_DISTANCE_SQUARED = SEPARATION_DISTANCE ** 2  # 8.0
'''Quadrierte Sichtweite pro Boid für Verhaltensregel "Separation". '''

ALIGNMENT_STRENGTH = 0.03
'''Intensität der Verhaltensregel "Alignment". '''
ALIGNMENT_DISTANCE = 24.0
'''Sichtweite pro Boid für Verhaltensregel "Alignment". '''
ALIGNMENT_DISTANCE_SQUARED = ALIGNMENT_DISTANCE ** 2
'''Quadrierte Sichtweite pro Boid für Verhaltensregel "Alignment". '''

COHESION_STRENGTH = 0.03
'''Intensität der Verhaltensregel "Cohesion". '''
COHESION_DISTANCE = 30.0
'''Sichtweite pro Boid für Verhaltensregel "Cohesion". '''
COHESION_DISTANCE_SQUARED = COHESION_DISTANCE ** 2
'''Quadrierte Sichtweite pro Boid für Verhaltensregel "Cohesion". '''

import numpy as np
import math

#def distance(point_1)

def get_vector(point1=(0, 0), point2=(0, 0)):# get a vector between two points
    vector = (point2[0] - point1[0], point2[1] - point1[1])
    return vector

def distance(point1=(0, 0), point2=(0, 0)):
    vector = (point1[0] - point2[0], point1[1] - point2[1])
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)

def magnitude(vector=(0, 0)):
    return math.sqrt((vector[0] ** 2) + (vector[1] ** 2))

def normalize_vector(vector=(0, 0)):
    #vector = np.array([vector[0], vector[1]])
    vectorMag = magnitude(vector)
    vector = vector/vectorMag
    return vector

def set_magnitude(new_magnitude, vector=(0, 0)):
    vector = normalize_vector(vector)
    vector[0] *= new_magnitude
    vector[1] *= new_magnitude
    return vector

def limit_vector(magnitude_cap, vector=(0, 0)):
    if (magnitude(vector) > magnitude_cap):
        vector = normalize_vector(vector)
        vector[0] *= magnitude_cap
        vector[1] *= magnitude_cap

    return vector


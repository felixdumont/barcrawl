import math
from geopy import distance
import pandas as pd


def calculate_distance(loc1, loc2, method='euclidean'):
    """
    Calculate the distance in miles between locations 1 and 2
    :param loc1: Tuple containing coordinates for loc1
    :param loc2: Tuple containing coordinates for loc2
    :param method: 'euclidean', 'manhattan' (default value = 'euclidean')
    :return: Distance in miles (float)
    """
    # Calculation of Manhattan Distance
    if method == 'manhattan':
        R = 6371  # Earth's radius in km
        km_to_mile = 0.621371

        lat1, lon1 = loc1
        lat2, lon2 = loc2
        lat_delta = math.radians(abs(lat1 - lat2))
        lon_delta = math.radians(abs(lon1 - lon2))

        # Latitude distance calculation
        a = (math.sin(lat_delta / 2)) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        lat_distance = R * c

        # Longitude distance calculation
        a = (math.sin(lon_delta / 2)) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        lon_distance = R * c

        return (abs(lat_distance) + abs(lon_distance)) * km_to_mile

    # Calculation of euclidean distance
    else:
        return distance.distance(loc1, loc2).miles


def walking_time(dist, speed=4):
    """
    Calculates the time required to walk the distance for a given speed.
    :param distance: Distance in km
    :param speed: Speed in km/hr (default value = 4 km/hr)
    :return: Walking time in minutes
    """
    t_walking = dist / speed

    return t_walking


def generate_distance_matrix(locations, names, method='euclidean'):
    """
    Given a list of n tuples representing location coordinates, return an nxn matrix containing all of the distances
    :param locations: list of n tuples representing location coordinates
    :param names: list of names, ordered in the same way as locations
    :return: data frame, nxn matrix containing all of the distances
    """
    n = len(locations)
    dist_matrix = [[0] * n for i in range(n)]
    for row in range(n):
        for col in range(n):
            dist_matrix[row][col] = walking_time(calculate_distance(locations[row], locations[col], method))

    return dist_matrix
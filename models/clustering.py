import numpy as np
import math
from geopy import distance
import pandas as pd
from sklearn.cluster import OPTICS, AgglomerativeClustering
import matplotlib.pyplot as plt
from preprocessing.business_utils import walking_time, calculate_distance

def get_dist_from_time(max_time):
    start_lat = 43.6426
    start_lon = -79.3871
    new_lat = start_lat
    while True:
        new_lat = new_lat + 0.001
        new_time = walking_time(calculate_distance((new_lat, start_lon), (start_lat, start_lon)))
        if new_time > max_time:
            return new_lat-start_lat


def get_clusters(locations, names):
    data = np.array([[x,y] for (x,y) in locations])
    eps = get_dist_from_time(0.25)
    print(eps)
    #for i in range (0,100,10):
    #    clustering = OPTICS(max_eps =eps, metric='euclidean', min_samples=2, min_cluster_size=6, xi =i/100.0).fit(data)
    #    plt.scatter(data[:, 0], data[:, 1], c=clustering.labels_)
    #    plt.show()
    #clustering = OPTICS(max_eps=eps, metric='euclidean', min_samples=2, min_cluster_size=6, xi=0.92).fit(data)
    # For ward, use ~0.4
    # Complete use 0.1, 0.12 or 0.15
    #for val in [0, 0.05, 0.08, 0.1, 0.12, 0.15]:
    #for val in [0, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5]:
    #    print(val)
    #    clustering = AgglomerativeClustering(n_clusters=None,
    #                                     distance_threshold=val, linkage='ward', compute_full_tree=True).fit(data)
    #    plt.scatter(data[:, 0], data[:, 1], c=clustering.labels_)
    #    plt.show()
    clustering = AgglomerativeClustering(n_clusters=None,
                                         distance_threshold=0.32, linkage='ward', compute_full_tree=True).fit(data)
    return list(clustering.labels_)
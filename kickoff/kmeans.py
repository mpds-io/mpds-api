"""
Pure-Python 100 lines
multidimensional K-Means
"""
import math
import random


class Point(object):
    def __init__(self, coords, reference=None):
        self.coords = coords
        self.n = len(coords)
        self.reference = reference

    def __repr__(self):
        return ", ".join(map(str, self.coords))

class Cluster(object):
    def __init__(self, points):
        if len(points) == 0: raise RuntimeError("Empty cluster")
        self.points = points
        self.n = points[0].n
        for p in points:
            if p.n != self.n: raise RuntimeError("Multispace cluster")
        self.centroid = self.calculate_centroid()

    def __repr__(self):
        rep = ""
        for p in self.points:
            rep += str(p) + "\n"
        return rep[:-1]

    # Assign a new list of Points to the Cluster, returns centroid difference
    def update(self, points):
        old_centroid = self.centroid
        self.points = points
        self.centroid = self.calculate_centroid()
        return get_distance(old_centroid, self.centroid)

    def calculate_centroid(self):
        return Point([sum(p.coords[i] for p in self.points) / len(self.points) for i in range(self.n)])

def kmeans(points, k, cutoff=0.5):
    # Randomly sample k Points from the points list, build Clusters around them
    if k > len(points): raise RuntimeError("Not enough points")
    initial = random.sample(points, k)
    clusters = [Cluster([p]) for p in initial]
    while True:
        lists = []
        for c in clusters: lists.append([])
        for p in points:
            # Figure out which Cluster's centroid is the nearest
            smallest_distance = get_distance(p, clusters[0].centroid)
            index = 0
            for i in range(len(clusters[1:])):
                distance = get_distance(p, clusters[i+1].centroid)
                if distance < smallest_distance:
                    smallest_distance = distance
                    index = i+1
            # Add this Point to that Cluster's corresponding list
            lists[index].append(p)
        # Update each Cluster with the corresponding list
        biggest_shift = 0.0
        for i in range(len(clusters)):
            if not len(lists[i]): continue # prevent ZeroDivisionError in calculate_centroid
            shift = clusters[i].update(lists[i])
            biggest_shift = max(biggest_shift, shift)
        if biggest_shift < cutoff: break
    return clusters

def get_distance(a, b):
    if a.n != b.n: raise RuntimeError("Incomparable points")
    return math.sqrt(sum(pow((a.coords[i] - b.coords[i]), 2) for i in range(a.n)))

def k_from_n(n):
    if n > 200: return 8
    elif 100 < n <= 200: return 6
    elif 50 < n <= 100: return 5
    elif 30 < n <= 50: return 4
    else: return 3

def make_random_point(n, lower, upper):
    return Point([random.uniform(lower, upper) for _ in range(n)])

if __name__ == "__main__":
    num_points, n, lower, upper = 30, 2, -10, 10
    points = []
    for i in range(num_points):
        points.append(make_random_point(n, lower, upper))
    clusters = kmeans(points, k_from_n(num_points))

    for p in points:
        print(p)
    print
    for c in clusters:
        print(c)
        print

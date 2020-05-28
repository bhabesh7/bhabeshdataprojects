#Author: Bhabesh Chandra Acharya
#Date: 28-May-2020
#Purpose: K-Means agorithm implementation
#Usage: python3 Kmeans.py <k-number>
#Libs: Pandas, Numpy
import random
import pandas as pd
import numpy as np
import sys

DATASET_SIZE = 100
DATASET_VALUE_MAX = 5000
DATASET_VALUE_MIN = 0

class my_dictionary(dict):
    def __init__(self):
        self = dict()

    def insert(self, key, value):
        if self.get(key) is None:
            lt = [value]
            self[key] = lt
        else:
            l = list(self[key])
            l.append(value)
            self[key]=l

def distance(x,y):
    return np.sqrt(np.square(x) + np.square(y))

def are_centroids_equal_by_rule(cent1, cent2):
    if len(cent1) == len(cent2):
        for c in range(len(cent1)):
            if cent1[c] == -1 or cent2[c] == -1:
                return False
            if cent1[c] == cent2[c]:
                continue
        return True
    return False

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("invalid args provided. usage -> python3 KMeans.py <K>", file=sys.stderr)
        exit(-1)

    k = int(sys.argv[1])
    # k =2
    data_arr = np.random.random(DATASET_SIZE)
    class_arr = np.full(DATASET_SIZE, -1)
    distance_arr = np.full(DATASET_SIZE, 99999999999999)
    centroidlist = []
    prevcentroidlist =[]
    class_count = []

    #pick k random centroids
    for i in range(k):
        t = random.randint(0, DATASET_SIZE)
        centroidlist.append(t)
        prevcentroidlist.append(t)
        #default the class counts per class (class is presented by index)
        class_count.append(0)
        firsttime = True

    while firsttime or not are_centroids_equal_by_rule(prevcentroidlist, centroidlist):
        firsttime = False
        for c in range(len(centroidlist)):
            prevcentroidlist[c] = centroidlist[c]
        #calculate distances and classify
        for i in range(len(centroidlist)):
            for d in range(len(data_arr)):
                #distance between current pass centroid point and data point
                dist = distance(data_arr[i], data_arr[d])
                if dist < distance_arr[d]:
                    distance_arr[d] = dist
                    #update class for the dist
                    class_arr[d] = i
        #default the centroidlist
        centroidlist = np.full(k, 0)
        #sum up values per class
        for j in range(len(class_arr)):
            index = class_arr[j]
            if index == -1:
                continue
            centroidlist[index] +=data_arr[j]
            class_count[index] +=1
        #new centroids
        for c in range(len(centroidlist)):
            #check classcount 0 condition
            if class_count[c] != 0:
                centroidlist[c] = centroidlist[c]/class_count[c]

    result_dict= my_dictionary()

    for c in range(len(class_arr)):
        result_dict.insert(class_arr[c], data_arr[c])

    print("Kmeans(", k, ")")
    print("centroid list")
    print(centroidlist)
    print("data array")
    print(data_arr)
    print("class array")
    print(class_arr)
    print("results dictionary")
    for k in result_dict.keys():
        v = result_dict.get(k)
        print("key "+str(k))
        print("value len: " + str(len(v)))
        print(v)
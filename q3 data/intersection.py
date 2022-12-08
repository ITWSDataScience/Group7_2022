from sympy import Point, Polygon
import json
import csv
import numpy

group_file = 'data/groups.csv'
target_file = 'data/Federal_Open_Space.json'
fout = open('intersections_computed.json', 'w')

perimeters = []
areas = []
avg_area = 0

intersections = dict()

def try_convert_to_float(string:str):
    try:
        return float(string)
    except:
        return string

def dist(coordA, coordB):
    return numpy.sqrt(numpy.square(coordA[0]-coordB[0])+numpy.square(coordA[1]-coordB[1]))

def get_groups(file):
    groups = []
    dev = 0.05
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row = [try_convert_to_float(e) for e in row if isinstance(try_convert_to_float(e), float)]
            if len(row) > 1:
                row.pop(0)
                groups.append(row)
    group_coordinates = []
    for group in groups:
        p1 = [group[0] + dev, group[1] - dev]
        p2 = [group[0] + dev, group[1] + dev]
        p3 = [group[0] - dev, group[1] + dev]
        p4 = [group[0] - dev, group[1] - dev]
        p5 = [group[0] + dev, group[1] - dev]
        polygon_coordinates = [p1, p2, p3, p4, p5]
        group_coordinates.append(polygon_coordinates)
    return group_coordinates

def get_features(file):
    f1 = open(file)
    data = json.load(f1)
    features = data.get('features', [])
    return features

def get_polygons(file, extra_layers=0):
    features = get_features(file)
    coordinates = []
    total_area = 0
    for feature in features:
        coordinate = feature.get('geometry', dict()).get('coordinates')
        for i in range(0, extra_layers):
            coordinate = coordinate[0]
        coordinates.append(coordinate)
        perimeters.append(feature.get('properties', dict()).get('SHAPE_Length'))
        areas.append(feature.get('properties', dict()).get('SHAPE_Area'))
        total_area += feature.get('properties', dict()).get('SHAPE_Area')
    global avg_area
    avg_area = total_area/len(features)
    print('average area:' + str(avg_area))
    return coordinates

def simplify_polygon(polygon, perimeter):
    new_polygon = [polygon[0]]
    for i in range(1, len(polygon) - 1):
        if dist(new_polygon[-1], polygon[i]) > 0.1 * perimeter:
            new_polygon.append(polygon[i])
    new_polygon.append(polygon[-1])
    return new_polygon
    

def match_intersect():
    # load group coordinates as polygons
    group_coordinates = get_groups(group_file)
    group_polygons = []

    i = 0
    for polygon in group_coordinates:
        points = []
        for coordinate in polygon:
            points.append(Point(coordinate))
        group_polygons.append(Polygon(*points))
        i+=1
        print(f'{i}/{len(group_coordinates)} groups')


    target_coordinates = get_polygons(target_file,2)
    # remove tiny places not relevant
    target_coordinates.pop(0)
    # simplify polygons
    for i in range(0, len(target_coordinates)):
        target_coordinates[i] = simplify_polygon(target_coordinates[i], perimeters[i])
    target_polygons = []

    i = 0
    for polygon in target_coordinates:
        points = []
        for coordinate in polygon:
            #print(str(coordinate))
            points.append(Point(coordinate))
        target_polygons.append(Polygon(*points))
        i+=1
        print(f'{i}/{len(target_coordinates)} targets')

    i = 0
    groupnum = 1
    print(group_polygons[0].intersection(group_polygons[0]))
    for group in group_polygons:
        if groupnum < 100:
            groupnum+=1
            i+=len(target_polygons)
            continue
        for road in target_polygons:
            #print(str(group) + "//" + str(road))
            intersect = group.intersection(road)
            if len(intersect) > 1:
                print(intersect)
                global intersections
                intersections.update({groupnum:intersect})
            i+=1
            groupnum+=1
            print(f'{i}/{len(group_polygons)*len(target_polygons)} intersections computed')

match_intersect()
fout.write(json.dumps(intersections, indent=4))
fout.close()
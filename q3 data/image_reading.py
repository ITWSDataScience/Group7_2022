from PIL import Image
import csv
import json
from collections import OrderedDict

open_space_img = 'data/open_space.png'
diversity_img = 'data/natural_diversity.png'
group_file = 'data/groups.csv'
fout = open('intersections_computed.json', 'w')

groups = []

top_bound = 42.1
bottom_bound = 41
left_bound = -73.7
right_bound = -71.8
res = 4

area_pixel_count = dict()
area_percentage_report = dict()

def try_convert_to_float(string:str):
    try:
        return float(string)
    except:
        return string

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

def convert_to_coordinates(x_pos:float, y_pos:float) -> list:
    x_coord = (right_bound - left_bound) * x_pos + left_bound
    y_coord = (top_bound - bottom_bound) * y_pos + bottom_bound
    return [y_coord, x_coord]

def convert_to_pixels(x_coord, y_coord, imagesize) -> list:
    x_pos = imagesize[0] * ((x_coord - left_bound) / (right_bound - left_bound))
    y_pos = imagesize[1] * ((y_coord - bottom_bound) / (top_bound - bottom_bound))
    return [x_pos, y_pos]

def bounds(polygon:list) -> list:
    top = -10000000
    bottom = 10000000
    left = 10000000
    right = -10000000
    for coordinate in polygon:
        if coordinate[0] < bottom:
            bottom = coordinate[0]
        if coordinate[0] > top:
            top = coordinate[0]
        if coordinate[1] < left:
            left = coordinate[1]
        if coordinate[1] > right:
            right = coordinate[1]
    return [left, right, bottom, top]
        
def get_area_pixels(area, imagesize):
    global groups
    polygon = groups[area-1]
    bound = bounds(polygon)
    topright = convert_to_pixels(bound[1], bound[3], imagesize)
    bottomleft = convert_to_pixels(bound[0], bound[2], imagesize)
    width = topright[0] - bottomleft[0]
    height = topright[1] - bottomleft[1]
    areasize = width * height
    return areasize


def in_area(coordinate:list) -> int:
    i = 1
    for area in get_groups(group_file):
        bound = bounds(area)
        if coordinate[1] >= bound[0]-0.0001 and coordinate[1] < bound[1] and coordinate[0] >= bound[2]-0.0001 and coordinate[0] < bound[3]:
            return i
        i+=1
    return 0

def get_area_occupancy(file):
    img = Image.open(file)
    img_width, img_height = img.size
    print('img size: ' + str(img_width) + ',' + str(img_height))

    for x in range(0, img_width):
        if x % res != 1:
            continue
        for y in range(0, img_height):
            if y % res != 1:
                continue
            x_loc_float = float(x)/img_width
            y_loc_float = float(y)/img_height
            coords = convert_to_coordinates(x_loc_float, y_loc_float)
            area = in_area(coords)
            color = img.getpixel((x,y))
            if (color[0] < 20):
                area_pixel_count.update({area:area_pixel_count.get(area, 0)+1})
                print(f'area: {area}, dark pixels found: {area_pixel_count.get(area)}')
                print(f'progress: {x}/{img_width}')

    for area, count in area_pixel_count.items():
        area_pixels = get_area_pixels(area, img.size)
        area_pixels = area_pixels/(res*res)
        global area_percentage_report
        area_percentage_report.update({area:count/area_pixels})


groups = get_groups(group_file)
get_area_occupancy(diversity_img)
fout.write(json.dumps(area_percentage_report, indent=4))
fout.close()

newimg = Image.new(mode="RGB",size=(600,400),color=(255,255,255))
for area, percent in area_percentage_report.items():
    bound = bounds(groups[area-1])
    print(f'bounds: {bound}')
    topright = convert_to_pixels(bound[1], bound[3],(600,400))
    bottomleft = convert_to_pixels(bound[0], bound[2],(600,400))
    print(f'bounds: {topright},{bottomleft}')
    for x in range(int(bottomleft[0]), int(topright[0])):
        for y in range(int(bottomleft[1]), int(topright[1])):
            value = int(255-percent*255)
            newimg.putpixel((x,y),(value,value,value))
newimg.show()
import math
from functools import reduce
from shapely.geometry import Point, MultiPoint, LineString
from shapely.affinity import rotate as arotate


def is_point(p):
    return hasattr(p, 'x') and hasattr(p, 'y')

def vecFrom2Points(p1, p2):
    return sub(p2, p1)
def dist(p1, p2):
    return p1.distance(p2)
def middle(p1, p2):
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
def linevec(p, vec):
    p1 = Point(p.x + vec.x * 1000, p.y + vec.y * 1000)
    p2 = Point(p.x - vec.x * 1000, p.y - vec.y * 1000)
    return LineString([p1, p2])
def rayvec(p, vec):
    p1 = Point(p.x + vec.x * 1000, p.y + vec.y * 1000)
    return LineString([p, p1])
#rayvec = linevec
def rotateCcw(p, angle):
    return arotate(p, angle, origin=(0,0), use_radians=True)
def rotateCw(p, angle):
    return rotateCcw(p, -angle)

def segment(p1, p2):
    return LineString([p1, p2])

def sub(p1, p2):
    return Point(p1.x - p2.x, p1.y - p2.y)

def angleCcw(p1, p2, p3): #CCW - TODO make sure it is ok
    l1 = sub(p1, p2)
    l3 = sub(p3, p2)
    val = math.atan2(l3.y, l3.x) - math.atan2(l1.y, l1.x)
    return val if val > 0 else 2*math.pi + val

def angleCw(p1, p2, p3): #CW
    return 2*math.pi - angleCcw(p1, p2, p3)

def angle(p1, p2, p3):
    return min(angleCw(p1, p2, p3), angleCcw(p1, p2, p3))

def circle(p, r):
    return p.buffer(r).boundary

def circleCenter(c):
    return c.centroid

def circleFromDiameter(s):
    return circle(s.centroid, s.length)

def intersection(*shapes):
    return reduce(lambda shape1, shape2: shape1.intersection(shape2), shapes)

def get_points(shape):
    if isinstance(shape, MultiPoint):
        return list(shape.geoms)
    elif shape.is_empty:
        return []
    else:
        return [shape.centroid]  # approximate with single point

orth = lambda p: rotateCw(p, math.pi/2)


# @todo return boundaries as well?
def get_search_range(shape):
    return lambda t: shape.interpolate(t)

pi = math.pi
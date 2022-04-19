'''
This is the original backend using SymPy Geometry;
Currently defunct, need to be tested again & integrated.
This backend has the drawback of being much slower, because it uses an analytical,
precise representation of real numbers. OTOH, it provides accurate results.
'''
from sympy import Ray, Point, Line, Segment, intersection, Circle, pi, cos, sin, sqrt, N


circle = Circle

def circleCenter(c):
    return c.center

def circleFromDiameter(s):
    return Circle(s.midpoint, s.length)

def middle1(p1, p3):
    return 2*p3 - p1

def middle(p1, p2):
    return (p1+p2)/2

def vecOpNegate(vec):
    return Point(-vec.x, -vec.y)

def vecFrom2Points(p1, p2):
    return Point(p2.x-p1.x, p2.y-p1.y)

def rayvec(p, vec):
    return Ray(p, Point(p.x+vec.x, p.y+vec.y))

def linevec(p, vec):
    return Line(p, Point(p.x + vec.x, p.y + vec.y))

def rotateCcw(vec, angle=pi/2):
    return vec.rotate(angle)

def rotateCw(vec, angle=pi/2):
    angle = angle % (2*pi)
    angle = 2*pi - angle
    return vec.rotate(angle)

def dist(p1, p2):
    return p1.distance(p2)

def angleCcw(p1, p2, p3): #CCW - TODO make sure it is ok
    l1 = Point(p1.x-p2.x,p1.y-p2.y)
    l3 = Point(p3.x-p2.x,p3.y-p2.y)
    val = math.atan2(l3.y, l3.x) - math.atan2(l1.y, l1.x)
    return val if val > 0 else 2*pi + val

def angleCw(p1, p2, p3): #CW
    return 2*pi - angleCcw(p1, p2, p3)

def angle(p1, p2, p3):
    return min(angleCw(p1, p2, p3), angleCcw(p1, p2, p3))

def smallestAngle(p1, p2, p3):
    l1 = Line(p1,p2)
    l3 = Line(p2,p3)
    return l1.smallest_angle_between(l3)

def ray_domain(r):
    return lambda t: r.points[0] + r.direction * t

def line_domain(l):
    return lambda t: l.points[0] + l.direction * t

def segment_domain(s):
    return lambda t: s.points[0] + s.direction * t

def circle_domain(c): #TODO: I haven't set boundary for the minimize function, but this works
    return lambda t: Point(N(c.radius*sympy.cos(2*pi*t)), N(c.radius*sympy.sin(2*pi*t))) + c.center

def get_domain(entity):
    if type(entity) is sympy.geometry.line.Ray2D:
        return ray_domain(entity)
    elif type(entity) is sympy.geometry.line.Line2D:
        return line_domain(entity)
    elif type(entity) is sympy.geometry.line.Segment2D:
        return segment_domain(entity)
    elif type(entity) is sympy.geometry.ellipse.Circle:
        return circle_domain(entity)
    return None

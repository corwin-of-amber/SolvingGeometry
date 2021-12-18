import sympy
from scipy.optimize import minimize
from sympy import Ray, Point, Line, Segment, intersection, Circle, pi, cos, sin, sqrt
from sympy.abc import x, y
import math
from numpy import finfo, float32
import copy

EPS = finfo(float32).eps

def vecOpNegate(vec):
    return Point(-vec.x, -vec.y)

def vecFrom2Points(p1, p2):
    return Point(p2.x-p1.x, p2.y-p1.y)

def rayVec(p, vec):
    return Ray(p, Point(p.x+vec.x, p.y+vec.y))

def lineVec(p, vec):
    return Line(p, Point(p.x + vec.x, p.y + vec.y))

def rotateCcw(vec, angle):
    return vec.rotate(angle)

def rotateCw(vec, angle):
    angle = angle % (2*pi)
    angle = 2*pi - angle
    return vec.rotate(angle)

def dist(p1, p2):
    return p1.distance(p2)

def angleCcw(p1, p2, p3): #CCW - TODO make sure it is ok
    l1 = Point(p1.x-p2.x,p1.y-p2.y)
    l3 = Point(p3.x-p2.x,p3.y-p2.y)
    val = math.atan2(l1.y, l1.x) - math.atan2(l3.y, l3.x)
    return val if val > 0 else 2*pi + val

def ray_domain(r):
    return lambda t: r.points[0] + r.direction * t

def line_domain(l):
    return lambda t: l.points[0] + l.direction * t

def segment_domain(s):
    return lambda t: s.points[0] + s.direction * t

def circle_domain(c): #TODO: I haven't set boundary for the minimize function, but this works
    return lambda t: Point(c.radius*cos(2*pi*t), c.radius*sin(2*pi*t)) + c.center

def get_domain(entity):
    if type(entity) is sympy.geometry.line.Ray2D:
        return ray_domain(entity)
    elif type(entity) is sympy.geometry.line.Line2D:
        return line_domain(entity)
    elif type(entity) is sympy.geometry.line.Segment2D:
        return segment_domain(entity)
    elif type(entity) is sympy.geometry.ellipse.Circle:
        return circle_domain(entity)


def is_duplicate(known, p):
    for k in known.values():
        if type(k) is not sympy.geometry.point.Point2D:
            continue
        if abs(k.x - p.x) < EPS and abs(k.y - p.y) < EPS:
            return True
    return False

def solveHillClimbing(rules, known):
    print("----------------------------------------------------------------")
    print("called solveHillClimbing with rules:")
    print(rules)
    print("and knwon:")
    print(known)
    rule = rules[0]
    current_rules = copy.deepcopy(rules[1:])
    current_known = copy.deepcopy(known)
    if len(current_rules) == 0: #assert with only 0-dimensions
        print("in assert")
        print(f"to eval = {rule[1]}")
        eval_value = abs(eval(rule[1], {**PRIMITIVES, **current_known}))
        print(f"eval value = {str(eval_value)}")
        return eval_value, current_known
    if len(rule[2]) == 1:
        print("in 1 dimension")
        domain = get_domain(eval(rule[2][0], {**PRIMITIVES, **current_known}))
        def objfunc(p):
            rules_dup = copy.deepcopy(current_rules)
            known_dup = copy.deepcopy(current_known)
            known_dup[rule[1]] = p
            print("***********************************")
            print(f"called objfunc with p = {p.x},{p.y} and rules:")
            print(rules_dup)
            print(f"and known:")
            print(known_dup)
            print("***********************************")
            res = solveHillClimbing(rules_dup,known_dup)[0]
            return res
        solution = minimize(lambda v: abs(objfunc(domain(*v))), 0.0, method="Powell")
        current_known[rule[1]] = domain(*solution.x)
        current_known = solveHillClimbing(current_rules, current_known)[1]
        return solution.fun, current_known

    else: #dimension == 0
        print("in 0 dimension")
        eval_res_list = []
        for i in range(len(rule[2])):
            eval_res_list.append(eval(rule[2][i], {**PRIMITIVES, **current_known}))
        intersection_res = intersection(*eval_res_list)
        if len(intersection_res) == 0:
            return float('inf'), current_known
        if len(intersection_res) == 1:
            current_known[rule[1]] = intersection_res[0] #TODO: check if needs to send inf
            return solveHillClimbing(current_rules, current_known)
        else:
            is_duplicate_0 = is_duplicate(current_known, intersection_res[0])
            is_duplicate_1 = is_duplicate(current_known, intersection_res[1])
            if is_duplicate_0 and not is_duplicate_1:
                current_known[rule[1]] = intersection_res[1]
                return solveHillClimbing(current_rules, current_known)
            elif is_duplicate_1 and not is_duplicate_0:
                current_known[rule[1]] = intersection_res[0]
                return solveHillClimbing(current_rules, current_known)
            else:
                current_known[rule[1]] = intersection_res[0]
                res1, known1 = solveHillClimbing(current_rules, current_known)
                current_known[rule[1]] = intersection_res[1]
                res2, known2 = solveHillClimbing(current_rules, current_known)
                if res1 < res2:
                    return res1, known1
                else:
                    return res2, known2




PRIMITIVES = {
    "sqrt": sqrt,
    "pi": pi,
    "Point": Point,
    "circle": Circle,
    "rayvec": rayVec,
    "linevec": lineVec,
    "segment": Segment,
    "dist": dist,
    "vecOpNegate": vecOpNegate,
    "rotateCw": rotateCw,
    "rotateCcw": rotateCcw,
    "vecFrom2Points": vecFrom2Points,
    "angleCcw": angleCcw,
    "intersection": intersection,
    "ray": Ray
}


def hillClimbing(known, rules):
    in_rules_list = []
    for rule in rules:
        if rule[0] == ":in":
            in_rules_list.append(rule)
        else: #rule[0]=="assert"
            in_rules_list.append(rule)
            known = solveHillClimbing(in_rules_list, known)[1]
            in_rules_list = []
    print("*****************************************************")
    print(known)

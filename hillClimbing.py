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

global_rules = []
global_known = {}


def solveHillClimbing(rules, known):
    print("----------------------------------------------------------------")
    print("called solveHillClimbing with rules:")
    print(rules)
    print("and knwon:")
    print(known)
    rule = rules[0]
    if len(rules) == 1: #assert with only 0-dimensions
        print("in assert")
        to_eval = "abs(" + rule[1] + ")"
        print(f"to eval = {to_eval}")
        eval_value = eval(to_eval, {**PRIMITIVES, **known})
        print(f"eval value = {str(eval_value)}")
        return eval_value, known
    rules.pop(0)
    if len(rule[2]) == 1:
        print("in 1 dimension")
        global global_rules
        global global_known
        global_rules = copy.deepcopy(rules)
        global_known = copy.deepcopy(known)
        domain = get_domain(eval(rule[2][0], {**PRIMITIVES, **known}))
        def objfunc(p):
            global global_rules, global_known
            global_rules2 = copy.deepcopy(global_rules)
            global_known2 = copy.deepcopy(global_known)
            global_known[rule[1]] = p
            print("***********************************")
            print(f"called objfunc with p = {p.x},{p.y} and rules:")
            print(global_rules)
            print(f"and known:")
            print(global_known)
            print("***********************************")
            res = solveHillClimbing(global_rules,global_known)[0]
            global_rules = copy.deepcopy(global_rules2)
            global_known = copy.deepcopy(global_known2)
            return res
        solution = minimize(lambda v: abs(objfunc(domain(*v))), 0.0, method="Nelder-Mead")
        known[rule[1]] = domain(*solution.x)
        known = solveHillClimbing(rules, known)[1]
        return solution.fun, known

    else: #dimension == 0
        print("in 0 dimension")
        eval_string = "intersection("
        for i in range(len(rule[2])):
            eval_string += rule[2][i]
            if i < len(rule[2]) - 1:
                eval_string += ","
        eval_string += ")"
        print(eval_string)
        eval_result = eval(eval_string, {**PRIMITIVES, **known})
        print(eval_result) #TODO: handle empty intersection
        # if type(eval_result[0]) is sympy.geometry.point.Point2D:
        if len(eval_result) == 1:
            known[rule[1]] = eval_result[0] #TODO: check if needs to send inf
            return solveHillClimbing(rules, known)
        else:
            duplicate_0 = False
            duplicate_1 = False
            for k in known:
                if type(k) is not sympy.geometry.point.Point2D:
                    print("error")
                    continue
                if abs(known[k].x - eval_result[0].x) < EPS and abs(known[k].y - eval_result[0].y) < EPS:
                    duplicate_0 = True
                if abs(known[k].x - eval_result[1].x) < EPS and abs(known[k].y - eval_result[1].y) < EPS:
                    duplicate_1 = True
            if duplicate_0 and not duplicate_1:
                known[rule[1]] = eval_result[1]
                return solveHillClimbing(rules, known)
            if duplicate_1 and not duplicate_0:
                known[rule[1]] = eval_result[0]
                return solveHillClimbing(rules, known)
            known[rule[1]] = eval_result[0]
            res1, known1 = solveHillClimbing(rules, known)
            known[rule[1]] = eval_result[1]
            res2, known2 = solveHillClimbing(rules, known)
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

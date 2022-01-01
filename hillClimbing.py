import sympy
from scipy.optimize import minimize
from sympy import Ray, Point, Line, Segment, intersection, Circle, pi, cos, sin, sqrt, N
# from sympy.abc import x, y
import math
from numpy import finfo, float32
import copy

EPS = finfo(float32).eps
global_rules = []
global_not_equal = []
global_not_in = []
global_not_collinear = []


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


def is_duplicate(known, p):
    for k in known.values():
        if type(k) is not sympy.geometry.point.Point2D:
            continue
        if abs(k.x.round(3) - p.x.round(3)) < EPS and abs(k.y.round(3) - p.y.round(3)) < EPS:
            return True
    return False

def is_equal(p1, p2):
    return abs(p1.x.round(3) - p2.x.round(3)) < EPS and abs(p1.y.round(3) - p2.y.round(3)) < EPS

def handle_not_equal(current_known, main_var, intersection_res):
    for tup in global_not_equal:
        if main_var == tup[0] and tup[1] in current_known:
            var = current_known[tup[1]]
        elif main_var == tup[1] and tup[0] in current_known:
            var = current_known[tup[0]]
        else:
            continue

        intersection_0_equal = is_equal(intersection_res[0], var)
        intersection_1_equal = is_equal(intersection_res[1], var)
        if intersection_0_equal and not intersection_1_equal:
            current_known[rule[1]] = intersection_res[1]
            return solveHillClimbing(current_index, current_known)
        if intersection_1_equal and not intersection_0_equal:
            current_known[rule[1]] = intersection_res[0]
            return solveHillClimbing(current_index, current_known)


def solveHillClimbing(rule_index, known):
    rule = global_rules[rule_index]
    print(rule_index, known, rule)
    current_known = copy.deepcopy(known)
    if rule_index == 0: #assert with only 0-dimensions
        print("in assert")
        eval_value = abs(eval(rule[1], {**PRIMITIVES, **current_known}))
        return eval_value, current_known
    current_index = rule_index - 1
    if rule[0] == ":=":
        print("in :=")
        known[rule[1]] = eval(rule[2], {**PRIMITIVES, **current_known})
        return solveHillClimbing(current_index, current_known)
    if len(rule[2]) == 1:
        print("in 1 dimension")
        domain = get_domain(eval(rule[2][0], {**PRIMITIVES, **current_known}))
        def objfunc(p):
            print("in objfunc")
            # known_dup = copy.deepcopy(current_known) #TODO: is it ok to not deep copy here?
            known_dup = known
            known_dup[rule[1]] = p
            res = solveHillClimbing(current_index,known_dup)[0]
            return res
        solution = minimize(lambda v: abs(objfunc(domain(*v))), 0.0, method="Nelder-Mead")
        current_known[rule[1]] = domain(*solution.x)
        current_known = solveHillClimbing(current_index, current_known)[1]
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
            return solveHillClimbing(current_index, current_known)
        else:
            for tup in global_not_equal:
                if rule[1] == tup[0] and tup[1] in current_known:
                    var = current_known[tup[1]]
                elif rule[1] == tup[1] and tup[0] in current_known:
                    var = current_known[tup[0]]
                else:
                    continue

                intersection_0_equal = is_equal(intersection_res[0], var)
                intersection_1_equal = is_equal(intersection_res[1], var)
                if intersection_0_equal and not intersection_1_equal:
                    current_known[rule[1]] = intersection_res[1]
                    return solveHillClimbing(current_index, current_known)
                if intersection_1_equal and not intersection_0_equal:
                    current_known[rule[1]] = intersection_res[0]
                    return solveHillClimbing(current_index, current_known)
            for stmnt in global_not_in:
                if rule[1] == stmnt[0] or rule[1] in stmnt[2]: #TODO: fix this
                    dependency_list = stmnt[2].append(stmnt[0])
                    all_known = True
                    for var in dependency_list:
                        if var not in current_known and var != rule[1]:
                            all_known = False
                            break
                    if not all_known:
                        continue
                    domain = eval(stmnt[1], {**PRIMITIVES, **current_known})
                    if intersection_res[0] in domain and intersection_res[1] not in domain:
                        current_known[rule[1]] = intersection_res[1]
                        return solveHillClimbing(current_index, current_known)
                    if intersection_res[1] in domain and intersection_res[0] not in domain:
                        current_known[rule[1]] = intersection_res[0]
                        return solveHillClimbing(current_index, current_known)

            for tup in global_not_collinear:
                if rule[1] == tup[0] and tup[1] in current_known and tup[2] in current_known:
                    p1, p2 = tup[1], tup[2]
                elif rule[1] == tup[1] and tup[0] in current_known and tup[2] in current_known:
                    p1, p2 = tup[0], tup[2]
                elif rule[1] == tup[2] and tup[1] in current_known and tup[0] in current_known:
                    p1, p2 = tup[1], tup[0]
                else:
                    continue

                collinear_0 = Point.is_collinear(intersection_res[0],current_known[p1],current_known[p2])
                collinear_1 = Point.is_collinear(intersection_res[1], current_known[p1], current_known[p2])

                if collinear_0 and not collinear_1:
                    current_known[rule[1]] = intersection_res[1]
                    return solveHillClimbing(current_index, current_known)
                if collinear_1 and not collinear_0:
                    current_known[rule[1]] = intersection_res[0]
                    return solveHillClimbing(current_index, current_known)

            current_known[rule[1]] = intersection_res[0]
            res1, known1 = solveHillClimbing(current_index, current_known)
            current_known[rule[1]] = intersection_res[1]
            res2, known2 = solveHillClimbing(current_index, current_known)
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


def hillClimbing(known, rules, not_equal, not_in, not_collinear):
    global global_rules, global_not_equal, global_not_in, global_not_collinear
    global_not_equal = not_equal
    global_not_in = not_in
    global_not_collinear = not_collinear
    for rule in rules:
        if rule[0] == ":in" or rule[0] == ":=":
            global_rules.insert(0,rule)
        else: #rule[0]=="assert"
            global_rules.insert(0,rule)
            known = solveHillClimbing(len(global_rules)-1, known)[1]
            for k in known.keys():
                if type(known[k]) is not sympy.geometry.point.Point2D:
                    continue
                known[k] = Point(known[k].x.round(3), known[k].y.round(3))
            global_rules = []
    print("*****************************************************")
    print(known)

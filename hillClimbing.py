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
global_not_intersect_2_segments = []

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

def rayVec(p, vec):
    return Ray(p, Point(p.x+vec.x, p.y+vec.y))

def lineVec(p, vec):
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
            return 1
        if intersection_1_equal and not intersection_0_equal:
            return 0
    return None

def handle_not_in(current_known, main_var, intersection_res):
    for stmnt in global_not_in:
        if main_var == stmnt[0] or main_var in stmnt[2]:
            dependency_list = copy.deepcopy(stmnt[2]).append(stmnt[0])
            all_known = True
            for var in dependency_list:
                if var not in current_known and var != main_var:
                    all_known = False
                    break
            if not all_known:
                continue
            domain = eval(stmnt[1], {**PRIMITIVES, **current_known})
            if intersection_res[0] in domain and intersection_res[1] not in domain:
                return 1
            if intersection_res[1] in domain and intersection_res[0] not in domain:
                return 0
    return None

def handle_not_collinear(current_known, main_var, intersection_res):
    for tup in global_not_collinear:
        if main_var == tup[0] and tup[1] in current_known and tup[2] in current_known:
            p1, p2 = tup[1], tup[2]
        elif main_var == tup[1] and tup[0] in current_known and tup[2] in current_known:
            p1, p2 = tup[0], tup[2]
        elif main_var == tup[2] and tup[1] in current_known and tup[0] in current_known:
            p1, p2 = tup[1], tup[0]
        else:
            continue

        collinear_0 = Point.is_collinear(intersection_res[0], current_known[p1], current_known[p2])
        collinear_1 = Point.is_collinear(intersection_res[1], current_known[p1], current_known[p2])

        if collinear_0 and not collinear_1:
            return 1
        if collinear_1 and not collinear_0:
            return 0
    return None


def handle_not_intersect_2_segments(current_known, main_var, intersection_res):
    for stmnt in global_not_intersect_2_segments:
        if main_var in stmnt:
            all_known = True
            for var in stmnt:
                if var not in current_known and var != main_var:
                    all_known = False
                    break
            if not all_known:
                continue
            points_list_0 = []
            points_list_1 = []
            for item in stmnt:
                if item in current_known:
                    points_list_0.append(current_known[item])
                    points_list_1.append(current_known[item])
                else: # var == main_var
                    points_list_0.append(intersection_res[0])
                    points_list_1.append(intersection_res[1])

            s1 = Segment(points_list_0[0], points_list_0[1])
            s2 = Segment(points_list_0[2], points_list_0[3])
            intersection_0 = intersection(s1,s2)

            s3 = Segment(points_list_1[0], points_list_1[1])
            s4 = Segment(points_list_1[2], points_list_1[3])
            intersection_1 = intersection(s3, s4)

            if len(intersection_0) > 0 and len(intersection_1) == 0:
                return 1
            if len(intersection_1) > 0 and len(intersection_0) == 0:
                return 0
    return None



def solveHillClimbing(rule_index, known):
    rule = global_rules[rule_index]
    current_known = copy.deepcopy(known)
    if rule_index == 0: #assert with only 0-dimensions
        #print("in assert with rule = ", rule, "and known = ", known)
        eval_value = abs(eval(rule[1], {**PRIMITIVES, **current_known}))
        return eval_value, current_known
    current_index = rule_index - 1
    if rule[0] == ":=":
        current_known[rule[1]] = eval(rule[2], {**PRIMITIVES, **current_known})
        return solveHillClimbing(current_index, current_known)
    if len(rule[2]) == 1:
        print("in dimension 1 with rule = ", rule, "and known = ", known)
        if "orth" in rule[2][0]:
            rule_cw = rule[2][0].replace("orth", "rotateCw")
            rule_ccw = rule[2][0].replace("orth", "rotateCcw")
            domains = [get_domain(eval(rule, {**PRIMITIVES, **current_known}))
                       for rule in [rule_cw, rule_ccw]]
        else:
            domains = [get_domain(eval(rule[2][0], {**PRIMITIVES, **current_known}))]
        
        solutions = []
        for domain in domains:
            def objfunc(p):
                #print("in objefunc with p:", p, "and known:", known)
                # known_dup = copy.deepcopy(current_known) #TODO: is it ok to not deep copy here?
                known_dup = known
                known_dup[rule[1]] = p
                res = solveHillClimbing(current_index, known_dup)[0]
                return res
            solution = minimize(lambda v: abs(objfunc(domain(*v))), 0.0, method="Nelder-Mead")
            current_known[rule[1]] = domain(*solution.x)
            current_known = solveHillClimbing(current_index, current_known)[1]
            solutions.append((solution.fun, current_known))

        return min(solutions, key=lambda tup: tup[0])

    else: #dimension == 0
        #print("in dimension 0 with rule = ", rule, "and known = ", known)
        eval_res_list = [[]]
        for i in range(len(rule[2])):
            if "orth" in rule[2][i]:
                for j in range(len(eval_res_list)):
                    li = eval_res_list[j]
                    new_li = copy.deepcopy(li)
                    li.append(eval(rule[2][i].replace("orth", "rotateCw"), {**PRIMITIVES, **current_known}))
                    new_li.append(eval(rule[2][i].replace("orth", "rotateCcw"), {**PRIMITIVES, **current_known}))
                    eval_res_list.append(new_li)
            else:
                for li in eval_res_list:
                    li.append(eval(rule[2][i], {**PRIMITIVES, **current_known}))
        intersection_res_list = [intersection(*li) for li in eval_res_list]
        min_ret = math.inf
        min_rule_res = None
        for intersection_res in intersection_res_list:
            #print("with p = ", intersection_res)
            if len(intersection_res) == 0:
                continue
            if len(intersection_res) == 1:
                current_known[rule[1]] = Point(intersection_res[0].x.round(10),intersection_res[0].y.round(10))
                ret1, _= solveHillClimbing(current_index, current_known)
                if ret1 < min_ret:
                    min_ret, min_rule_res = ret1, current_known[rule[1]]
                continue
            else:
                not_equal_res = handle_not_equal(current_known, rule[1], intersection_res)
                if not_equal_res is not None:
                    current_known[rule[1]] = intersection_res[not_equal_res]
                    ret1, _= solveHillClimbing(current_index, current_known)
                    if ret1 < min_ret:
                        min_ret, min_rule_res = ret1, current_known[rule[1]]
                    continue
                not_in_res = handle_not_in(current_known, rule[1], intersection_res)
                if not_in_res is not None:
                    current_known[rule[1]] = intersection_res[not_in_res]
                    ret1, _= solveHillClimbing(current_index, current_known)
                    if ret1 < min_ret:
                        min_ret, min_rule_res = ret1, current_known[rule[1]]
                    continue
                not_collinear_res = handle_not_collinear(current_known, rule[1], intersection_res)
                if not_collinear_res is not None:
                    current_known[rule[1]] = intersection_res[not_collinear_res]
                    ret1, _= solveHillClimbing(current_index, current_known)
                    if ret1 < min_ret:
                        min_ret, min_rule_res = ret1, current_known[rule[1]]
                    continue
                not_intersect_2_segments_res = handle_not_intersect_2_segments(current_known, rule[1], intersection_res)
                if not_intersect_2_segments_res is not None:
                    current_known[rule[1]] = intersection_res[not_intersect_2_segments_res]
                    ret1, _= solveHillClimbing(current_index, current_known)
                    if ret1 < min_ret:
                        min_ret, min_rule_res = ret1, current_known[rule[1]]
                    continue

                current_known[rule[1]] = intersection_res[0]
                res1, known1 = solveHillClimbing(current_index, current_known)
                current_known[rule[1]] = intersection_res[1]
                res2, known2 = solveHillClimbing(current_index, current_known)
                if res1 < min_ret:
                    min_ret, min_rule_res = res1, intersection_res[0]
                if res2 < min_ret:
                    min_ret, min_rule_res = res2, intersection_res[1]
        current_known[rule[1]] = min_rule_res
        return solveHillClimbing(current_index, current_known)


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
    "angleCw": angleCw,
    "angle": angle,
    "smallestAngle": smallestAngle,
    "intersection": intersection,
    "circleCenter": circleCenter,
    "circleFromDiameter": circleFromDiameter,
    "middle": middle,
    "middle1": middle1
}


def hillClimbing(known, rules, not_equal, not_in, not_collinear, not_intersect_2_segments):
    global global_rules, global_not_equal, global_not_in, global_not_collinear, global_not_intersect_2_segments
    global_not_equal = not_equal
    global_not_in = not_in
    global_not_collinear = not_collinear
    global_not_intersect_2_segments = not_intersect_2_segments
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
    #print("*****************************************************")
    return known
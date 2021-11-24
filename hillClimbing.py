import sympy
from scipy.optimize import minimize
from sympy import *
import numpy as np

#keyword arguments
def calcOneSiteUserFunction(x1,y1,a1,b1, user_function):
    codeObejct = compile(user_function, 'sumstring', 'exec')
    loc = {"x": x1, "y": y1, "a": a1, "b": b1}
    exec(codeObejct, globals(), loc)
    return loc['result']

def myInput():
    a = Point(0,0)
    b = Point(0,6)
    return [{"missing points": ["o", "c", "d", "e", "f"]},
            {"name": "a", "object": a},
            {"name": "b", "object": b},
            {"name": "o", "in": ["Circle(a,a.distance(b))","Circle(b,a.distance(b))"]},
            {"name": "c", "in": ["Circle(o,o.distance(b))","Ray(o,angle=Line(a,o).angle_between(Line(o,b))).rotate(pi/3)"]},
            {"name": "d", "in": ["Circle(o,o.distance(b))","Ray(o,angle=Line(a,o).angle_between(Line(o,b))).rotate(0)"]},
            {"name": "e", "in": ["Circle(o,o.distance(b))","Ray(o,angle=Line(a,o).angle_between(Line(o,b))).rotate(-pi/3)"]},
            {"name": "f", "in": ["Circle(o,o.distance(b))","Ray(o,angle=Line(a,o).angle_between(Line(o,b))).rotate(-(2*pi)/3)"]},
            {"name": "Assert", "object": ["Line(a,o).angle_between(Line(o,b))","Line(f,o).angle_between(Line(o,a))"]}]

# def myFunction(arg):
#     x, y = arg
#     X = Point(0, 0)
#     Z = Point(0, 6)
#     Y = Point(x, y)
#     result = abs(X.distance(Y)-6) #maybe use **2
#     result += abs(Z.distance(Y)-6)
#     return result

def perpBisect(a,b,x1,y1):
    s = Segment(a,b)
    if s.slope == 0:
        x,y = s.midpoint.coordinates
        l = Line(s.midpoint, Point(x,y+1))
    else:
        l = Line(s.midpoint, slope=-Segment(a,b).slope)
    a,b,c = l.coefficients
    if b==0:
        return Point(-c/a, y1)
    else:
        return Point(x1, -a/b*x1 -c/b)

def myFunction2(arg):
    x,y = arg
    res = 0
    # given a
    a = Point(0,1)
    #given b
    b = Point(6,1)
    #given o in perp bisect(a,b)
    o = Point(x,y)
    coordinates = perpBisect(a, b, x, y).coordinates
    res += (o.coordinates[0] - coordinates[0])**2 + (o.coordinates[1] - coordinates[1])**2
    #given r=|ob|
    r = o.distance(b)
    # given alpha=angle(a,o,b)
    alpha=Line(a,o).angle_between(Line(o,b))
    #c in circle(o,r) and ray(o,rotate(b-o,alpha))
    c_intersections = intersection(Circle(o,r), Ray(o,angle=(Line(b,o).angle_between(Line(Point(0,0),Point(1,0)))+alpha)))
    for c in c_intersections:
        # d in circle(o,r) and ray(o,rotate(c-o,alpha))
        d_intersections = intersection(Circle(o, r), Ray(o, angle=(Line(c, o).angle_between(Line(Point(0, 0), Point(1, 0))) + alpha)))
        for d in d_intersections:
            # e in circle(o,r) and ray(o,rotate(d-o,alpha))
            e_intersections = intersection(Circle(o, r), Ray(o, angle=(Line(d, o).angle_between(Line(Point(0, 0), Point(1, 0))) + alpha)))
            for e in e_intersections:
                # f in circle(o,r) and ray(o,rotate(e-o,alpha))
                f_intersections = intersection(Circle(o, r), Ray(o, angle=(Line(e, o).angle_between(Line(Point(0, 0), Point(1, 0))) + alpha)))
                for f in f_intersections:
                    pass
                    #assert angle(f,o,a)=alpha
                    #use min()

def myFunction(arg):
    x,y = arg
    a = Point(0,1)
    b = Point(6,1)
    o = Point(x,y)
    coordinates = perpBisect(a, b, x, y).coordinates
    res = (o.coordinates[0] - coordinates[0])**2 + (o.coordinates[1] - coordinates[1])**2
    print(f"coordinates o(x,y)={o}, from bisept={coordinates}")
    intersections = intersection(Circle(o,o.distance(b)), Ray(o,angle=(Line(a,o).angle_between(Line(o,b))+(2*pi)/3)))
    if len(intersections) == 0:
        print("ERROR")
        print(Circle(o,o.distance(b)))
        print(Ray(o,angle=(Line(a,o).angle_between(Line(o,b))+(2*pi)/3)))
        return #error
    elif len(intersections) == 1:
        print(Circle(o, o.distance(b)))
        print(Ray(o, angle=(Line(a, o).angle_between(Line(o, b)) - (2 * pi) / 3)))
        return res + (Line(a,o).angle_between(Line(o,b))-Line(intersections[0],o).angle_between(Line(o,a)))**2
    else:
        intersectionResult = (Line(a,o).angle_between(Line(o,b))-Line(intersections[0],o).angle_between(Line(o,a)))**2
        for f in intersections:
            intersectionResult = min(intersectionResult,(Line(a,o).angle_between(Line(o,b))-Line(f,o).angle_between(Line(o,a)))**2)
        return res + intersectionResult









# --- these are general definitions

def vecOpNegate(vec):
    return Point(-vec.x, -vec.y)

def vecFrom2Points(p1, p2):
    return Point(p2.x-p1.x, p2.y-p1.y)

def rotateCcw(vec, angle):
    return vec.rotate(angle)

def rotateCw(vec, angle):
    angle = angle % (2*pi)
    angle = 2*pi - angle
    return vec.rotate(angle)

def dist(p1, p2):
    return p1.distance(p2)

def angleCcw(p1, p2, p3): #CCW - TODO
    return Line(p2,p1).angle_between(Line(p2,p3))

def ray_domain(r):
    return lambda t: r.points[0] + r.direction * t

def line_domain(l):
    return lambda t: l.points[0] + l.direction * t

def segment_domain(s):
    return lambda t: s.points[0] + s.direction * t

def circle_domain(c):
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

def solve(domain, objfunc):
    solution = minimize(lambda v: abs(objfunc(domain(*v))), 0.0, method="Nelder-Mead")
    return domain(*solution.x)

def solveWithoutHillClimbing(rule, domain, known):
    min_value = float("inf")
    min_point = None
    print(known)
    for point in domain:
        known[rule[1]] = point
        temp_value = eval(f'abs({rule[2]})', {**PRIMITIVES, **known})
        if temp_value < min_value:
            min_point = point
            min_value = temp_value
    return min_point

PRIMITIVES = {
    "sqrt": sqrt,
    "Point": Point,
    "circle": Circle,
    "rayvec": Ray,
    "linevec": Line,
    "segment": Segment,
    "dist": dist,
    "vecOpNegate": vecOpNegate,
    "rotateCw": rotateCw,
    "rotateCcw": rotateCcw,
    "vecFrom2Points": vecFrom2Points,
    "angleCcw": angleCcw,
    "intersection": intersection
}


def hillClimbing(known, rules):

    #
    # domain_c = get_domain(eval(stmts[0][2], {**PRIMITIVES, **known}))
    # objfunc_c = eval(f'lambda {stmts[0][1]}: {stmts[1][1]}', {**PRIMITIVES, **known})
    # known['c'] = solve(domain_c, objfunc_c)
    # print(known)
    # return

    domains = {}
    for rule in rules:
        print(rule)
        if rule[0] == ":in":
            if len(rule[2]) == 1:
                domains[rule[1]] = get_domain(eval(rule[2][0], {**PRIMITIVES, **known}))
            else:
                eval_string = "intersection("
                for i in range(len(rule[2])):
                    eval_string += rule[2][i]
                    if i < len(rule[2]) -1:
                        eval_string += ","
                eval_string += ")"
                print(eval_string)
                eval_result = eval(eval_string, {**PRIMITIVES, **known})
                if type(eval_result[0]) is sympy.geometry.point.Point2D:
                    domains[rule[1]] = eval_result
                else:
                    domains[rule[1]] = get_domain(eval(eval_string[0], {**PRIMITIVES, **known}))
        # elif rule[0] == ":=":

        else: #rule[0] == "assert"
            if type(domains[rule[1]]) is list:
                # list_string = ""
                # for i in range(len(domains[rule[1]])):
                #     list_string += "Point(" + str(domains[rule[1]][i].x) + ", " + str(domains[rule[1]][i].y) + ")"
                #     if i < (len(domains[rule[1]]) - 1):
                #         list_string += ", "
                # print(f'lambda {rule[1]}: min({list_string})')
                # objfunc = eval(f'lambda {rule[1]}: min({list_string})', {**PRIMITIVES, **known})
                known[rule[1]] = solveWithoutHillClimbing(rule, domains[rule[1]], known)
            else:
                objfunc = eval(f'lambda {rule[1]}: {rule[2]}', {**PRIMITIVES, **known})
                known[rule[1]] = solve(domains[rule[1]], objfunc)

    print(known)


    # # c :∈ ray(a, b)
    # domain_c = ray_domain(eval(rules[0][2], {**PRIMITIVES, **known})) #string eval, globals, locals
    # # assert dist(a, c) - dist(a, b)   [depends on c]
    # objfunc_c = eval(f'lambda {rules[0][1]}: {rules[1][1]}', {**PRIMITIVES, **known})
    # known['c'] = solve(domain_c, objfunc_c)
    # print(known)


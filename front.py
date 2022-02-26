import re
from sympy import Point, pi
from  utils import is_number, deg_to_rad

SAMPLES = {
    "test": ["angle(a,b,c)=90"],
    "triangle": ["dist(X,Y)=136",
                "X!=Y",
                "X=Point(0,0)",
                "dist(Z,Y)=136",
                "X!=Z",
                "Z=Point(136,0)",
                        "?(Y)"],
    "myTriangle": ["?(W)",
                    "?(Y)",
                    "X=Point(0, 0)",
                    "Z=Point(1, 0)",
                    "W!=X",
                    "dist(X,Y)=1",
                    "dist(Z,Y)=1",
                    "dist(W,Y)=1",
                    "dist(Z,W)=1"
                    ],
    "square": ["dist(A,B)=d",
               "dist(B,C)=d",
               "dist(C,D)=d",
               "dist(D,A)=d",
               "A!=B",
               "A!=C",
               "B!=D",
               "angle(A,D,C)=90",
               "A=Point(0,0)",
               "B=Point(1,0)",
               "?(C)",
               "?(D)"
    ],
    "square2": [#"MakeLine(A, B)",
                #"MakeLine(B, C)",
                "dist(A,B)=1",
                "dist(B,C)=1",
                "dist(C,D)=1",
                "angle(A,B,C)=90",
                "A=Point(0,0)",
                "B=Point(1,0)",
                "?(C)", "?(D)"
    ],
    "pentagon": ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d",
                "dist(D,E)=d", "dist(E,A)=d",
                "angleCcw(A,B,C)=a", "angleCcw(B,C,D)=a",
                "angleCcw(C,D,E)=a", "angleCcw(D,E,A)=a",
                "angleCcw(E,A,B)=a",
                # TODO: Implement intersect2segmentsQ, realnot
                #"intersect2segmentsQ(A,B,C,D,q)",
                #"realnot(q)",
                "D!=A", "A!=C",
                "A=Point(0, 0)", "C=Point(2,0)",
                "?(B)", "?(D)", "?(E)"],
    "pentagon2": ["d=1.23606",
                "dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d",
                "dist(D,E)=d", "dist(E,A)=d",
                "angleCcw(A,B,C)=108", "angleCcw(B,C,D)=108",
                "angleCcw(C,D,E)=108", "angleCcw(D,E,A)=108",
                "angleCcw(E,A,B)=108",
                # TODO: Implement intersect2segmentsQ, realnot
                #"intersect2segmentsQ(A,B,C,D,q)",
                #"realnot(q)",
                "D!=A", "A!=C",
                "A=Point(0, 0)", "C=Point(2,0)",
                "?(B)", "?(D)", "?(E)"],
    "9gon": ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d",
            "dist(D,E)=d", "dist(E,F)=d", "dist(F,G)=d",
            "dist(G,H)=d", "dist(H,I)=d", "dist(I,A)=d", "angleCcw(A,B,C)=a",
            "angleCcw(B,C,D)=a", "angleCcw(C,D,E)=a",
            "angleCcw(D,E,F)=a", "angleCcw(E,F,G)=a",
            "angleCcw(F,G,H)=a", "angleCcw(G,H,I)=a",
            "angleCcw(H,I,A)=a", "angleCcw(I,A,B)=a",
            "A=Point(0,0)", "B=Point(1,1)", "D!=A",
            "?(C)", "?(D)", "?(E)", "?(F)", "?(G)", "?(H)", "?(I)"
            #realont(q1), realnot(q2), intersect_2_segments
            ],
    "square-in-square":
          ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d", "dist(D,A)=d", "A!=B", "A!=C", "B!=D",
           "angleCcw(A,D,C)=90",
           "segment(A,B,AB)","in(E,AB)", "dist(A,E)=15",
           "segment(B,C,BC)","in(F,BC)","!in(F,CD)",
           "segment(C,D,CD)", "in(G,CD)", "!in(G,DA)",
           "segment(D,A,DA)", "in(H,DA)",
           "angle(E,F,G)=90",
           "angle(F,G,H)=90",
           "angle(G,H,E)=90",
           "A=Point(0,0)", "B=Point(60,0)","?(C)", "?(D)"
           "?(E)", "?(F)", "?(G)", "?(H)"
           ],
   "square-in-triangle":
            ["A=Point(0,0)", "B=Point(2,0)",
            "C=Point(1,1)",
             "segment(A,B,AB)", "in(D,AB)",
             "in(E,AB)",
             "segment(A,C,AC)", "in(F,AC)",
             "segment(B,C,BC)", "in(G,BC)",
             "angle(D,E,F,90)",
             "angle(E,D,G,90)",
             "angle(D,G,F,90)",
             "dist(D,E,d)", "dist(E,F,d)",
             "D!=E", "D!=A", "D!=B", "E!=B", "E!=A",
             "!colinear(A,C,D)",
             "!colinear(A,B,C)",
             "!colinear(D,E,F)", "!colinear(D,E,C)","!colinear(E,F,C)",
             "!colinear(D,G,B)",
#                 "[!colinear](G,A,C)",
             #"dist(E,D,x) & dist(E,F,x)",
             "?(D)", "?(E)", "?(F)","?(G)"
             ],
    'tut:middle-1': # This is where I got so far (it doesnt work)
            ["segment(A,B,AB)", "in(E,AB)", "dist(A,E,a)",
            "dist(E,B,a)", "segment(B,C,BC)", "in(D,BC)",
            "dist(B,D,b)", "dist(D,C,b)",
             "segment(C,A,CA)", "in(F,CA)", "dist(C,F,c)",
             "dist(F,A,c)", "dist(A,B,d)", "dist(A,C,d)",
            "A!=D",
            "A=Point(2,2)","B=Point(0,0)",
            "?(C)", "?(D)", "?(E)", "?(F)"],
     'SAT:angles-1': [
            "dist(O,A,100)", "dist(O,R,100)",
            "O!=B", "O!=L",
            "angleCcw(B,O,A,40)", "angleCcw(R,O,L,25)",
             "middle(L,A,O)", "middle(K,B,O)",
             "O=Point(0,0)", "B=Point(10, 0)",
             #TODO: Make known an option"known(O)", "known(B)", 
             "?(A)", "?(R)", "?(L)", "?(K)"],
     'SAT:clover': [
            "angleCcw(D,A,B,50)", "angleCcw(C,D,A,45)",
            "angleCcw(A,B,F,50)", "angleCcw(B,F,E,60)",
           "angleCcw(F,E,C,90)", "segment(A,B,AB)",
            "segment(C,D,CD)", "in(P,AB)", "in(P,CD)",
            "C!=D",
            # & [!=](AB,CD)",
           "segment(E,F,EF)", "in(P,EF)", # & [!=](AB,EF) & [!=](CD,EF)",
           "A=Point(0,0)", "B=Point(5, 0)",
           "?(C)", "?(D)", "?(E)", "?(F)", "?(P)"]
    }
# User writes: 
# dist(A,B) = 10
# A = Point(1,5)
# A != B
# angleCcw(A,B,C) = pi
# angleCw
# ?(D)
# Format of synthesis part:
# dist, known, neq, point?, angleCCW?angle_ccw, output
# Statement(predicate="neq", vars=("A",  "B"))
# Statement(predicate="angle", vars=("A", "D", "C", "a"))
# Statement(predicate="known", vars=("a", pi))
# Statement(predicate"output", vars=("A",  "B", ...))
# Statement(predicate="rightAngle", vars=("A", "D", "C"))
# Notice the exception in case of 90 degrees angle, where we should turn angle into 'rightAngle'
# This class is the way to pass the input to the synthesis part
class Statement:
    def __init__(self, predicate, vars):
        self.predicate = predicate
        self.vars = tuple(vars)
    
    def is_ready(self, known):
        if self.predicate == "known":
            return True
        for var in self.vars:
            # TODO: Shouldnt use this condition
            assert(type(var) == str)
            if var not in known:
                return False
        return True
    
    def __str__(self):
        return "{}{}".format(self.predicate, self.vars)
        

def parse_dl(input_file):
    # Parse input (right now in the form of dl file)
    f = open(input_file, "r")
    input_lines = f.read().split("\n")
    f.close()
    statements = []
    for s in input_lines[1:]: # the first line is the include
        if s == "":
            continue
        if s.startswith("//"):
            continue;
        tmp = re.compile("(\w+)").findall(s)
        predicate = tmp[0]
        predicate = predicate[0].lower() + predicate[1:]
        vars = []
        for i in tmp[1:]:
            vars.append(i)
        statements.append(Statement(predicate, vars))
    return statements
    
# A dict of the form num: var_name, that represents numbers we converted to variable.
numbers = {}

def get_number_as_var(num):
    if num in numbers:
        return numbers[num]
    else:
        new_var = "num_" + str(len(numbers))
        numbers[num] = new_var
        return new_var

    
POSSIBLE_PREDICATES = ["segment",  "middle", "angle","angleCcw", "angleCw", "notColinear","dist", "in", "known", "notIn", "neq", "output"]

# Api for Statement
# All functions gets strings as parameters
def segment(a, b, name_of_segment):
    return Statement("Segment", vars=[a, b, name_of_segment])

def middle(a, b, c):
    return Statement("Middle", vars=[a, b, c])

def _angle_helper(angle_name, a,  b, c, angle_val):
    s = []
    if angle_val == "90":
        s.append(Statement("rightAngle", vars=[a, b, c]))
        return s
    if is_number(angle_val):
        angle_val = get_number_as_var(deg_to_rad(angle_val))
    s.append(Statement(angle_name,
                        vars=[
                                a, b, c, angle_val
                            ]))
    return s
    
def angle(a, b, c, angle_val):
    return _angle_helper("angle", a,  b, c, angle_val)
    
def angleCcw(a, b, c, angle_val):
    return _angle_helper("angleCcw", a,  b, c, angle_val)
        
def angleCw(a, b, c, angle_val):
    return _angle_helper("angleCw", a,  b, c, angle_val)
        
def notColinear(a, b, c):
    return Statement("notColinear", vars=[a, b, c])
        
def dist(p1, p2, dist_p1_p2):
    if is_number(dist_p1_p2):
        dist_p1_p2 = get_number_as_var(dist_p1_p2)
    s = [Statement("dist", vars=[p1, p2, dist_p1_p2])]
    return s

# Notice this is a patch - because in cant be a name for a function
def in_func(a, domain):
    return Statement("in", vars=[a, domain])

# TODO: Perhaps add the option  for known without a value (and value will be generated)
def known(var, val):
    return Statement("known",  vars=[var, eval(val)])

def notIn(a, domain):
    return Statement("notIn", vars=[a, domain])

def neq(a, b):
    return Statement("neq", vars=[a, b])

def output(var):
    return Statement("output", vars=[var])

def parse_predicate_with_params(exp_lhs, exp_rhs=None):
    """
    exp_lhs is of the form: predicate(var1, var2, ...).
    exp_rhs (if exists) if the exp value.
    Return a string in a form ready to eval
    """
    res = re.compile("(!?\w+)\(.*\)").findall(exp_lhs)
    if len(res) == 0:
        return
    predicate = res[0]
    if predicate.startswith("!"):
        predicate = "not{}".format(predicate[1].upper() + predicate[2:])
    if predicate and (predicate in POSSIBLE_PREDICATES):
        if predicate == "in":
            predicate = "in_func"
        vars = re.compile("\w+\((.*)\)").findall(exp_lhs)[0].split(",")
        if exp_rhs:
            vars.append(exp_rhs)
        return_str = predicate +  "("
        for var in vars:
            return_str += "'{}',".format(var)
        return_str += ")"
        return return_str
    raise NotImplementedError("statement: {} isn't implemented".format(exp_lhs))

def parse_line(line):
    line = line.strip("\r")
    if line.startswith("?"):
        # Each output var should be  in a seperated  line as well
        output_var = re.compile("\?\((\w+)\)").findall(line)[0]
        return output(output_var)
    if "!=" in line:
        vars = line.split("!=")
        assert(len(vars) == 2)
        return neq(vars[0],  vars[1])
    if "=" in line:
        left, right = line.split("=")
        str_to_eval = parse_predicate_with_params(left, right)
        if not str_to_eval:
            # In this case we have: X=something
            # TODO: Maybe use the eval in the numeric part instead
            return known(left, right)
        return eval(str_to_eval)
    else:
        str_to_eval = parse_predicate_with_params(line)
        return eval(str_to_eval)
    
def parse_free_text(lines):
    # Get input after it was split into lines, in a format similar to the spec in the appendix.
    # Assumes no unnessacary spaces, tabs or whatever
    # with each new line contains one statement
    # TODO: replace numbers  with constants, replace 90 degrees angle with rightAngle
    # TODO: There is still some work here (handle spaces, indicutive errors, etc)
    statements = [] # a list of objects from type Statement
    for line in lines:
        try:
            new_statements = parse_line(line)
        except Exception as e:
            print("Failed parsing in line: " + line)
            raise e
        if type(new_statements) == list:
            statements += new_statements
        else:
            statements.append(new_statements)
    
    # Add variables that were casted from numbers as Known statements
    for numeric_val, var_name in numbers.items():
        statements.append(known(var_name, numeric_val))
    return statements

def main(exercise_name=None):
    # If exercise_name is None - get input from user
    # Otherwise - use a builtin sample
    if exercise_name:
        lines = SAMPLES[exercise_name]
    else:
        lines = input("Enter input: ").split("\n")
    print("In front - about to create statements")
    #statements = build_statements(parse_free_text(lines))
    statements = parse_free_text(lines)
    print("statements are: ")
    for s in statements:
        print(s)
    print()
    return statements
    
    # souffle_main_dir = "souffleFiles"
    # souffle_in_dir = os.path.join(souffle_main_dir, exercise_name)    
    #return parse_dl(os.path.join(souffle_in_dir,exercise_name + ".dl"))
        
     
if __name__ == "__main__":
    main("triangle")

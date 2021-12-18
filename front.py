import re
from sympy import Point, pi
from  utils import is_number, deg_to_rad

SAMPLES = {
    "triangle": ["dist(X,Y)=136",
                "X!=Y",
                "X=Point(0,0)",
                "dist(Z,Y)=136",
                "X!=Z",
                "Z=Point(136,0)",
                "136=136",
                        "?(Y)"],
    "myTriangle": ["?(W)",
                    "?(Y)",
                    "X=Point(0, 0)",
                    "Z=Point(1, 0)",
                    "Dist=1",
                    "W!=X",
                    "dist(X,Y)=Dist",
                    "dist(Z,Y)=Dist",
                    "dist(W,Y)=Dist",
                    "dist(Z,W)=Dist"
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
                "dist(A,B)=d",
                "dist(B,C)=d",
                "dist(C,D)=d",
                "angle(A,B,C)=90",
                "A=Point(0,0)",
                "B=Point(1,0)",
                "d=1",
                "?(C)"
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
                "A=Point(0, 0)", "C=Point(1,0)",
                "?(B)", "?(D)", "?(E)"],
    "pentagon2": ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d",
                "dist(D,E)=d", "dist(E,A)=d",
                "angleCcw(A,B,C)=a", "angleCcw(B,C,D)=a",
                "angleCcw(C,D,E)=a", "angleCcw(D,E,A)=a",
                "angleCcw(E,A,B)=a",
                # TODO: Implement intersect2segmentsQ, realnot
                #"intersect2segmentsQ(A,B,C,D,q)",
                #"realnot(q)",
                "D!=A", "A!=C",
                "A=Point(0, 0)", "C=Point(1,0)",
                "a=deg_to_rad(120)", # TODO: Should make this interface better for the user
                "d=1",
                "?(B)", "?(D)", "?(E)"],
    "9gon": ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d",
            "dist(D,E)=d", "dist(E,F)=d", "dist(F,G)=d",
            "dist(G,H)=d", "dist(I,I)=d", "angleCcw(A,B,C)=a",
            "angleCcw(B,C,D)=a", "angleCcw(C,D,E)=a",
            "angleCcw(D,E,F)=a", "angleCcw(E,F,G)=a",
            "angleCcw(F,G,H)=a", "angleCcw(G,H,I)=a",
            "angleCcw(H,I,A)=a", "angleCcw(I,A,B)=a",
            "A=Point(0,0)", "B=Point(1,0)", "D!=A",
            "?(C)", "?(D)", "?(E)", "?(F)", "?(G)", "?(H)", "?(I)"
            #realont(q1), realnot(q2), intersect_2_segments
            ],
    'square-in-square':
          ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d", "dist(D,A)=d", "A!=B", "A!=C", "B!=D",
           "angleCcw(A,D,C)=90",
           "segment(A,B,AB)","in(E,AB)", "dist(A,E)=15",
           "segment(B,C,BC)","in(F,BC)","!in(F,CD)",
           "segment(C,D,CD)", "in(G,CD)", "!in(G,DA)",
           "segment(D,A,DA)", "in(H,DA)",
           "angle(E,F,G)=90",
           "angle(F,G,H)=90",
           "angle(G,H,E)=90",
           "A=Point(0,0)", "B=Point(1,0)","?(C)", "?(D)"
           "?(E)", "?(F)", "?(G)", "?(H)"
           ],
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
            if is_number(var):
                continue
            if var not in known:
                return False
        return True
    
    # This is just for convenience
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
    
POSSIBLE_PREDICATES = ["segment",  "angle","angleCcw", "angleCw", "dist", "in", "known", "not_in", "neq", "output"]

# Api for Statement
# All functions gets strings as parameters

def segment(a, b, name_of_segment):
    return Statement("Segment", vars=[a, b, name_of_segment])

def _angle_helper(angle_name, a,  b, c, angle_val):
    s = [
        #Statement("MakeLine", vars=[a, b]),
        #Statement("MakeLine", vars=[b, c])
        Statement("makeRaythru", vars=[b, a]),
        Statement("makeRaythru", vars=[b, c])
        ]
    if angle_val == "90":
        s.append(Statement("rightAngle", vars=[a, b, c]))
        return s
    s.append(Statement(angle_name,
                        vars=[
                                a, b, c, deg_to_rad(angle_val)
                            ]))
    return s
    
def angle(a, b, c, angle_val):
    return _angle_helper("angle", a,  b, c, angle_val)
    
def angleCcw(a, b, c, angle_val):
    return _angle_helper("angleCcw", a,  b, c, angle_val)
        
def angleCw(a, b, c, angle_val):
    return _angle_helper("angleCw", a,  b, c, angle_val)
        
def dist(p1, p2, dist_p1_p2):
    return Statement("dist", vars=[p1, p2, dist_p1_p2])

# Notice this is a patch - because in cant be a name for a function
def in_func(a, domain):
    return Statement("in", vars=[a, domain])

# TODO: Perhaps add the option  for known without a value (and value will be generated)
def known(var, val):
    return Statement("known",  vars=[var, eval(val)])

def not_in(a, domain):
    return Statement("not_in", vars=[a, domain])

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
    res = re.compile("(\w+)\(.*\)").findall(exp_lhs)
    if len(res) == 0:
        return
    predicate = res[0]
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

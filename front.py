import re
from sympy import Point, pi

SAMPLES = {
    "triangle": ["dist(X,Y)=136",
                "X!=Y",
                "X=Point(0,0)",
                "dist(Z,Y)=136",
                "X!=Z",
                "Z=Point(136,0)",
                "136=136",
                        "?(Y)"],
    "pentagon": ["dist(A,B)=d",
                "dist(B,C)=d",
                "dist(C,D)=d",
                "dist(D,E)=d",
                "dist(E,A)=d",
                "angleCcw(A,B,C)=a",
                "angleCcw(B,C,D)=a",
                "angleCcw(C,D,E)=a",
                "angleCcw(D,E,A)=a",
                "angleCcw(E,A,B)=a",
                # TODO: Implement intersect2segmentsQ, realnot
                #"intersect2segmentsQ(A,B,C,D,q)",
                #"realnot(q)",
                "D!=A",
                "A!=C",
                "A=Point(0, 0)",
                "C=Point(1,0)",
                "a=deg_to_rad(120)",
                "d=1",
                "?(B)",
                "?(D)",
                "?(E)"]
            }

def deg_to_rad(deg):
    return (2*pi)*(float(deg)/360)

def is_number(string):
    for i in string:
        if not i.isdigit():
            return False
    return True

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
    
POSSIBLE_PREDICATES = ["dist", "angleCcw", "angleCw", "angle", "segment", "makeLine"] # Also possible: !=, =, ?

def parse_line(line):
    line = line.strip("\r")
    if line.startswith("?"):
        # Each output var should be  in a seperated  line as well
        output_var = re.compile("\?\((\w+)\)").findall(line)[0]
        return ["output", (output_var)]
    if "!=" in line:
        vars = line.split("!=")
        return ["neq", tuple(vars)]
    if "=" in line:
        left, right = line.split("=")
        res = re.compile("(\w+)\(.*\)").findall(left)
        if len(res) > 0:
            predicate = res[0]
        else:
            predicate = None
        if predicate and (predicate in POSSIBLE_PREDICATES):
            vars = re.compile("\w+\((.*)\)").findall(left)[0].split(",")
            vars.append(right)
            return [predicate, vars]
        if not predicate:
            # In this case we have: X=something
            # TODO: Maybe use the eval in the numeric part instead
            return ["known", (left, eval(right))]
            
    raise NotImplementedError("statements: {} isn't implemented".format(line))
    
def parse_free_text(lines):
    # Get input after it was split into lines, in a format similar to the spec in the appendix.
    # Assumes no unnessacary spaces, tabs or whatever
    # with each new line contains one statement
    # TODO: replace numbers  with constants, replace 90 degrees angle with rightAngle
    # TODO: There is still some work here (handle spaces, indicutive errors, etc)
    statements = [] # a list of lists, each one has predicate  and tuple of variables
    for line in lines:
        try:
            statements.append(parse_line(line))
        except Exception as e:
            print("Failed parsing in line: " + line)
            raise e
    return statements
    
def build_statements(input_list):
    # Get a list  of statements with format: [predicate, vars]
    # Turn into a list of statement objects
    statements = []
    for predicate, vars in input_list:
        statements.append(Statement(predicate=predicate, vars=vars))
    return statements
    

def main(exercise_name=None):
    # If exercise_name is None - get input from user
    # Otherwise - use a builtin sample
    if exercise_name:
        lines = SAMPLES[exercise_name]
    else:
        lines = input("Enter input: ").split("\n")
    print("In front - about to create statements")
    statements = build_statements(parse_free_text(lines))
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

import re

# This class is the way to pass the input to the synthesis part
class Statement:
    def __init__(self, predicate, vars):
        self.predicate = predicate
        self.vars = vars


def parse_input(input_file):
    # Parse input (right now in the form of dl file)
    f = open(input_file, "r")
    input_lines = f.read().split("\n")
    f.close()
    statements = []
    for s in input_lines[1:]: # the first line is the include
        if s == "":
            continue
        tmp = re.compile("(\w+)").findall(s)
        predicate = tmp[0]
        vars = []
        for i in tmp[1:]:
            vars.append(i)
        statements.append(Statement(predicate, vars))
    return statements
    
def main():
    exercise_name = "triangle"
    souffle_main_dir = "souffleFiles"
    souffle_in_dir = os.path.join(souffle_main_dir, exercise_name)
    return parse_input(os.path.join(souffle_in_dir,exercise_name + ".dl"))
        
if __name__ == "__main__":
    main()

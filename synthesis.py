#TODO:
# Handle asserts
# Define an api for the synthesis module
# - Take care of "error loading file" errors in souffle (for example create empty files)
# - Take care of input - from spec to dl file/ facts files
# - Handle exception in case souffle has error (catch it somehow and return niec output)
# Handle the fact that its running slowly

import os
import shutil
import re
import csv
from sympy import Point, pi
from utils import deg_to_rad, is_number
# Notice: should download sympy
#from sympy.geometry import Point, Circle, Line, intersection

class Exercise:
    def __init__(self, name):
        # Note: symbols should come from the front
        self.name = name
        self.dl_file = None
        self.output_vars = []
        self.known_symbols = {}
        self.other_vars = [] # Here are the rest of the vars (that arent known or required as output)

    def build_exercise_from_statements(self, statements):
        self._write_dl(statements)
        # Add variables to known and output vars
        for s in statements:
            if s.predicate == "known":
                var_name = s.vars[0]
                var_val = s.vars[1]
                # Variable shouldnt be in known  twice
                assert(var_name not in self.known_symbols)
                assert(var_name not in self.output_vars)
                self.known_symbols[var_name] = var_val
                if var_name in self.other_vars:
                    self.other_vars.remove(var_name)
            elif s.predicate == "output":
                assert(len(s.vars) == 1)
                var = s.vars[0]
                assert(var not in self.known_symbols)
                self.output_vars.append(var)
                if var in self.other_vars:
                    self.other_vars.remove(var)
            else:
                for var in s.vars:
                    if var not in self.known_symbols and var not in self.output_vars and var not in self.other_vars and (not is_number(var)):
                        self.other_vars.append(var)

    def _write_dl(self, statements):
        # Create dl file inside souffle_in_dir folder
        # Create relevant variables from statements
        # Assumes statements is after the replacement of numbers with known symbols
        self.dl_file = os.path.join(souffle_in_dir, self.name + ".dl")
        f = open(self.dl_file, "w")
        f.write("#include <GeometryRules.dl>\n")
        for s in statements:
            # Notice if there is a predicate that has only 1 var - it should be handled seperatly
            predicate = s.predicate[0].upper() + s.predicate[1:]
            if s.predicate == "known":
                f.write(predicate + "(\"" + s.vars[0] + "\").\n")
            elif s.predicate == "rightAngle":
                f.write("Angle(\"{}\", \"{}\", \"{}\", \"90\").\n".format(s.vars[0], s.vars[1], s.vars[2]))
            elif (s.predicate == "notIn") or (s.predicate == "neq") or (s.predicate == "output"):
                # neq shouldnt be in dl file (only as assert)
                pass
            else:
                line_to_write = predicate + str(s.vars) + ".\n"
                f.write(line_to_write.replace("'", "\""))
        f.close()
        
    def build_exercise_from_dl(self, dl_file, output_vars, known_symbols):
        # Assume dl file is already written
        self.dl_file = dl_file
        self.output_vars = output_vars
        self.known_symbols = known_symbols


# name: [output_vars, known_symbols]
SAMPLES = {"triangle": [["Y"], {"X": Point(0, 0), "Z":Point(1, 0), "d": 1}],
        "myTriangle": [["W", "Y"], {"X": Point(0, 0), "Z":Point(1, 0), "Dist": 1}],
        "square": [["C", "D"], {"A":Point(0,0), "B":Point(1, 0)}],
        "square2": [["C"], {"A":Point(0,0), "B":Point(1, 0), "d": 1}],
        "pentagon": [["B", "D", "E"], {"A":Point(0, 0),  "C": Point(1, 0)}],
        "pentagon2": [["B", "D", "E"], {"A":Point(0, 0),  "C": Point(1, 0), "a":deg_to_rad(120),  "d": 1}],
        "9gon": [["C", "D", "E", "F", "G", "H", "I"], {"A":Point(0, 0),  "B": Point(1, 0)}]
        }


MIN_APPLY = 1
MAX_APPLY = 3

class Relation:
    def __init__(self, name, is_make_relation=False, should_delete_symmetry=False):
        self.name = name
        self.facts = []
        self.is_make_relation = is_make_relation
        if is_make_relation:
            self.make_name = "Make" + name
        # should_delete_symmetry can refer only to relations with exactly 2 parameters
        self.should_delete_symmetry = should_delete_symmetry
        
    def _find_new_facts(self):
        is_new_object = False

        # Read output file of the make relation
        r_out_path = os.path.join(souffle_out_dir, self.make_name + ".csv")
        lines = []
        if (not os.path.isfile(r_out_path)):
            return is_new_object
        
        # Look for new facts and add them to the relation
        f = open(r_out_path, "r")
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            # Create new fact
            new_fact = Fact(self, row)
            # Check if we have already seen this object
            #TODO: Maybe there is a better way (like comparing the id)
            if new_fact in self.facts:
                continue
            if self.should_delete_symmetry:
                # Don't add this fact if the symmetric fact has already been added
                a, b = row
                symmetric_fact = Fact(self, [b, a])
                if symmetric_fact in self.facts:
                    continue
            is_new_object = True
            self.facts.append(new_fact)
        
        f.close()
        return is_new_object

    def _write_facts_helper(self, out_rel_name, generate_row_to_write, should_mark_is_new=True):
        in_file = open(os.path.join(souffle_in_dir, out_rel_name + ".facts"), "a")
        csv_writer = csv.writer(in_file, delimiter="\t")
        for fact in self.facts:
            if fact.is_new:
                if should_mark_is_new:
                    fact.is_new = False
                csv_writer.writerow(generate_row_to_write(fact))
        in_file.close()
    
    # This function adds the new facts to the relation input file
    def _write_new_facts(self):
        if self.name == "Line":
            self._write_facts_helper(out_rel_name="TypeOf",
                                generate_row_to_write=lambda fact:["line", fact.id],
                                should_mark_is_new=False)
            self._write_facts_helper(out_rel_name="In",
                                generate_row_to_write=lambda fact:[fact.params[0], fact.id],
                                should_mark_is_new=False)
            self._write_facts_helper(out_rel_name="In",
                                generate_row_to_write=lambda fact:[fact.params[1], fact.id])
        elif self.name.startswith("Apply") or (self.name == "Known"):
            # For apply and known relations - dont use id
            self._write_facts_helper(out_rel_name=self.name,
                                generate_row_to_write=lambda fact:fact.params)
        else:
            self._write_facts_helper(out_rel_name=self.name,
                                generate_row_to_write=lambda fact:fact.params + [fact.id])
    
    def make(self):
        # Write new facts to relevant input files for deduction
        # The function read outpus of last souffle run, look for new facts from 'make' relations, and create appropriate facts. Return True if a new fact was added
        if not self.is_make_relation:
            return
        is_new_object = self._find_new_facts()
        self._write_new_facts()
        return is_new_object


class Fact:
    def __init__(self, relation, params, is_new=True):
        self.relation = relation
        self.params = params
        self.is_new = is_new
        self.id = self.relation.name.lower() + str(len(self.relation.facts) + 1)
        
    def  __str__(self):
        tmp =  self.relation.name +  "("
        for p in self.params:
            tmp += p + ", "
        return  tmp + ")"
    
    def __eq__(self, other):
        return (self.params == other.params) and (self.relation.name == self.relation.name)

relations = {
        "Circle": Relation("Circle", is_make_relation=True),
        "PerpBisect":Relation("PerpBisect", is_make_relation=True, should_delete_symmetry=True),
        "Intersection": Relation("Intersection", is_make_relation=True, should_delete_symmetry=True),
        "Line": Relation("Line", is_make_relation=True),
        "Raythru": Relation("Raythru", is_make_relation=True),
        "ExtendRay": Relation("ExtendRay", is_make_relation=True),
        "Linethru": Relation("Linethru", is_make_relation=True),
        "Minus": Relation("Minus", is_make_relation=True),
        "Known": Relation("Known", is_make_relation=True),
        # Apply relations are here to prevent from  applying rules that are already known
        "Apply1": Relation("Apply1", is_make_relation=True),
        "Apply2": Relation("Apply2", is_make_relation=True),
        "Apply3": Relation("Apply3", is_make_relation=True)                
            }
# These are relations that has "make" relations (to help create their data)
make_relations = [rel for rel in relations.values() if rel.is_make_relation]

def run_souffle(souffle_script):
    os.system("souffle -F {souffle_in_dir} {script} -D {souffle_out_dir} -I {include_dir}".format(
    souffle_in_dir=souffle_in_dir, script=souffle_script, souffle_out_dir=souffle_out_dir, include_dir="."))

# Functions to parse the results of the deduction
def find_all_locations(obj_id):
    # Get an object id, parse datalog output and return list of locations it's in
    loci = []
    try:
        f = open(os.path.join(souffle_out_dir, "In.csv"), "r")
    except FileNotFoundError as e:
        print("ERROR: file wasn't found, probably a mistake in the dl file")
        print()
        raise e
    csv_reader = csv.reader(f, delimiter="\t")
    for row in csv_reader:
        obj, locus_id = row
        if obj == obj_id:
            loci.append(locus_id)
    f.close()
    return loci

def get_best_known_locus(loci):
    # Get list of possible locations, return  a known one with minimal dimension
    # If the object isn't in any known locus - return  None

    f = open(os.path.join(souffle_out_dir, "KnownDimension" + ".csv"), "r")
    csv_reader = csv.reader(f, delimiter="\t")
    
    # TODO: Improve this code (finding lowest dimension)
    locus_from_dim0 = None
    locus_from_dim1 = None
    
    for row in csv_reader:
        locus = row[0]
        dim = int(row[1])
        if locus in loci:
            if dim == 0:
                locus_from_dim0 = locus
                best_dim = 0
            if dim == 1:
                locus_from_dim1 = locus
                best_dim = 1
    f.close()
    
    if locus_from_dim0:
        return locus_from_dim0, best_dim
    if locus_from_dim1:
        return locus_from_dim1, best_dim

# The function gets all unknown vars, finds best locus for each one and return a dict that saves it
# Dict structure: locus_per_var = {var:(best_locus, best_dim)}
def best_known_locus_for_each_var(vars):
    locus_per_var = {}
    for var in vars:
        loci = find_all_locations(var)
        res = get_best_known_locus(loci)
        if res:
            best_locus, best_dim = res
            print(var + " is inside this locus: " + best_locus + ", from dim: " + str(best_dim))
            locus_per_var[var] = (best_locus, best_dim)
        else:
            print("Couldn't find a locus for " + var)
    return locus_per_var

def get_best_output_var(locus_per_var):
    # Get a dict with the best location for each unknown var. return  the locus of the best one (lowest dimension locus)
    overall_best_dim = None
    overall_best_var = None
    overall_best_locus = None
    for var in locus_per_var.keys():
        cur_locus, cur_dim = locus_per_var[var]
        if (overall_best_dim == None) or (cur_dim < overall_best_dim):
            overall_best_dim = cur_dim
            overall_best_var = var
            overall_best_locus = cur_locus
    return overall_best_var, overall_best_locus, overall_best_dim
    
def is_search_completed(output_vars, locus_per_var):
    # Get output vars and a dict with their best locations.
    # If all vars have locus from 0 dimension then return True
    for var in output_vars:
        if var not in locus_per_var:
            return False
        # This is the locus dimension
        if locus_per_var[var][1] != 0:
            return False
    return True

def get_locus_type_from_name(locus_name):
    locus_type = re.compile("(\D+)\d+").findall(locus_name)[0]
    # Make the first letter capital
    locus_type = locus_type[0].upper() + locus_type[1:]
    return locations[locus_type]
    return locus_type

# The function gets a known locus name, and find the reason it is known (using the apply relation).
# The function returns the reason title and its params
def get_reason(symbol_name):
    # TODO: Save this for each iteration instead of calculating  from scratch
    # Find locus name inside the apply relation files, and return the relevant predicate
    for i in range(MIN_APPLY, MAX_APPLY + 1):
        #f = open(os.path.join(souffle_out_dir, "Apply" + str(i) + ".csv"), "r")
        f = open(os.path.join(souffle_out_dir, "Apply" + str(i) + ".facts"), "r")
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            if (row[0] == symbol_name):
                f.close()
                return row[1], row[2:]
                
        f.close()
    # If couldn't find a predicate - than this is a leaves
    raise AssertionError("Couldnt find apply rule for: " + str(locus_name))
    

def is_leave(term):
    # TODO: Dont calculate this twice
    for i in range(MIN_APPLY, MAX_APPLY + 1):
        #f = open(os.path.join(souffle_out_dir, "Apply" + str(i) + ".csv"), "r")
        f = open(os.path.join(souffle_out_dir, "Apply" + str(i) + ".facts"), "r")
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            if (row[0] == term):
                f.close()
                return False
                
        f.close()
    return True

def produce_assert_helper(statement, known_symbols):
    # Gets a statement in the format the front sent to synthesis module. Returns an assert rule according to the numeric module api
    # Notice this function can return None for certain predicates
    predicate = statement.predicate.lower()
    if predicate == "segment":
        return
    elif predicate == "rightangle":
        return ("angleCcw({}, {}, {}) - {}".format(*statement.vars, deg_to_rad("90")))
    elif (predicate == "angle") or (predicate == "angleccw"):
        # angle means we dont care of its ccw or cw 
        # Notice there shouldnt be an angle in degrees here
        angle = statement.vars[3]
        if (is_number(angle)):
            angle = deg_to_rad(angle)
        return "angleCcw({}, {}, {}) - {}".format(*statement.vars[:-1], angle)
    elif predicate == "notcolinear":
        # TODO: implement (not as an assertion rule)
        return  
    elif predicate == "dist":
        return ("dist({}, {}) - {}".format(*statement.vars))
    elif predicate == "known":
        for var in statement.vars:
            assert(var in known_symbols)
        # In this case there isn't an assertion error
        return
    elif predicate == "in":
        # TODO: Should I do something here?
        return
    elif predicate == "notin":
        # TODO: Implement (not as an assertion rule but a notIn rule)
        return
    elif predicate == "neq":
        # TODO: Implement this (not as an assertion rule)
        return
    elif predicate == "output":
        return
    elif predicate.startswith("make"):
        return
    else:
        raise NotImplementedError("predicate {} isn't implemented".format(predicate))

class PartialProg:
    """
    Holds the output from the deduction procedure.
    """
    def __init__(self):
        self.known = {}
        self.rules = []

    def _help_produce_rule(self, locus_name):
        # TODO: this shouldnt be a part of the partialProgram object
        reason_title, params = get_reason(locus_name)
        param_strings = []
        for param in params:
            if not is_leave(param):
                param_strings.append(self._help_produce_rule(param))
            else:
                param_strings.append(param)
        if reason_title == "intersection":
            return param_strings
        #if reason_title in ["id", "circle-center", "circle-from-diameter"]:
            #raise NotImplementedError("reason title {} wasnt implemented yet".format(reason_title))
        if reason_title == "orth":
            return "rotateCcw({}, pi/2)".format(param_strings[0])
        if reason_title == "perp_bisect-0":
            # This hack will work,  but it doesnt actually create a tree
            middle_point = "({} + {}) / 2".format(param_strings[0], param_strings[1])
            #vec = "orth(vecFrom2Points({}, {}))".format(param_strings[0], param_strings[1])
            vec = "rotateCcw(vecFrom2Points({}, {}), pi/2)".format(param_strings[0], param_strings[1]) #TODO:  use orth here
            return 'linevec(({}), ({}))'.format(middle_point, vec)
        if len(param_strings) == 1:
            return '{}({})'.format(reason_title, *param_strings)
        if len(param_strings) == 2:
            return '{}({}, {})'.format(reason_title, *param_strings)
        if len(param_strings) == 3:
            return '{}({}, {}, {})'.format(reason_title, *param_strings)
        raise NotImplementedError("param strings len is: " + str(len(param_strings)))
        
    def produce_equal_rule(self, var_name):
        # TODO: After handling numbers in front - remove is_number checkings from here
        # Notice this is only true since we check is_number when deciding a statement is ready
        if (is_number(var_name)):
            return
        val = self._help_produce_rule(var_name)
        self.rules.append([":=", var_name, val])
        
    def produce_in_rule(self, var, locus_name, dim):
        # This function  adds an in rule. It creates it as a tree of predicates
        locus_list = self._help_produce_rule(locus_name)
        if type(locus_list) != list:
            locus_list = [locus_list]
        self.rules.append([":in", var, locus_list])
        
    def produce_known(self, symbols):
        self.known = symbols
        
    def produce_assert(self, statements, *args, **kwargs):
        # This function decides the format of the assertion rule
        # The helper function calculates the expression to evaluate
        # statements: list of ready statements
        assert_rules = ""
        for s in statements:
            res = produce_assert_helper(s, *args, **kwargs)
            # Notice res might be none (which means we dont need an assertion rule for that statement)
            if res:
                res = "abs({})".format(res)
                if assert_rules != "":
                    # This  isn't the first assert
                    assert_rules += " + " + res
                else:
                    assert_rules = res
        if assert_rules == "":
            return
        self.rules.append(["assert", assert_rules])


    def __str__(self):
        #return "known = {}\nrules = {}".format(str(self.known), str(self.rules))
        out_str = "known = {}\n".format(str(self.known))
        out_str += "[\n"
        for rule in  self.rules:
            out_str += "\t{}\n".format(rule)
        out_str += "]"
        return out_str
    
# The function  emits a known fact for the best var possible, in order to run the deductive part again
def emit_known_fact(var):
    print("Emit: {} to known  facts".format(var))
    f = open(os.path.join(souffle_in_dir, "Known.facts"), "a")
    csv_writer = csv.writer(f, delimiter="\t")
    csv_writer.writerow([var])
    f.close()
    
# This function is called after making a var known. It removes it from the relevant list and appends to the known_symbols list
def update_vars_state(output_vars, other_vars, known_symbols, var):
    # TODO: Notice remove is slow in python (perhaps there is an alternative)
    if var in output_vars:
        output_vars.remove(var)
    elif var in other_vars:
        other_vars.remove(var)
    else:
        raise AssertionError("This shouldnt happen")
    known_symbols.append(var)

def deductive_synthesis_iteration(souffle_script):
    # Run souffle iteratively, until there aren't new facts in the make relations
    is_new_object = True
    while is_new_object:
        is_new_object = False
        print("Running souffle...")
        run_souffle(souffle_script)
        for rel in make_relations:
            if rel.make():
                is_new_object = True

# The function returns all the symbols in Known relation in the datalog but the output vars
# Notice this doesnt return symbols that were known by input
def get_known_symbols():
    known = []
    for fact in relations["Known"].facts:
        assert(len(fact.params) == 1)
        known.append(fact.params[0])
    return known

# The function gets all vars that are yet unknown, checks which one has become known  in  the last iteration, and returns a list of the new known vars
def find_new_known_vars(vars):
    new_known = []
    known_symbols = get_known_symbols()
    for var in vars:
        if var in known_symbols:
            new_known.append(var)
    return new_known

# The function create the partial program for the numeric search algorithm
# TODO: improve assertion rules - seperate them for each var and make sure we add them in the right time
def deductive_synthesis(exercise, partial_prog, statements):
    output_vars = exercise.output_vars.copy()
    # Distinguish between required out to others (Other vars may appear in the partial prog output, but they dont have to)
    other_vars = exercise.other_vars.copy()
    # Create a copy of all known symbols names
    known_symbols = list(exercise.known_symbols.keys())
    is_done = False
    # Remove assertions on already known  symbols
    statements = [s for s in statements if ((s.predicate != "known") and (not s.is_ready(known_symbols)))]

    while not is_done:
        new_known_vars = False
        deductive_synthesis_iteration(souffle_script=exercise.dl_file)
        vars = find_new_known_vars(output_vars + other_vars)
        for var in vars:
            partial_prog.produce_equal_rule(var)
            update_vars_state(output_vars=output_vars,
                    other_vars=other_vars,
                    known_symbols=known_symbols,
                    var=var)
        if len(vars) > 0:
            new_known_vars = True
        locus_per_var = best_known_locus_for_each_var(output_vars + other_vars)
        var, locus, dim = get_best_output_var(locus_per_var)
        if var:
            new_known_vars = True
            partial_prog.produce_in_rule(var, locus, dim)
            emit_known_fact(var=var)
            update_vars_state(output_vars=output_vars,
                            other_vars=other_vars,
                            known_symbols=known_symbols,
                            var=var)
        if not new_known_vars:
            print("remaining output vars are: ")
            for var in output_vars:
                print(var)
            # In this case there is no way to progress
            raise AssertionError("Not found output var with known location")

        if is_search_completed(output_vars, locus_per_var):
            # Question: Should I always emit known facts for all vars with dimension 0?
            # In this case all output vars has 0 dimension
            for var in output_vars:
                locus, dim = locus_per_var[var]
                partial_prog.produce_in_rule(var, locus, dim)
                update_vars_state(output_vars=output_vars,
                            other_vars=other_vars,
                            known_symbols=known_symbols,
                            var=var)
            print("Search completed")
            is_done = True
        
        # A new var is known - add relevant assertion rules
        cur_statements = []
        for s in statements:
            if s.is_ready(known_symbols):
                cur_statements.append(s)
        
        partial_prog.produce_assert(
                    statements=cur_statements,
                    known_symbols=exercise.known_symbols)
        statements = [s for s in statements if not s.is_ready(known_symbols)]

    if statements:
        print("Note: the remaining statements")
        for s in statements:
            print(s)
    print()
    

# Functions to prepare for the deduction part

def create_folder():
    #TODO: create empty facts files
    if (not os.path.isdir(souffle_main_dir)):
        os.mkdir(souffle_main_dir)
    if (os.path.isdir(souffle_out_dir)):
        shutil.rmtree(souffle_out_dir)
    os.mkdir(souffle_out_dir)

def move_input_to_folder():
    # deprecated
    # This function copies the files in the input dir, to the dir which souffle reads from
    # Later we will get the input from spec and won't need this
    in_dir = os.path.join("tmpInput", EXERCISE_NAME)
    for file_name in os.listdir(in_dir):
        if file_name.endswith(".facts"):
            shutil.copyfile(os.path.join(in_dir, file_name), os.path.join(souffle_in_dir, file_name))

def define_souffle_vars(exercise_name):
    global souffle_main_dir
    souffle_main_dir = "souffleFiles"
    global souffle_in_dir
    souffle_in_dir = os.path.join(souffle_main_dir, exercise_name)
    global souffle_out_dir
    souffle_out_dir = os.path.join(souffle_main_dir, exercise_name)


def main(exercise_name=None, exercise=None, statements=[], write_output_to_file=True):
    # Must get either exercise or statements (or both if they match).
    # exercise_name is optional
    if exercise and exercise_name:
        assert(exercise.name == exercise_name)
    if not exercise_name:
        if exercise:
            exercise_name = exercise.name
        else:
            exercise_name = "tmp"
    
    define_souffle_vars(exercise_name)
    create_folder()
    
    partial_prog = PartialProg()
    if not exercise:
        exercise = Exercise(exercise_name)
        assert(len(statements) > 0)
        exercise.build_exercise_from_statements(statements)
        
    # Note: symbols is a dict we should get from the front
    partial_prog.produce_known(exercise.known_symbols)
    deductive_synthesis(exercise, partial_prog, statements)
    
    if write_output_to_file:
        f = open(os.path.join(souffle_out_dir, exercise_name + ".out.txt"), "w")
        f.write(str(partial_prog))
        f.close()        
    return partial_prog
    
      
if __name__ == "__main__":
    # Basiccaly everything here shouldn't happen when running the whole program (the input should come from the front and the output should go to the numeric search

    # This is an example of useing synthesis straight from dl file
    exercise_name = "pentagon"
    souffle_script = os.path.join("tmpInput", exercise_name + ".dl")
    exercise = Exercise(exercise_name)
    exercise.build_exercise_from_dl(
                    dl_file=souffle_script,
                    output_vars=SAMPLES[exercise_name][0],
                    known_symbols=SAMPLES[exercise_name][1]
                    )
    #output_vars = parse_spec() # Currentlhy parse spec only gives the output variables
    print("Partial program is: ")
    partial_prog = main(exercise=exercise, write_output_to_file=True) # Note this will produce no assertion rules
    print(partial_prog)

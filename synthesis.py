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
# Notice: should download sympy
#from sympy.geometry import Point, Circle, Line, intersection

def deg_to_rad(deg):
    return (2*pi)*(float(deg)/360)

class Exercise:
    def __init__(self, name):
        # Note: symbols should come from the front
        self.name = name
        self.dl_file = None
        self.output_vars = []
        self.known_symbols = {}

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
            elif s.predicate == "output":
                assert(len(s.vars) == 1)
                assert(s.vars[0] not in self.known_symbols)
                self.output_vars.append(s.vars[0])

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
            elif (s.predicate == "neq") or (s.predicate == "output"):
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
        "pentagon": [["B", "D", "E"], {"A":Point(0, 0),  "C": Point(1, 0), "a":deg_to_rad(120),  "d": 1}],
        "9gon": [["C", "D", "E", "F", "G", "H", "I"], {"A":Point(0, 0),  "B": Point(1, 0), "d": 1}]
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
        if self.name.startswith("Apply"):
            # For apply relation - dont use id
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
        
    def __eq__(self, other):
        return (self.params == other.params) and (self.relation.name == self.relation.name)

relations = {
                "Circle": Relation("Circle", is_make_relation=True),
                "Intersection": Relation("Intersection", is_make_relation=True, should_delete_symmetry=True),
                "Line": Relation("Line", is_make_relation=True),
                "Raythru": Relation("Raythru", is_make_relation=True),
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
    os.system("souffle -F {souffle_in_dir} {script} -D {souffle_out_dir} -I {include_dir}".format(souffle_in_dir=souffle_in_dir, script=souffle_script, souffle_out_dir=souffle_out_dir, include_dir="."))

# Functions to parse the results of the deduction
def find_all_locations(obj_id):
    # Get an object id, parse datalog output and return list of locations it's in
    loci = []
    f = open(os.path.join(souffle_out_dir, "In.csv"), "r")
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

# The function gets all output vars, finds best locus for each one and return a dict that saves it
# Dict structure: locus_per_var = {var:(best_locus, best_dim)}
def best_known_locus_for_each_var(output_vars):
    locus_per_var = {}
    for var in output_vars:
        loci = find_all_locations(var)
        res = get_best_known_locus(loci)
        if res:
            best_locus, best_dim = res
            print(var + " is inside this locus: " + best_locus + ", from dim: " + str(best_dim))
            locus_per_var[var] = (best_locus, best_dim)
        else:
            print("Couldn't find a locus for " + var)
    return locus_per_var

def get_best_output_var(output_vars, locus_per_var):
    # Get output vars and a dict with their best locations. return  the locus of the best one (lowest dimension locus)
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
   
"""    
def find_fact_for_locus(locus_id, relation_name):
    # Read from souffle.
    # Question: is it enough to take rel.facts?
    f = open(os.path.join(souffle_in_dir, relation_name + ".csv"), "r")
    csv_reader = csv.reader(f, delimiter="\t")
    for row in csv_reader:
        # The locus id is always the last word in the row
        if row[-1] == locus_id:
            return  row
""" 

def get_locus_type_from_name(locus_name):
    locus_type = re.compile("(\D+)\d+").findall(locus_name)[0]
    # Make the first letter capital
    locus_type = locus_type[0].upper() + locus_type[1:]
    return locations[locus_type]
    return locus_type

# The function gets a locus name, and find the predicate that made the locus known (usiing the apply relation).
# The function returns the predicate and its params
def get_predicate(locus_name):
    # TODO: Save this for each iteration instead of calculating  from scratch
    # Find locus name inside the apply relation files, and return the relevant predicate
    for i in range(MIN_APPLY, MAX_APPLY + 1):
        #f = open(os.path.join(souffle_out_dir, "Apply" + str(i) + ".csv"), "r")
        f = open(os.path.join(souffle_out_dir, "Apply" + str(i) + ".facts"), "r")
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            if (row[0] == locus_name):
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

def produce_assert_helper(statement, known_symbols, output_vars):
    # Gets a statement in the format the front sent to synthesis module. Returns an assert rule according to the numeric module api
    # Notice this function can return None for certain predicates
    # TODO: Define an api for the synthesis module
    predicate = statement.predicate.lower()
    if predicate == "dist":
        return ("dist({}, {}) - {}".format(*statement.vars))
    elif predicate == "known":
        for var in statement.vars:
            assert(var in known_symbols)
        # In this case there isn't an assertion error
        return
    elif predicate == "makeline":
        return
    elif predicate == "rightangle":
        return ("angleCcw({}, {}, {}) - {}".format(*statement.vars, deg_to_rad("90")))
    elif (predicate == "angle") or (predicate == "angleccw"):
        # angle means we dont care of its ccw or cw 
        # TODO: Make sure!!!
        a = statement.vars[0]
        b = statement.vars[1]
        c = statement.vars[2]
        res = statement.vars[3]
        return ("angleCcw({}, {}, {}) - {}".format(a, b, c, deg_to_rad(res)))
    else:
        raise NotImplementedError


class PartialProg:
    def __init__(self):
        self.known = {}
        self.rules = []

    def _help_produce_rule(self, locus_name):
        # Problem: Apply for already known facts
        predicate_name, params = get_predicate(locus_name)
        param_strings = []
        for param in params:
            if not is_leave(param):
                param_strings.append(self._help_produce_rule(param))
            else:
                param_strings.append(param)
        if predicate_name == "intersection":
            return [self._help_produce_rule(params[0]), self._help_produce_rule(params[1])]
        if predicate_name == "orth":
            return "rotateCcw({}, pi)".format(param_strings[0])
        if len(param_strings) == 1:
            return '{}({})'.format(predicate_name, *param_strings)
        if len(param_strings) == 2:
            return '{}({}, {})'.format(predicate_name, *param_strings)
        if len(param_strings) == 3:
            return '{}({}, {}, {})'.format(predicate_name, *param_strings)
        raise NotImplementedError("param strings len is: " + str(len(param_strings)))
        
    def produce_in_rule(self, var, locus_name, dim):
        locus_list = self._help_produce_rule(locus_name)
        if type(locus_list) != list:
            locus_list = [locus_list]
        self.rules.append([":in", var, locus_list])
    def produce_known(self, symbols):
        self.known = symbols
        
    def produce_assert(self, var, statements, *args, **kwargs):
        # This function decides the format of the assertion rule
        # The helper function calculates the expression to evaluate
        # statements: list of ready statements
        # var: name of the var we searched for in this assert
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
        self.rules.append(["assert", var,  assert_rules])


    def __str__(self):
        #return "known = {}\nrules = {}".format(str(self.known), str(self.rules))
        out_str = "known = {}\n".format(str(self.known))
        out_str += "[\n"
        for rule in  self.rules:
            out_str += "\t{}\n".format(rule)
        out_str += "]"
        return out_str
        
    
def get_geometric_locus(locus_id, symbols):
    # Get a locus id and dict of symbols with their real values.
    # Return  an object of the geometric location
    locus = get_locus_type_from_name(locus_id)
    locus_type = locus.name
    # All the relavent locations are already in the facts list in memory
    for fact in locus.facts:
        if fact.id == locus_id:
            # TODO: Should I check somewhere if the locus is  known?
            if locus_type == "Circle":
                point_name = fact.params[0]
                radius_name = fact.params[1]
                return Circle(Point(*symbols[point_name]), symbols[radius_name])
                # Should somehow get real coordinates and distance
                # Circle(point, radius)
            if locus_type == "intersection":
                locus1_name = fact.params[0]
                locus2_name = fact.params[1]
                return intersection(get_geometric_locus(locus1_name, symbols), get_geometric_locus(locus2_name, symbols))
            if locus_type == "Line":
                point1_name = facts.params[0]
                point2_name = facts.params[1]
                return Line(Point(*symbols[point1_name]), Point(*symbols[point2_name]))
            return
    raise AssertionError
    
# The function  emits a known fact for the best var possible, in order to run the deductive part again
def emit_known_fact(output_vars, known_symbols, var):
    print("Emit: {} to known  facts".format(var))
    f = open(os.path.join(souffle_in_dir, "Known.facts"), "a")
    csv_writer = csv.writer(f, delimiter="\t")
    csv_writer.writerow([var])
    f.close()
    # TODO: Notice remove is slow in python (perhaps there is an alternative)
    output_vars.remove(var)
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

# The function create the partial program for the numeric search algorithm
# TODO: improve assertion rules - seperate them for each var and make sure we add them in the right time
def deductive_synthesis(exercise, partial_prog, statements):
    output_vars = exercise.output_vars.copy()
    # Create a copy of all known symbols names
    known_symbols = list(exercise.known_symbols.keys())
    is_done = False
    # Remove assertions on already known  symbols
    statements = [s for s in statements if ((s.predicate == "known") and (not s.is_ready(known_symbols)))]
    
    while not is_done:
        deductive_synthesis_iteration(souffle_script=exercise.dl_file)
        locus_per_var = best_known_locus_for_each_var(output_vars)
        var, locus, dim = get_best_output_var(output_vars, locus_per_var)
        if not var:
            # In this case there is no way to progress
            raise AssertionError("Not found output var with known location")
        partial_prog.produce_in_rule(var, locus, dim)
        # Notice this function removes the var from output vars and add it to known symbols
        emit_known_fact(output_vars=output_vars,
                        known_symbols=known_symbols,
                        var=var)
        # A new var is known - add relevant assertion rules
        cur_statements = []
        for s in statements:
            if s.is_ready(known_symbols):
                cur_statements.append(s)
        
        partial_prog.produce_assert(
                    statements=cur_statements,
                    var=var,
                    known_symbols=exercise.known_symbols,
                    output_vars=exercise.output_vars)
        statements = [s for s in statements if not s.is_ready(known_symbols)]

        if is_search_completed(output_vars, locus_per_var):
            # Question: Should I always emit known facts for all vars with dimension 0?
            # In this case all output vars has 0 dimension
            for var in output_vars:
                locus, dim = locus_per_var[var]
                partial_prog.produce_in_rule(var, locus, dim)
            print("Search completed")
            is_done = True

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


def main(exercise_name=None, exercise=None, statements=[], write_output_to_file=False):
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
    exercise_name = "square2"
    souffle_script = os.path.join("tmpInput", exercise_name + ".dl")
    exercise = Exercise(exercise_name)
    exercise.build_exercise_from_dl(
                    dl_file=souffle_script,
                    output_vars=SAMPLES[exercise_name][0],
                    known_symbols=SAMPLES[exercise_name][1]
                    )
    #output_vars = parse_spec() # Currentlhy parse spec only gives the output variables
    print("Partial program is: ")
    partial_prog = main(exercise, write_output_to_file=True) # Note this will produce no assertion rules
    print(partial_prog)

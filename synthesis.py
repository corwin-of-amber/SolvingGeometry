#TODO:
# - Take care of "error loading file" errors in souffle (for example create empty files)
# - Take care of input - from spec to dl file/ facts files
# - Handle exception in case souffle has error (catch it somehow and return niec output)
# Questions:
# Can two relations share the same fact?

import os
import shutil
import re
import csv
# Notice: should download sympy
#from sympy.geometry import Point, Circle, Line, intersection

class Sample:
    def __init__(self, name, output_vars, symbols):
        # Note: symbols should come from the front
        self.name = name
        self.output_vars = output_vars
        self.symbols = symbols

SAMPLES = {"triangle": Sample("triangle", output_vars=["Y"], symbols={"X": (0, 0), "Z":(1, 0), "Dist": 1}),
        "myTriangle": Sample("myTriangle", output_vars=["W", "Y"], symbols={"X": (0, 0), "Z":(1, 0), "Dist": 1}),
        "square": Sample("square", output_vars=["C", "D"], symbols={"A":(0,0), "B":(1, 0)}),
        "pentagon": Sample("pentagon", output_vars=["B", "D", "E"], symbols={"A":(0, 0),  "C": (1, 0), "a":108,  "d": 1})}

EXERCISE_NAME = "pentagon"
souffle_main_dir = "souffleFiles"
souffle_in_dir = os.path.join(souffle_main_dir, EXERCISE_NAME)
script = os.path.join("tmpInput", EXERCISE_NAME + ".dl")
souffle_out_dir = os.path.join(souffle_main_dir, EXERCISE_NAME)


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
                "Minus": Relation("Minus", is_make_relation=True)
            }
# These are relations that has "make" relations (to help create their data)
make_relations = [rel for rel in relations.values() if rel.is_make_relation]

def run_souffle():
    os.system("souffle -F {souffle_in_dir} {script} -D {souffle_out_dir} -I {include_dir}".format(souffle_in_dir=souffle_in_dir, script=script, souffle_out_dir=souffle_out_dir, include_dir="."))

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
    for i in range(2, 4):
        f = open(os.path.join(souffle_out_dir, "Apply" + str(i) + ".csv"), "r")
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            if (row[0] == locus_name):
                f.close()
                return row[1], row[2:]
                
        f.close()
    # If couldn't find a predicate - than this is a leaves
    raise AssertionError("Couldnt find apply rule for: " + str(locus_name))
    

def is_leave(term):
    for i in range(2, 4):
        f = open(os.path.join(souffle_out_dir, "Apply" + str(i) + ".csv"), "r")
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            if (row[0] == term):
                f.close()
                return False
                
        f.close()
    return True

class PartialProg:
    def __init__(self):
        self.known = {}
        self.rules = []
    def _help_produce_rule(self, locus_name):
        # TODO: Handle non-uniform quotation-mark
        # Question: how do I know what the leaves are?
        # Problem: Apply for already known facts
        predicate_name, params = get_predicate(locus_name)
        param_strings = []
        for param in params:
            if not is_leave(param):
                param_strings.append(self._help_produce_rule(param))
            else:
                param_strings.append(param)
        if predicate_name == "Intersection":
            return [self._help_produce_rule(params[0]), self._help_produce_rule(params[1])]
        return '{}{}'.format(predicate_name, tuple(param_strings))
        
    def produce_in_rule(self, var, locus_name, dim):
        locus_list = self._help_produce_rule(locus_name)
        if type(locus_list) != list:
            locus_list = [locus_list]
        self.rules.append([":in", var, locus_list])
    def produce_known(self, symbols):
        self.known = symbols
    def to_str(self):
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
            if locus_type == "Intersection":
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
def emit_known_fact(output_vars, var):
    # geometric_locus = get_geometric_locus(locus, symbols)
    # print("Geometric locus for var {0} is {1}".format(var, geometric_locus))
    print("Emit: {} to known  facts".format(var))
    f = open(os.path.join(souffle_in_dir, "Known.facts"), "a")
    csv_writer = csv.writer(f, delimiter="\t")
    csv_writer.writerow([var])
    f.close()
    output_vars.remove(var)
    #symbols[var] = geometric_locus[0] # This line is  temporary

def deductive_synthesis_iteration():
    # Run souffle iteratively, until there aren't new facts in the make relations
    is_new_object = True
    while is_new_object:
        is_new_object = False
        print("Running souffle...")
        run_souffle()
        for rel in make_relations:
            if rel.make():
                is_new_object = True

# The function create the partial program for the numeric search algorithm
def deductive_synthesis(exercise, partial_prog):
    output_vars = exercise.output_vars.copy()
    is_done = False
    while not is_done:
        deductive_synthesis_iteration()
        locus_per_var = best_known_locus_for_each_var(output_vars)
        var, locus, dim = get_best_output_var(output_vars, locus_per_var)
        if not var:
            # In this case there is no way to progress
            raise AssertionError("Not found output var with known location")
        partial_prog.produce_in_rule(var, locus, dim)
        emit_known_fact(output_vars=output_vars,
                        var=var)
        if is_search_completed(output_vars, locus_per_var):
            # Question: Should I always emit known facts for all vars with dimension 0?
            # In this case all output vars has 0 dimension
            for var in output_vars:
                locus, dim = locus_per_var[var]
                partial_prog.produce_in_rule(var, locus, dim)
            print("Search completed")
            is_done = True

# Functions to prepare for the deduction part

def parse_spec():
    # Open spec file and parse it. Return  output variable if exist
    # TODO: Create appropriate facts file\ dl file from the input
    with open("example.spec", "r") as f:
        for line in f.readlines():
            line = line.strip("\n")
            if line.startswith("dist"):
                x,y,dist = re.compile("dist\((\w+),(\w+)\)=(\d*)").findall(line)[0]
            if line.startswith("known"):
                pass
            if line.startswith("?"):
                # This is output variable
                output_var = re.compile("\?\((\w+)\)").findall(line)
    return output_var

def create_folder():
    #TODO: create empty facts files
    if (not os.path.isdir(souffle_main_dir)):
        os.mkdir(souffle_main_dir)
    if (os.path.isdir(souffle_out_dir)):
        shutil.rmtree(souffle_out_dir)
    os.mkdir(souffle_out_dir)

def move_input_to_folder():
    # This function copies the files in the input dir, to the dir which souffle reads from
    # Later we will get the input from spec and won't need this
    in_dir = os.path.join("tmpInput", EXERCISE_NAME)
    for file_name in os.listdir(in_dir):
        if file_name.endswith(".facts"):
            shutil.copyfile(os.path.join(in_dir, file_name), os.path.join(souffle_in_dir, file_name))


def main():
    create_folder()
    #output_vars = parse_spec() # Currentlhy parse spec only gives the output variables
    exercise = SAMPLES[EXERCISE_NAME]
    #move_input_to_folder()
    partial_prog = PartialProg()
    # Note: symbols is a dict we should get from the front
    partial_prog.produce_known(exercise.symbols)
    deductive_synthesis(exercise, partial_prog)
    print("Partial program is: ")
    print(partial_prog.to_str())
        
main()
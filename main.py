#TODO:
# V use csv module
# V parse files to create facts in memory and only then write to file
# V Go back to triangle example and make it work
# V Make 0-dimension-search work (emit new 'known' fact
# - make square example work
# - Numeric search\ hill climbing
# - Take care of "error loading file" errors in souffle (for example create empty files)
# - listen to recording\ go over my notes
# - Take care of input - from spec to dl file/ facts files
# - Handle exception in case souffle has error (catch it somehow and return niec output)
# Questions:
# Can two relations share the same fact?

import os
import shutil
import re
import csv

SAMLPES = {"triangle": ["Y"], "square": ["C", "D"], "test": ["W", "Y"]}

EXERCISE_NAME = "test"
souffle_main_dir = "souffleFiles"
souffle_in_dir = os.path.join(souffle_main_dir, EXERCISE_NAME)
script = os.path.join("tmpInput", EXERCISE_NAME + ".dl")
souffle_out_dir = os.path.join(souffle_main_dir, EXERCISE_NAME)


class Relation:
    def __init__(self, name, should_delete_symmetry=False):
        self.name = name
        self.facts = []
        self.make_name = "Make" + name
        # should_delete_symmetry can refer only to relations with exactly 2 parameters
        self.should_delete_symmetry = should_delete_symmetry


class Fact:
    def __init__(self, relation, params, is_new=True):
        self.relation = relation
        self.params = params
        self.is_new = is_new
        self.id = self.relation.name.lower() + str(len(self.relation.facts) + 1)
        
    def __eq__(self, other):
        return (self.params == other.params) and (self.relation.name == self.relation.name)

# These are relations that has "make" relations (to help create their data)
make_relations = [Relation("Circle"),
            Relation("Intersection", should_delete_symmetry=True)]

def run_souffle():
    os.system("souffle -F {souffle_in_dir} {script} -D {souffle_out_dir} -I {include_dir}".format(souffle_in_dir=souffle_in_dir, script=script, souffle_out_dir=souffle_out_dir, include_dir="."))

def add_facts_to_relation(rel):
    # The function read outpus of last souffle run, look for new facts from 'make' relations, and create appropriate facts. Return True if a new fact was added
    is_new_object = False

    # Read output file of the make relation
    r_out_path = os.path.join(souffle_out_dir, rel.make_name + ".csv")
    lines = []
    if (not os.path.isfile(r_out_path)):
        return is_new_object
    
    # Look for new facts and add them to the relation
    f = open(r_out_path, "r")
    csv_reader = csv.reader(f, delimiter="\t")
    for row in csv_reader:
        # Create new fact
        new_fact = Fact(rel, row)
        # Check if we have already seen this object
        #TODO: Maybe there is a better way (like comparing the id)
        if new_fact in rel.facts:
            continue
        if rel.should_delete_symmetry:
            # Don't add this fact if the symmetric fact has already been added
            a, b = row
            symmetric_fact = Fact(rel, [b, a])
            if symmetric_fact in rel.facts:
                continue
        is_new_object = True
        rel.facts.append(new_fact)
    
    f.close()
    
    # Add the new facts to the relation input file
    in_file = open(os.path.join(souffle_in_dir, rel.name + ".facts"), "a")
    csv_writer = csv.writer(in_file, delimiter="\t")
    for fact in rel.facts:
        if fact.is_new:
            fact.is_new = False
            csv_writer.writerow(fact.params + [fact.id])
    in_file.close()
    return is_new_object

def find_all_locations(obj_id):
    # Get an object id, return list of locations it's in
    loci = []
    f = open(os.path.join(souffle_out_dir, "In.csv"), "r")
    csv_reader = csv.reader(f, delimiter="\t")
    for row in csv_reader:
        obj, locus_id = row
        if obj == obj_id:
            loci.append(locus_id)
    f.close()
    return loci

def get_best_locus(loci):
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
        return  locus_from_dim1, best_dim


def create_folder():
    #TODO: create empty facts files
    if (not os.path.isdir(souffle_main_dir)):
        os.mkdir(souffle_main_dir)
    if (os.path.isdir(souffle_out_dir)):
        shutil.rmtree(souffle_out_dir)
    os.mkdir(souffle_out_dir)

def deductive_synthesis():
    # Run souffle iteratively, until there aren't new facts in the make relations
    is_new_object = True
    while is_new_object:
        is_new_object = False
        print("Running souffle...")
        run_souffle()
        for rel in make_relations:
            if add_facts_to_relation(rel):
                is_new_object = True

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

def move_input_to_folder():
    # This function copies the files in the input dir, to the dir which souffle reads from
    # Later we will get the input from spec and won't need this
    in_dir = os.path.join("tmpInput", EXERCISE_NAME)
    for file_name in os.listdir(in_dir):
        if file_name.endswith(".facts"):
            shutil.copyfile(os.path.join(in_dir, file_name), os.path.join(souffle_in_dir, file_name))

def best_locus_for_each_var(output_vars):
    # Get all output vars, find best locus for each one and return a dict that saves it
    locus_per_var = {}
    for var in output_vars:
        loci = find_all_locations(var)
        best_locus, best_dim = get_best_locus(loci)
        if best_locus:
            print(var + " is inside this locus: " + best_locus)
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
        if not overall_best_dim or (cur_dim < overall_best_dim):
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
    
def deductive_synthesis_and_numeric_search(output_vars):
    while True:
        deductive_synthesis()
        locus_per_var = best_locus_for_each_var(output_vars)
        if is_search_completed(output_vars, locus_per_var):
            print("Search completed")
            return
        var, locus, dim = get_best_output_var(output_vars, locus_per_var)
        if not var:
            print("Not found output var with known location")
            return
        if dim == 0:
            # Emit a known fact for this var, and run the deductive part again
            f = open(os.path.join(souffle_in_dir, "Known.facts"), "a")
            csv_writer = csv.writer(f, delimiter="\t")
            csv_writer.writerow([var])
            f.close()
            output_vars.remove(var)
        else:
            # TODO: Add  hill-climbing algorithm here
            return

def main():
    create_folder()
    #output_vars = parse_spec() # Currentlhy parse spec only gives the output variables
    output_vars = SAMLPES[EXERCISE_NAME]
    #move_input_to_folder()
    deductive_synthesis_and_numeric_search(output_vars)
        
main()
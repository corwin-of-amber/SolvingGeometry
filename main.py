# Goal: Make the first example work (Isosceles triangle)

import os
import shutil
import re

class Relation:
    def __init__(self, name, should_delete_symmetry=False):
        self.name = name
        self.objects = []
        self.make_name = "Make" + name
        # should_delete_symmetry can refer only to relations with exactly 2 parameters
        self.should_delete_symmetry = should_delete_symmetry


# These are relations that has "make" relations (to help create their data)
make_relations = [Relation("Circle"),
            Relation("Intersection", should_delete_symmetry=True)]

exercise_name = "triangle"
souffle_in_dir = os.path.join("souffleFiles", exercise_name)
script = "triangle.dl"
souffle_out_dir = os.path.join("souffleFiles", exercise_name)

def get_obj_from_line(line):
    return line.strip("\n").split("\t")


def run_souffle():
    os.system("souffle -F {souffle_in_dir} {script} -D {souffle_out_dir}".format(souffle_in_dir=souffle_in_dir, script=script, souffle_out_dir=souffle_out_dir))

def add_facts_to_relation(rel):
    # The function read outpus of last souffle run, look for new objects from 'make' relations, and create appropriate facts. Return True if a new fact was added
    is_new_object = False

    # Read output file of the make relation
    r_out_path = os.path.join(souffle_out_dir, rel.make_name + ".csv")
    lines = []
    if (os.path.isfile(r_out_path)):
        with open(r_out_path, "r") as f:
            lines = f.readlines()
    
    # look for new objects and write them as input for the relation
    in_file = open(os.path.join(souffle_in_dir, rel.name + ".facts"), "a")
    for i, line in enumerate(lines):
        # Check if we have already seen this object
        if line in rel.objects:
            continue
        if rel.should_delete_symmetry:
            a, b = get_obj_from_line(line)
            symmetric_line = "{b}\t{a}\n".format(b=b, a=a)
            if symmetric_line in rel.objects:
                continue
        # Create new object in the facts file
        rel.objects.append(line)
        is_new_object = True
        line_to_write = "{params}\t{name}{id}\n".format(params=line.strip("\n"), name=rel.name.lower(), id=i)
        in_file.write(line_to_write)
    return is_new_object

def get_locus_from_dimenstion(dimension, loci):
    # Helper function for getting the best locus of an  object
    f = open(os.path.join(souffle_out_dir, "Dimension" + dimension + ".csv"), "r")
    for line in f.readlines():
        locus = get_obj_from_line(line)[0]
        if locus in loci:
            f.close()
            return locus
    f.close()

def get_best_locus(obj_id):
    # Get an object id, return a locus id with minimal dimension from all the loci the object is in.
    # If the object isn't in any locus - return  None
    loci = []
    f = open(os.path.join(souffle_out_dir, "In.csv"), "r")
    for line in f.readlines():
        obj, locus_id = get_obj_from_line(line)
        if obj == obj_id:
            loci.append(locus_id)
    f.close()

    dimension0_locus = get_locus_from_dimenstion("0", loci)
    if dimension0_locus:
        return dimension0_locus
        
    dimension1_locus = get_locus_from_dimenstion("1", loci)
    if dimension1_locus:
        return dimension1_locus

def create_folder():
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
    # TODO: Create appropriate facts file from the input
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
    in_dir = os.path.join("tmpInput", exercise_name)
    for file_name in os.listdir(in_dir):
        if file_name.endswith(".facts"):
            shutil.copyfile(os.path.join(in_dir, file_name), os.path.join(souffle_in_dir, file_name))

create_folder()
output_var = parse_spec() # Currentlhy parse spec only gives the output variables
move_input_to_folder()
deductive_synthesis()
for var in output_var:
    best_locus = get_best_locus(var)
    if best_locus:
        print(var + " is inside this locus: " + best_locus)
    else:
        print("Couldn't find a locus for " + var)
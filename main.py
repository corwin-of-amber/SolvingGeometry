# Goal: Make the first example work (Isosceles triangle)
# read input file?
# run souffle iterativly - create facts for make relations if needed
# get c locus and dimension for each option (In relation)
# Choose the locus with lowest dimension, search it for the correct answer

import os
import shutil

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

in_dir = "triangle"
script = "triangle.dl"
out_dir = "triangle"

def get_obj_from_line(line):
    return line.strip("\n").split("\t")


def run_souffle():
    os.system("souffle -F {in_dir} {script} -D {out_dir}".format(in_dir=in_dir, script=script, out_dir=out_dir))

def add_facts_to_relation(rel):
    # The function read outpus of last souffle run, look for new objects from 'make' relations, and create appropriate facts. Return True if a new fact was added
    is_new_object = False

    # Read output file of the make relation
    r_out_path = os.path.join(out_dir, rel.make_name + ".csv")
    lines = []
    if (os.path.isfile(r_out_path)):
        with open(r_out_path, "r") as f:
            lines = f.readlines()
    
    # look for new objects and write them as input for the relation
    in_file = open(os.path.join(out_dir, rel.name + ".facts"), "a")
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

def get_best_locus(obj_id):
    # Get an object id, return a locus id with minimal dimension from all the loci the object is in.
    # If the object isn't in any locus - return  None
    loci = []
    f = open(os.path.join(out_dir, "In.csv"), "r")
    for line in f.readlines():
        obj, locus_id = get_obj_from_line(line)
        if obj == obj_id:
            loci.append(locus_id)
    f.close()

    f = open(os.path.join(out_dir, "Dimension0.csv"), "r")
    for line in f.readlines():
        locus = get_obj_from_line(line)[0]
        if locus in loci:
            f.close()
            return locus
    f.close()

    f = open(os.path.join(out_dir, "Dimension1.csv"), "r")
    for line in f.readlines():
        locus = get_obj_from_line(line)
        if locus in loci:
            f.close()
            return locus
    f.close()

def create_folder():
    if (os.path.isdir(out_dir)):
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)

create_folder()
is_new_object = True
while is_new_object:
    is_new_object = False
    print("Running souffle...\n")
    run_souffle()
    for rel in make_relations:
        if add_facts_to_relation(rel):
            is_new_object = True

best_locus = get_best_locus("c")
if best_locus:
    print("c  is inside this locus: " + best_locus)
else:
    print("Couldn't find a locus for c")
import parser
import synthesis
import hillClimbing
import os
from sympy import *
import hillClimbing
import samples
from collections import  namedtuple

# name: [predicate_name, list_of_vars]
SAMPLES = {"triangle": [
            ["dist", ("X",  "Y", "d")],
            ["dist", ("Z",  "Y", "d")],
            ["known", ("X",  Point(0, 0))],
            ["known", ("Z",  Point(1, 0))],
            ["known", ("d",  1)],
            ["output",  ("Y")]
        ],
"square2": [
            ["makeLine", ("A", "B")],
            ["makeLine", ("B", "C")],
            ["dist", ("A", "B", "d")],
            ["dist", ("B", "C", "d")],
            ["dist", ("C", "D", "d")],
            ["rightAngle", ("A", "B", "C")],
            ["known", ("A", Point(0, 0))],
            ["known",  ("B", Point(1,  0))],
            ["known", ("d", 1)]
        ]
}

# Different functions for various ways to run the program (so that we are able to run each part seperately, as well as everything together)

def skip_front(exercise_name):
    # Allows to uses input from sample and  skip the front
    statements=parser.build_statements(SAMPLES[exercise_name])
    return statements

def get_partial_prog_from_dl(exercise_name, dl_script_path=None):
    if not dl_script_path:
        dl_script_path = script = os.path.join("tmpInput", exercise_name + ".dl")
    statements = parser.parse_dl(dl_script_path)
    exercise = synthesis.Exercise(exercise_name)
    exercise.build_exercise_from_dl(
                    dl_file=dl_script_path,
                    output_vars=synthesis.SAMPLES[exercise_name][0],
                    known_symbols=synthesis.SAMPLES[exercise_name][1]
                    )
    partial_prog = synthesis.main(exercise=exercise, exercise_name=exercise_name, statements=statements)
    return partial_prog

def is_point(val):
    return isinstance(val, Point)

def get_input_points(input_text):
    # Return the list of points in the input
    statements = parser.parse_free_text(input_text)
    input_points = []
    for s in statements:
        if s.predicate == "known":
            symbol = s.vars[0]
            val = s.vars[1]
            if is_point(val):
                input_points.append((symbol, val))
    return input_points

def get_output(input_text):
    # Get input from the user, return the partial program, the output points and output lines\rays\segments
    statements = parser.parse_free_text(input_text)
    partial_prog = synthesis.main(exercise_name=exercise_name, statements=statements)
    print("Partial program is: ")
    print(partial_prog)
    print("Perform numeric search")
    results = hillClimbing.hillClimbing(partial_prog.known, partial_prog.rules, not_equal=partial_prog.not_equal_rules, not_in=partial_prog.not_in_rules, not_collinear=partial_prog.not_colinear, not_intersect_2_segments=partial_prog.not_intersect_2_segments)
    
    # Get the output points
    out_points = []
    # Results is a dictionary
    for var_name, val in results.items():
        if is_point(val):
            out_points.append((var_name, val))
            
    # Get segments\ lines\ rays
    out_lines = () # TODO: Do something here
    
    output = namedtuple("output", "partial_prog output_points output_lines")
    return output(str(partial_prog), out_points, out_lines)
    
if __name__ == '__main__':
    print("In main")
    exercise_name = "triangle"
    input_text = samples.SAMPLES[exercise_name]
    print(get_input_points(input_text))
    output = get_output(input_text)
    print("Get output: ")
    print(output)
    print("partial prog: ")
    print(output.partial_prog)
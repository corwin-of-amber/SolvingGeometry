import front
import synthesis
import hillClimbing
import os
from sympy import *
import hillClimbing

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
    statements=front.build_statements(SAMPLES[exercise_name])
    return statements

def get_partial_prog_from_dl(exercise_name, dl_script_path=None):
    if not dl_script_path:
        dl_script_path = script = os.path.join("tmpInput", exercise_name + ".dl")
    statements = front.parse_dl(dl_script_path)
    exercise = synthesis.Exercise(exercise_name)
    exercise.build_exercise_from_dl(
                    dl_file=dl_script_path,
                    output_vars=synthesis.SAMPLES[exercise_name][0],
                    known_symbols=synthesis.SAMPLES[exercise_name][1]
                    )
    partial_prog = synthesis.main(exercise=exercise, exercise_name=exercise_name, statements=statements)
    return partial_prog

if __name__ == '__main__':

    # known = {'X': Point(0, 0), 'Z': Point(1, 0), 'd': 1}
    # rules = [
    #     [':in', 'Y', ['circle(X, d)', 'circle(Z, d)']],
    #     ['assert', 'Y', 'abs(dist(X, Y) - d) + abs(dist(Z, Y) - d)']
    # ]
    print("In main")
    exercise_name = "pentagon"#"tut:middle-1"
    # TODO: square2 - doesnt work yet (make line)
    # TODO2: square-in-square also doesnt work
    statements = front.main(exercise_name=exercise_name)
    partial_prog = synthesis.main(exercise_name=exercise_name, statements=statements)
    print("Partial program is: ")
    print(partial_prog)
    print("Perform numeric search")
    hillClimbing.hillClimbing(partial_prog.known, partial_prog.rules)

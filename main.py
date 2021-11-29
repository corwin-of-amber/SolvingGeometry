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


def skip_front(exercise_name):
    # Allows to uses input from sample and  skip the front
    statements=front.build_statements(SAMPLES[exercise_name])
    return statements

if __name__ == '__main__':

    # known = {'X': Point(0, 0), 'Z': Point(1, 0), 'd': 1}
    # rules = [
    #     [':in', 'Y', ['circle(X, d)', 'circle(Z, d)']],
    #     ['assert', 'Y', 'abs(dist(X, Y) - d) + abs(dist(Z, Y) - d)']
    # ]
    print("In main")
    exercise_name = "pentagon"
    statements = front.main(exercise_name=exercise_name)
    partial_prog = synthesis.main(exercise_name=exercise_name, statements=statements)
    print("Partial program is: ")
    print(partial_prog)
    print("Perform numeric search")
    hillClimbing.hillClimbing(partial_prog.known, partial_prog.rules)

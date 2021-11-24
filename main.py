import front
import synthesis
import hillClimbing
import os
from sympy import *
import hillClimbing

exercise_name = "triangle"
script = os.path.join("tmpInput", exercise_name + ".dl")

# Create input statements from the front
statements = front.parse_input(script)
# TODO: Move SAMPLES here
exercise = synthesis.SAMPLES[exercise_name]


print("Partial program is: ")
partial_prog = synthesis.main(exercise, exercise_name=exercise_name, statements=statements)
print(partial_prog)

if __name__ == '__main__':

    known = {'X': Point(0, 0), 'Z': Point(1, 0), 'd': 1}
    rules = [
        [':in', 'Y', ['circle(X, d)', 'circle(Z, d)']],
        ['assert', 'Y', 'abs(dist(X, Y) - d) + abs(dist(Z, Y) - d)']
    ]
    print(partial_prog.known)
    print(partial_prog.rules)
    print("Perform numeric search")
    hillClimbing.hillClimbing(partial_prog.known, partial_prog.rules)

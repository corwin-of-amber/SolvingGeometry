import front
import synthesis
import hillClimbing
import os
from sympy import Ray, Point, Line, Segment, intersection, Circle, pi, cos, sin, sqrt
import hillClimbing

exercise_name = "square"
script = os.path.join("tmpInput", exercise_name + ".dl")

# Create input statements from the front
statements = front.parse_input(script)
# TODO: Move SAMPLES here
exercise = synthesis.SAMPLES[exercise_name]


# print("Partial program is: ")
# partial_prog = synthesis.main(exercise, exercise_name=exercise_name, statements=statements)
# print(partial_prog)

if __name__ == '__main__':
    known = {'A': Point(0, 0), 'B': Point(1, 0)}
    rules = [
        [':in', 'C', ['circle(B, dist(A, B))']],
        [':in', 'D', ['circle(A, dist(A, B))','circle(C, dist(A, B))']],
        ['assert', 'abs(angleCcw(A, D, C) - pi/2)']
    ]
    # known = {'X': Point(0, 0), 'Z': Point(1, 0), 'd': 1}
    # rules = [
    #     [':in', 'Y', ['circle(X, d)', 'circle(Z, d)']],
    #     ['assert', 'abs(dist(X, Y) - d) + abs(dist(Z, Y) - d)']
    # ]
    print("Perform numeric search")
    hillClimbing.hillClimbing(known, rules)

import front
import synthesis
import os

exercise_name = "triangle"
script = os.path.join("tmpInput", exercise_name + ".dl")

# Create input statements from the front
statements = front.parse_input(script)

# TODO: Move SAMPLES here
exercise = synthesis.SAMPLES[exercise_name]


print("Partial program is: ")
partial_prog = synthesis.main(exercise, exercise_name=exercise_name, statements=statements)
print(partial_prog)


import json
from timeit import timeit
from sympy import Number
from sympy.geometry import Point2D, Segment2D

import parser
import synthesis
import hillClimbing
import samples


class TestFixture:

    def __init__(self):
        self.results = {}

    def run_tests(self, tests):
        for title, input_text in tests.items():
            print(f"\n\n#\n## {title}\n#")
            self.run_test(title, input_text)

    def run_test(self, title, input_text):
        out = []
        elapsed = timeit(lambda: out.append(self._run_test(title, input_text)), number=1)
        self.results[title] = {'out': out[0], 'elapsed': elapsed}

    def _run_test(self, title, input_text):
        # Get input from the user, return the partial program, the output points and output lines\rays\segments
        statements = parser.parse_free_text(input_text)
        partial_prog = synthesis.main(exercise_name=title, statements=statements)
        print("Partial program is: ")
        print(partial_prog)
        print("Perform numeric search")
        results = hillClimbing.solve_numerical(partial_prog.known, partial_prog.rules, not_equal=partial_prog.not_equal_rules, not_in=partial_prog.not_in_rules, not_collinear=partial_prog.not_colinear, not_intersect_2_segments=partial_prog.not_intersect_2_segments)
        print("numeric search results are: ")
        print(results)
        return {'partial_prog': partial_prog.rules, 'solution': self._serialize(results)}

    def _serialize(self, v):
        _ = self._serialize
        if isinstance(v, Point2D):
            return (float(v.x), float(v.y))
        elif isinstance(v, Segment2D):
            return [_(v.p1), _(v.p2)]
        elif isinstance(v, dict):
            return {k: self._serialize(u) for k, u in v.items()}
        else:
            # assume it's a numeric value
            return float(v)


if __name__ == '__main__':
    tf = TestFixture()
    try:
        tf.run_tests(samples.SAMPLES)
    finally:
        with open('test-results.json', 'w') as outf:
            outf.write(json.dumps(tf.results, indent=4))
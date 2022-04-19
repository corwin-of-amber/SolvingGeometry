from flask import Flask, Response, request, jsonify, send_from_directory
import json
from serialization import json_custom
import parser
import samples
import synthesis
import hillClimbing
from collections import namedtuple
import backend_shapely as backend

HOST = 'localhost'
PORT = 8000
UI_BUILD_DIR = "../UI/build"

app = Flask(__name__, static_url_path="/", static_folder=UI_BUILD_DIR)

SolutionResponse = namedtuple("output", "partial_prog output_points output_lines")



@app.route('/')
def index():
    return send_from_directory(UI_BUILD_DIR, 'index.html')

@app.route("/samples")
def samples_index():
    return json.dumps(samples.SAMPLES)

@app.route("/compile", methods=["POST"])
def compile_request():
    data = str(request.data, 'utf-8')

    statements = parser.parse_free_text(data)
    for s in statements:
        print(s)

    result = {"statements": statements}

    return json_custom(result)

def _get_points_coordinates(point_name, all_points):
    assert(point_name in all_points)
    return all_points[point_name]

def memoize_one(func):
    memo = {}
    def decorated(arg):
        try:
            return memo[arg]
        except KeyError:
            memo.clear()   # save at most one result
            memo[arg] = res = func(arg)
            return res
    return decorated

@memoize_one
def synthesize(input_text):
    statements = parser.parse_free_text(input_text)
    partial_prog = synthesis.main(statements=statements)
    return statements, partial_prog

def synthesize_and_solve(input_text):
    # Get input from the user, return the partial program, the output points and output lines\rays\segments
    statements, partial_prog = synthesize(input_text)
    print("Partial program is: ")
    print(partial_prog)
    # print("Perform numeric search")
    results = hillClimbing.hillClimbing(partial_prog.known, partial_prog.rules, not_equal=partial_prog.not_equal_rules, not_in=partial_prog.not_in_rules, not_collinear=partial_prog.not_colinear, not_intersect_2_segments=partial_prog.not_intersect_2_segments)
    # print("numeric search results are: ")
    # print(results)
    # Get the output points
    out_points = {}
    # Results is a dictionary
    for var_name, val in results.items():
        if backend.is_point(val):
            out_points[var_name] = (val.x, val.y)
            
    # Get segments and circles to draw
    # draw only draw_circle\draw_segment statements
    # Get the points coordinates from the hill climbing results
    out_lines = []
    for s in statements:
        if s.predicate == "drawSegment":
            # Format for segment: (a.x, a.y, b.x, b.y)
            point_a = s.vars[0]
            point_b = s.vars[1]
            segment_ab = (*_get_points_coordinates(point_a, out_points), 
            *_get_points_coordinates(point_b, out_points))
            out_lines.append(segment_ab)
        if s.predicate == "draw_circle":
            # Format for circle: (a.x, a.y, r)
            point_a = s.vars[0]
            radius = s.vars[1]
            circle_a = (*_get_points_coordinates(point_a, out_points), radius)
            out_lines.append(circle_a)
    
    return SolutionResponse(str(partial_prog), out_points, out_lines)

@app.route("/presolve", methods=["POST"])
def presolve_request():
    data = str(request.data, 'utf-8')
    statements, partial_prog = synthesize(data)
    out = SolutionResponse(partial_prog.rules, [], [])
    return json_custom(out)

@app.route("/solve", methods=["POST"])
def solve_request():
    data = str(request.data, 'utf-8')
    out = synthesize_and_solve(data)
    print(out)
    return json_custom(out)


if __name__ == '__main__':
    app.run(debug=True, port=PORT, host=HOST)




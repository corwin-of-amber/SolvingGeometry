from flask import Flask, render_template, request
from markupsafe import escape
import json

import front


app = Flask(__name__, template_folder="src/ui",
            static_url_path="/ui", static_folder="build/ui")

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/samples")
def samples_index():
    return json.dumps(front.SAMPLES)

@app.route("/solve", methods=["POST"])
def solve_request():
    data = json.loads(request.data)

    print("TODO invoke solver on data")

    result = {}

    return json.dumps(result)


if __name__ == '__main__':
    app.run(port=2080, debug=True)
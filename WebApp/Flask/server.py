from flask import Flask, Response, request, jsonify, send_from_directory
import json
from serialization import json_custom


HOST = 'localhost'
PORT = 8000
UI_BUILD_DIR = "../UI/build"

app = Flask(__name__, static_url_path="/", static_folder=UI_BUILD_DIR)

def create_response(status_code:int) -> Response:

    status_text_dict = {
        200:"OK",
        204: "No Content",
        302: "Found",
        401:"Unauthorized",
        404:"not found",
        409:"conflict",
        500:"internal server error"
    }
    status_text = status_text_dict[status_code]

    return Response(status_text,status_code)




@app.route('/')
def index():
    return send_from_directory(UI_BUILD_DIR, 'index.html')

@app.route("/samples")
def samples_index():
    import samples
    return json.dumps(samples.SAMPLES)

@app.route("/compile", methods=["POST"])
def compile_request():
    data = str(request.data, 'utf-8')

    import parser
    statements = parser.parse_free_text(data)
    for s in statements:
        print(s)

    result = {"statements": statements}

    return json_custom(result)

@app.route("/solve", methods=["POST"])
def solve_request():
    data = str(request.data, 'utf-8')

    print("TODO invoke solver on data", data)

    result = {}

    return json_custom(result)


# @app.route('/add_reply/', methods=['GET'])
# def addReply():
#     try:
#         id = request.args.get('userTelegramID')
#         answer = request.args.get('Answer')
#         pollID = request.args.get('PollID')
#         status_code = updateReplyInDB(id, answer, pollID)
#         return create_response(status_code)
#     except:
#         return create_response(status_code=500)
#
#
# @app.route('/get_all_admins/', methods=['POST'])
# def getAllAdmins():
#     try:
#         body = request.get_json()
#         status_code = isAdminRegistered(body['username'], body['password'])
#         if status_code == 500:
#             return create_response(status_code)
#         elif status_code != 200:
#             return create_response(401)
#
#         status_code, admins = getAllAdminsFromDB()
#
#         if status_code == 500:
#             raise
#
#         return jsonify({"admins": admins})
#     except:
#         return create_response(status_code=500)



# ---------------------------static functions--------------------------------#


if __name__ == '__main__':
    app.run(debug=True, port=PORT, host=HOST)




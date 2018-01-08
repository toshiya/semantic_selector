from flask import Flask, request, jsonify, make_response
from semantic_selector.estimator.fnn_simple import FNNSimpleEstimator
from semantic_selector.adapter.inference import JSONInferenceAdapter


app = Flask(__name__)
model = None


@app.before_first_request
def startup():
    global model
    print("initializing model...")
    model = FNNSimpleEstimator()
    options = {}
    adapter = JSONInferenceAdapter(options)
    model.set_adapter(adapter)
    model.load("models/fnn_simple")


@app.route("/api/inference", methods=['POST'])
def inference():
    global model
    if request.headers['Content-Type'] != 'application/json':
        return make_response("Content-Type must be application/json", 400)

    if "html" not in request.json.keys():
        err_message = 'request body json must contain "html" attributes'
        return make_response(err_message, 400)

    options = {"record": {'html': request.json["html"]}}
    model.adapter.set_options(options)
    estimated_topic = model.predict()
    res = {"topic": estimated_topic}
    return jsonify(res)

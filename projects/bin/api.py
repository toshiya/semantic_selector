from attrdict import AttrDict
from flask import Flask, request, jsonify, make_response, g
from semantic_selector.model.one_to_one import NNFullyConnectedModel

import os
import yaml

app = Flask(__name__)
model = None

@app.before_first_request
def startup():
    global model
    print("initializing model...")
    model = NNFullyConnectedModel()
    model.load()

@app.route("/api/inference", methods=['POST'])
def inference():
    global model
    if request.headers['Content-Type'] != 'application/json':
        return make_response("Content-Type must be application/json", 400)

    if "html" not in request.json.keys():
        err_message = 'request body json must contain "html" attributes'
        return make_response(err_message, 400)

    target_tag = AttrDict({'html': request.json["html"]})
    estimated_topic = model.inference_html(target_tag)
    res = {"topic": estimated_topic}
    return jsonify(res)

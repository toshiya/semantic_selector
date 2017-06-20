from flask import Flask, request, jsonify, make_response, g
from semantic_selector import ml_model
from semantic_selector import datasource

app = Flask(__name__)

def get_model():
    if not hasattr(g, 'model'):
        g.model = ml_model.LsiModel(grouping=None)
    return g.model

@app.teardown_appcontext
def close_db(error):
    datasource.InputTags.cleanup()


@app.route("/inference", methods=['POST'])
def inference():
    if request.headers['Content-Type'] != 'application/json':
        return make_response("Content-Type must be application/json", 400)

    model = get_model()
    target_tag = request.json["html"]
    estimated_label = model.grouped_label_name_from_id(
            model.inference_html(target_tag)
            )
    res = { "label" : estimated_label  }
    return jsonify(res)

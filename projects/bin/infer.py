#!/usr/bin/env python
import argparse
from semantic_selector.estimator.lsi import LsiEstimator
from semantic_selector.estimator.fnn_simple import FNNSimpleEstimator
from semantic_selector.adapter.inference import JSONInferenceAdapter


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--html', nargs='?', help='input html string')
    parser.add_argument('--model_name', nargs='?',
                        help='model to use', default="fnn_simple")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    input_html = args.html
    model_name = args.model_name
    if model_name == "fnn_simple":
        model = FNNSimpleEstimator()
        options = {
            "record": {'html': input_html}
        }
        adapter = JSONInferenceAdapter(options)
        model.set_adapter(adapter)
        model.load("models/fnn_simple")
        topic = model.predict()
        print("infered topic: " + topic)
        if args.debug:
            prob_vec = model.predict_with_prob_vec()
            model.print_probalitity(prob_vec)
    elif model_name == "lsi":
        model = LsiEstimator()
        options = {
            "record": {'html': input_html}
        }
        adapter = JSONInferenceAdapter(options)
        model.set_adapter(adapter)
        model.load("models/lsi")
        topic = model.predict()
        print("infered topic: " + topic)


if __name__ == '__main__':
    main()

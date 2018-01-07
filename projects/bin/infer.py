#!/usr/bin/env python
import sys
import argparse
from semantic_selector.estimator.lsi import LsiEstimator
from semantic_selector.adapter.inference import JSONInferenceAdapter


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--html', nargs='?', help='input html string')
    parser.add_argument('--model_name', nargs='?',
                        help='model to use', default="fnn_simple")
    args = parser.parse_args()
    input_html = args.html
    model_name = args.model_name
    if model_name == "fnn_simple":
        pass
    else:
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

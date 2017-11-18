#!/usr/bin/env python
import sys
import os
import yaml
import argparse
from semantic_selector.model.one_to_one import NNFullyConnectedModel
from semantic_selector.adapter.one_to_one import MySQLToNNFullyConnectAdapter
from semantic_selector.mysql import InputTable


def main():
    '''
        ./bin/infer_test
    '''

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--threashold', type=int, nargs='?', help='a threashold of the number of topics', default=10)
    parser.add_argument('--ratio_test', type=float, nargs='?', help='a ratio of test sets', default=0.2)
    parser.add_argument('--model_name', nargs='?', help='model to use', default="nn_fc")
    parser.add_argument('--seed', type=int, nargs='?', help='seed of np.random', default=100)
    parser.add_argument('--epochs', type=int, nargs='?', help='seed of np.random', default=400)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    model_name = args.model_name
    print("model type: %s" % (model_name))
    if model_name == "nn_fc":
        model = NNFullyConnectedModel()
        adapter = MySQLToNNFullyConnectAdapter(args.threashold, args.ratio_test, args.seed)
        model.train(adapter, args.epochs)
    else:
        print("model %s unknown" % (model_name))
        sys.exit(1)

    if args.debug:
        print("failing inferences\n")
        print("estimated, correct")
        for t in tests:
            estimated_topic = model.inference_html(t)
            correct_topic = t.canonical_topic
            if estimated_topic != correct_topic:
                print(estimated_topic + "," + correct_topic)

    model.save()

if __name__ == '__main__':
    main()

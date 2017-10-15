#!/usr/bin/env python
import sys
import os
import yaml
import argparse
from semantic_selector import lsi_model
from semantic_selector import nn_fc_model
from semantic_selector import chainer_model
from semantic_selector import datasource


def main():
    '''
        ./bin/infer_test
    '''

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--threashold', type=int, nargs='?', help='a threashold of the number of labels', default=10)
    parser.add_argument('--ratio_test', type=float, nargs='?', help='a ratio of test sets', default=0.05)
    parser.add_argument('--model_name', nargs='?', help='model to use', default="nn_fc")
    parser.add_argument('--seed', type=int, nargs='?', help='seed of np.random', default=100)
    args = parser.parse_args()

    (training, tests) = datasource.InputTags(args.threashold).fetch_data(args.ratio_test, args.seed)

    model_name = args.model_name
    print("model type: %s" % (model_name))
    if model_name == "nn_fc":
        model = nn_fc_model.NNFullyConnectedModel(training, tests)
    elif model_name == "chainer":
        model = chainer_model.ChainerModel(training, tests)
    elif model_name == "lsi":
        model = lsi_model.LsiModel(training)
    else:
        print("model %s unknown" % (model_name))
        sys.exit(1)


    print("failing inferences\n")
    print("estimated, correct")
    positive_hit = 0
    for t in tests:
        estimated_label = model.inference_html(t)
        correct_label = t.label
        if estimated_label != correct_label:
            print(estimated_label + "," + correct_label)
        if estimated_label == correct_label:
            positive_hit += 1

    print()
    print("# of test data: " + str(len(tests)))
    print("# of training_data: " + str(len(training)))
    print("Accuracy,", positive_hit / len(tests))
    print("Recall,", (positive_hit / len(tests)))


if __name__ == '__main__':
    main()

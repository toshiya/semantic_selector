#!/usr/bin/env python
import sys
import os
import yaml
import argparse
from semantic_selector.model.one_to_one import NNFullyConnectedModel
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

    (training, tests) = InputTable(args.threashold).fetch_data(args.ratio_test, args.seed)

    model_name = args.model_name
    print("model type: %s" % (model_name))
    if model_name == "nn_fc":
        model = NNFullyConnectedModel()
    else:
        print("model %s unknown" % (model_name))
        sys.exit(1)

    model.train(training, tests, args.epochs)
    if args.debug:
        print("failing inferences\n")
        print("estimated, correct")
        for t in tests:
            estimated_topic = model.inference_html(t)
            correct_topic = t.canonical_topic
            if estimated_topic != correct_topic:
                print(estimated_topic + "," + correct_topic)


    print()

    num_unknown = 0
    for t in training:
        if t.canonical_topic == 'unknown':
            num_unknown += 1
    print('# of unknown in training: ' + str(num_unknown))

    num_unknown = 0
    for t in tests:
        if t.canonical_topic == 'unknown':
            num_unknown += 1
    print('# of unknown in test: ' + str(num_unknown))
    print("# of test data: " + str(len(tests)))
    print("# of training_data: " + str(len(training)))
    model.save()

if __name__ == '__main__':
    main()

#!/usr/bin/env python
import sys
import argparse
from semantic_selector.estimator.lsi import LsiEstimator
from semantic_selector.estimator.fnn_simple import FNNSimpleEstimator
from semantic_selector.adapter.training import MySQLTrainingAdapter


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--threashold', type=int, nargs='?',
                        help='a threashold of the number of topics',
                        default=10)
    parser.add_argument('--ratio_test', type=float, nargs='?',
                        help='a ratio of test sets', default=0.2)
    parser.add_argument('--model_name', nargs='?',
                        help='model to use', default="fnn_simple")
    parser.add_argument('--seed', type=int, nargs='?',
                        help='seed of np.random', default=100)
    parser.add_argument('--epochs', type=int, nargs='?',
                        help='seed of np.random', default=400)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    model_name = args.model_name
    print("model type: %s" % (model_name))
    if model_name == "fnn_simple":
        model = FNNSimpleEstimator()
        options = {
            'threashold': args.threashold,
            'ratio_test': args.ratio_test,
            'seed': args.seed,
        }
        adapter = MySQLTrainingAdapter(options)
        model.set_adapter(adapter)
        model.train({'epochs': args.epochs, 'verbose': args.debug})
        model.save("./models/fnn_simple")
    elif model_name == "lsi":
        model = LsiEstimator()
        options = {
            'threashold': args.threashold,
            'ratio_test': args.ratio_test,
            'seed': args.seed,
        }
        adapter = MySQLTrainingAdapter(options)
        model.set_adapter(adapter)
        model.train()
        model.save("./models/lsi")
    else:
        print("model %s unknown" % (model_name))
        sys.exit(1)


if __name__ == '__main__':
    main()

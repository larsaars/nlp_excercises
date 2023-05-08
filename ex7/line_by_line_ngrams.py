#!/usr/bin/env python3

import argparse
import random

# define constants
START_SYMBOL = "<s>"
END_SYMBOL = "</s>"


# define functions for generating n-grams and building the model
def ngrams_from_text(f, N):
    """Generate n-grams from text"""
    for line in f:
        line = [START_SYMBOL] * (N - 1) + list(line.strip()) + [END_SYMBOL]
        for i in range(len(line) - N + 1):
            yield tuple(line[i:i + N])


def build_model(args):
    """Build the n-gram model from the input file"""
    model = {}
    with open(args.source, 'r', encoding='utf-8') as f:
        for ngram in ngrams_from_text(f, args.N):
            prefix, last = ngram[:-1], ngram[-1]
            node = model
            for c in prefix:
                node = node.setdefault(c, {})
            node[last] = node.get(last, 0) + 1

    return model


# define function for generating text from the model
def generate_text(model, args):
    """Generate text from the n-gram model"""
    
    # create start sequence

    start = [START_SYMBOL] * (args.N - 1) + list(args.start)
    start = start[-(args.N - 1):]

    while True:
        node = model
        for c in start:
            node = node.get(c)

            if node is None:
                break

        if node is None or not node:
            break

        chars, counts = zip(*node.items())
        char = random.choices(chars, weights=counts)[0]

        if char == END_SYMBOL:
            break

        yield char

        start = start[1:] + [char]


def main(args):
    random.seed(args.random_seed)
    model = build_model(args)
    text = ''.join(generate_text(model, args))
    print(args.start + text[:args.length])


if __name__ == '__main__':
    # create argparser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--random-seed', type=int, default=1,
                        help='Set random seed for replicability; 0 implies truly random seed')
    parser.add_argument('--source', type=str, required=True, help='Input text file')
    parser.add_argument('-N', type=int, default=3, help='Order of n-gram')
    parser.add_argument('--start', type=str, default='', required=False, help='Initial n-gram to start the generation')
    parser.add_argument('--length', type=int, default=5000, help='Length of generated text')

    args = parser.parse_args()

    # start program
    main(args)

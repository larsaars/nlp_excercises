#!/usr/bin/env python3

import argparse
import random
import math

# define constants
START_SYMBOL = "<s>"
END_SYMBOL = "</s>"


def ngrams_from_text(lines, N):
    """Generate n-grams from text"""

    for line in lines:
        # prepend start symbol (N - 1) times and append end symbol
        line = [START_SYMBOL] * (N - 1) + list(line.strip()) + [END_SYMBOL]

        # loop through all n-grams in the line and yield them
        for i in range(len(line) - N + 1):
            yield tuple(line[i:i + N])


def get_base_node(model, prefix):
    """from our model tree, get the node that represents the prefix (history)"""

    node = model

    # loop through all chars in prefix
    for c in prefix:
        node = node.get(c)

        # return empty dict if node is None
        if node is None:
            node = dict()
            break

    return node


def build_model(source, N):
    """Build the n-gram model in form of a nested dict structure
    from the input file"""

    model = dict()
    alphabet_base = dict()  # dict containing all the characters in the alphabet and their base probabilities (1)

    # open source file and loop through all n-grams
    with open(source, 'r', encoding='utf-8') as f:
        for ngram in ngrams_from_text(f, N):
            # get prefix and last character (char to be predicted)
            prefix, last = ngram[:-1], ngram[-1]

            # set root node of model as model itself
            node = model

            # loop through all characters in prefix and create nodes if they don't exist
            for c in prefix:
                node = node.setdefault(c, {})

            # at the end of the nested dict structure
            # increase the count when found by one
            # default value is 0 (laplace smoothing)
            node[last] = node.get(last, 1) + 1

            # add character to alphabet_base if not already in there
            alphabet_base[last] = 1

    return model, alphabet_base


def generate_text(model, alphabet_base, N, start):
    """Generate text from the n-gram model"""
    
    # create start prefix (as list)
    prefix = [START_SYMBOL] * (N - 1) + list(start)
    prefix = prefix[-(N - 1):]

    # loop as long as the end symbol is not found
    while True:
        # get the base node (node that represents the prefix)
        base_node = get_base_node(model, prefix)

        # insert into the alphabet base probabilities the probabilities of the base node create a copy of
        # alphabet_base and update it with the base node the effect of this is that all characters that are not in
        # the base node but in the alphabet base will have a weight of 1 (laplace smoothing)
        node = alphabet_base.copy()
        node.update(base_node)

        # next character is chosen randomly based on the weights
        chars, counts = zip(*node.items())
        char = random.choices(chars, weights=counts)[0]

        # break if end symbol is found
        if char == END_SYMBOL:
            break

        # yield generated character
        yield char

        # for next iteration, remove first character and append generated character
        prefix = prefix[1:] + [char]


def eval_model(model, alphabet_base, test_source, N):
    """Evaluate the model by calculating the cross entropy and perplexity"""

    # sum of log probabilities and count of ngrams
    log_prob = 0
    ngram_count = 0

    # open test source file and loop through all ngrams
    with open(test_source, 'r', encoding='utf-8') as f:
        for ngram in ngrams_from_text(f, N):
            # get base node for prefix
            node = get_base_node(model, ngram[:-1])

            # get count of last character (weight is 1 if not in node (laplace smoothing))
            count = node.get(ngram[-1], 1)

            # add log probability to sum (with laplace smoothing)
            weight_sum = sum(node.values()) + len(alphabet_base) - len(node)
            log_prob += math.log2(count / weight_sum)

            # increase ngram count by one
            ngram_count += 1

    # calculate cross entropy and perplexity
    cross_entropy = log_prob / ngram_count
    perplexity = 2 ** cross_entropy

    return cross_entropy, perplexity


def main(args):
    random.seed(args.random_seed)

    # build the model to be used for generation
    model, alphabet_base = build_model(args.source, args.N)

    # if given, evaluate the model
    if args.test_source:
        cross_entropy, perplexity = eval_model(model, alphabet_base, args.test_source, args.N)
        print(f'Cross entropy: {cross_entropy:.3f}')
        print(f'Perplexity: {perplexity:.3f}')

    # print the user defined start
    print(args.start, end='')

    # print characters while generating
    for c in generate_text(model, alphabet_base, args.N, args.start):
        print(c, end='')


if __name__ == '__main__':
    # create argparser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--random-seed', type=int, default=1,
                        help='Random seed for the random number generator')
    parser.add_argument('--source', type=str, required=True, help='Input text file')
    parser.add_argument('-N', type=int, default=3, help='Size of n-gram')
    parser.add_argument('--start', type=str, default='', required=False, help='Beginning of the generated text')
    parser.add_argument('--test-source', type=str, required=False, help='Test input text file. If given, the cross '
                                                                        'entropy and perplexity is calculated')

    args = parser.parse_args()

    # start program
    main(args)

#!/usr/bin/env python3
import dynet as dy
import random
import numpy as np

START_SYMBOL = "<s>"
END_SYMBOL = "</s>"

data = open('input.txt', 'r').read() # should be simple plain text file
characters = set(data)
characters.add(START_SYMBOL)
characters.add(END_SYMBOL)
characters = list(characters)
sentences = [x for x in data.splitlines() if x]

int2char = list(characters)
char2int = {c:i for i, c in enumerate(characters)}

MAX_EPOCHS = 5
VOCAB_SIZE = len(characters)
INPUT_DIM = VOCAB_SIZE
HIDDEN_DIM = 64

N = 7

pc = dy.ParameterCollection()
params = {}
#params["lookup"] = pc.add_lookup_parameters((VOCAB_SIZE, INPUT_DIM))
params["W1"] = pc.add_parameters((HIDDEN_DIM, (N - 1) * VOCAB_SIZE))
params["bias1"] = pc.add_parameters((HIDDEN_DIM,))
params["W2"] = pc.add_parameters((VOCAB_SIZE, HIDDEN_DIM))
params["bias2"] = pc.add_parameters((VOCAB_SIZE,))


# return the N-grams for the given sentence (as pairs, divided in history and symbol to be predicted)
def ngrams_from_sentence(sentence, N):
    prefix = [START_SYMBOL] * (N - 1) # start out with N-1 start symbols
    symbols = list(sentence) + [END_SYMBOL]
    for last in symbols:
        yield prefix, last
        prefix.append(last)
        prefix.pop(0)


# return compute loss of RNN for one sentence
def do_one_sentence(sentence):
    # setup the sentence
    dy.renew_cg()

    W1 = params["W1"]
    bias1 = params["bias1"]
    W2 = params["W2"]
    bias2 = params["bias2"]
    loss = []
    for history,next_char in ngrams_from_sentence(sentence, N):
        inputs = []
        for c in history:
            one_hot_vector = [0] * VOCAB_SIZE
            one_hot_vector[char2int[c]] = 1
            inputs.extend(one_hot_vector)
        input_layer = dy.inputVector(inputs)
        hidden_layer = dy.tanh(W1 * input_layer + bias1)
        probs = dy.softmax(W2 * hidden_layer + bias2)
        loss.append( -dy.log(dy.pick(probs,char2int[next_char])) )
    loss = dy.esum(loss)
    return loss


# generate from model:
def generate():
    # setup the sentence
    dy.renew_cg()

    W1 = params["W1"]
    bias1 = params["bias1"]
    W2 = params["W2"]
    bias2 = params["bias2"]
    history = [START_SYMBOL] * (N-1)
    out=["<s>"]

    while out[-1] != END_SYMBOL:
        inputs = []
        for c in history:
            one_hot_vector = [0] * VOCAB_SIZE
            one_hot_vector[char2int[c]] = 1
            inputs.extend(one_hot_vector)
        input_layer = dy.inputVector(inputs)
        hidden_layer = dy.tanh(W1 * input_layer + bias1)
        probs = dy.softmax(W2 * hidden_layer + bias2)
        probs = probs.npvalue()
        next_symbol = np.random.choice(VOCAB_SIZE, p=probs/probs.sum())
        next_char = int2char[next_symbol]
        out.append(next_char)
        history.append(next_char)
        history.pop(0)
    return "".join(out[1:-1]) # strip the start/end symbols


def multiple_train(trainer, sentences):
    i = 1
    aggr_loss = 0
    aggr_symbols = 0
    for sentence in sentences:
        loss = do_one_sentence(sentence)
        loss.backward()
        loss_value = loss.value()
        trainer.update()
        aggr_loss += loss_value
        aggr_symbols += len(sentence) + 1
        if i % 1000 == 0:
            print(i, aggr_loss/aggr_symbols, generate())
            aggr_loss = 0
            aggr_symbols = 0
        i += 1


trainer = dy.SimpleSGDTrainer(pc)
for _ in range(MAX_EPOCHS):
    random.shuffle(sentences)
    multiple_train(trainer, sentences)

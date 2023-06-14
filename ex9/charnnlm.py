#!/usr/bin/env python3
import dynet as dy
import random
import numpy as np
import math

START_SYMBOL = "<s>"
END_SYMBOL = "</s>"


data = open('input.txt', 'r').read() # should be simple plain text file
characters = set(data)
characters.add(START_SYMBOL)
characters.add(END_SYMBOL)
characters = list(characters)
sentences = [x for x in data.splitlines() if x]

int2char = list(characters)
char2int = {c:i for i,c in enumerate(characters)}

MAX_EPOCHS = 5
VOCAB_SIZE = len(characters)
INPUT_DIM = 32
HIDDEN_DIM = 64
LAYERS = 2

pc = dy.ParameterCollection()

rnn = dy.SimpleRNNBuilder(LAYERS, INPUT_DIM, HIDDEN_DIM, pc)
#rnn = dy.LSTMBuilder(LAYERS, INPUT_DIM, HIDDEN_DIM, pc)

params = {}
params["lookup"] = pc.add_lookup_parameters((VOCAB_SIZE, INPUT_DIM))
params["R"] = pc.add_parameters((VOCAB_SIZE, HIDDEN_DIM))
params["bias"] = pc.add_parameters((VOCAB_SIZE))


# return compute loss of RNN for one sentence
def do_one_sentence(rnn, sentence):
    # setup the sentence
    dy.renew_cg()
    s0 = rnn.initial_state()

    R = params["R"]
    bias = params["bias"]
    lookup = params["lookup"]
    sentence = [START_SYMBOL] + list(sentence) + [END_SYMBOL]
    sentence = [char2int[c] for c in sentence]
    s = s0
    loss = []
    for char,next_char in zip(sentence,sentence[1:]):
        s = s.add_input(lookup[char])
        probs = dy.softmax(R*s.output() + bias)
        loss.append( -dy.log(dy.pick(probs,next_char)) )
    loss = dy.esum(loss)
    return loss


# generate from model:
def generate(rnn):
    # setup the sentence
    dy.renew_cg()
    s0 = rnn.initial_state()

    R = params["R"]
    bias = params["bias"]
    lookup = params["lookup"]

    s = s0
    out=[START_SYMBOL]
    lines_generated = 0
    next_char = char2int[START_SYMBOL]
    while out[-1] != END_SYMBOL:
        s = s.add_input(lookup[next_char])
        probs = dy.softmax(R*s.output() + bias)
        probs = probs.npvalue()
        next_char = np.random.choice(VOCAB_SIZE, p=probs/probs.sum())
        out.append(int2char[next_char])
    return "".join(out[1:-1]) # strip the <s>/</s>


def assess(rnn, sentence):
    dy.renew_cg()
    crossentropy = 0
    R = params["R"]
    bias = params["bias"]
    lookup = params["lookup"]
    sentence = list(sentence) + [END_SYMBOL]
    s = rnn.initial_state().add_input(lookup[char2int[START_SYMBOL]])
    for symbol in sentence:
        probs = dy.softmax(R*s.output() + bias)
        probs = probs.npvalue()
        prob = probs[char2int[symbol]]
        #print("prob of {} is {}".format(symbol, prob))
        crossentropy -= math.log2(prob)
        s = s.add_input(lookup[char2int[symbol]])
    return crossentropy / len(sentence), crossentropy, len(sentence)


def multiple_train(trainer, rnn, sentences):
    i = 1
    aggr_loss = 0
    aggr_symbols = 0
    for sentence in sentences:
        loss = do_one_sentence(rnn, sentence)
        loss.backward()
        loss_value = loss.value()
        trainer.update()
        aggr_loss += loss_value
        aggr_symbols += len(sentence) + 1
        if i % 1000 == 0:
            print(i, aggr_loss/aggr_symbols, "\n\t", generate(rnn), "\n\t", assess(rnn, "His tender heir might bear his memory:"))
            aggr_loss = 0
            aggr_symbols = 0
        i += 1


trainer = dy.SimpleSGDTrainer(pc)
for _ in range(MAX_EPOCHS):
    random.shuffle(sentences)
    multiple_train(trainer, rnn, sentences)

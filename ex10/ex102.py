import dynet as dy
import random

START_SYMBOL = "<s>"
END_SYMBOL = "</s>"

lines = open('data/Cocolab_DE.lex', 'r').read().splitlines()

# Preprocessing: Create vocabulary and convert graphemes and phonemes to indices
grapheme_vocab = set()
phoneme_vocab = set()

for line in lines:
    grapheme, phoneme = line.split("\t")
    grapheme_vocab.update(grapheme)
    phoneme_vocab.update(phoneme.split())

grapheme_vocab.add(START_SYMBOL)
grapheme_vocab.add(END_SYMBOL)

grapheme2int = {c: i for i, c in enumerate(grapheme_vocab)}
int2grapheme = list(grapheme_vocab)
phoneme2int = {c: i for i, c in enumerate(phoneme_vocab)}
int2phoneme = list(phoneme_vocab)

VOCAB_SIZE = len(grapheme_vocab)
PHONEME_SIZE = len(phoneme_vocab)

MAX_EPOCHS = 50
STOP_EARLY = True  # stop early if there's no change for a while

INPUT_DIM = 64
HIDDEN_DIM = 32
LAYERS = 1

random.shuffle(lines)
training_data = []

for line in lines:
    grapheme, phoneme = line.split("\t")
    grapheme_indices = [grapheme2int[c] for c in grapheme]
    phoneme_indices = [phoneme2int[p] for p in phoneme.split()]
    training_data.append((grapheme_indices, phoneme_indices))

pc = dy.ParameterCollection()
encoder_rnn = dy.LSTMBuilder(LAYERS, INPUT_DIM, HIDDEN_DIM, pc)
decoder_rnn = dy.LSTMBuilder(LAYERS, INPUT_DIM + HIDDEN_DIM, HIDDEN_DIM, pc)

params = {}
params["encoder_lookup"] = pc.add_lookup_parameters((VOCAB_SIZE, INPUT_DIM))
params["decoder_lookup"] = pc.add_lookup_parameters((PHONEME_SIZE, INPUT_DIM))
params["W"] = pc.add_parameters((PHONEME_SIZE, HIDDEN_DIM))
params["bias"] = pc.add_parameters((PHONEME_SIZE,))


# Return the encoding of a grapheme sequence
def encode_sequence(graphemes):
    dy.renew_cg()
    encoder_lookup = params["encoder_lookup"]
    s = encoder_rnn.initial_state()
    rnn_output = s.transduce([encoder_lookup[grapheme] for grapheme in graphemes])[-1]
    return rnn_output


# Return the decoded phoneme sequence given the encoding
def decode_sequence(encoding, target_sequence):
    dy.renew_cg()
    decoder_lookup = params["decoder_lookup"]
    W = params["W"]
    bias = params["bias"]
    s = decoder_rnn.initial_state(dy.concatenate([encoding, dy.inputTensor([0] * INPUT_DIM)]))
    decoded_phonemes = []
    for target in target_sequence:
        s = s.add_input(decoder_lookup[target])
        rnn_output = s.output()
        probs = dy.softmax(W * rnn_output + bias)
        prediction = dy.argmax(probs)
        decoded_phonemes.append(int(prediction.value()))
    return decoded_phonemes


# Example usage
graphemes = [START_SYMBOL] + list("erfüllt") + [END_SYMBOL]
encoding = encode_sequence([grapheme2int[grapheme] for grapheme in graphemes]).npvalue()

target_phonemes = [phoneme2int[p] for p in "E 6 f Y l t".split()]
decoded_phonemes = decode_sequence(encoding, target_phonemes)
decoded_phonemes = [int2phoneme[phoneme] for phoneme in decoded_phonemes]

print("Graphemes:", graphemes)
print("Target Phonemes:", "E 6 f Y l t".split())
print("Decoded Phonemes:", decoded_phonemes)
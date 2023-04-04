import grammar
import parse
import parser

with open("../data/telescope.srgs", "r") as f:
    lines = f.readlines()
    #print("".join(lines))
    gr = grammar.Grammar(lines)
print(gr)

# print(parser.example_telescope_parse().to_dot())

sentence = "I saw the duck with a telescope"
tokens = sentence.split(" ")

# print(f'Is in grammar: {parser.is_in_language(tokens, gr)}')

parsing_results = parser.parse(tokens, gr)  

print(f'Parsing results: {parsing_results}')
# one of the parsing results should yield the same result as the example from above
# assert repr(parser.example_telescope_parse()) in map(repr, parsing_results)

#!/usr/bin/env python3

import grammar
import parse
import parser

if __name__ == "__main__":
    with open("grammar.srgs", "r") as f:
        lines = f.readlines()
        gr = grammar.Grammar(lines)

    sentence = "I saw the duck with a telescope"
    tokens = sentence.split(" ")

    print(f'Is in grammar: {parser.is_in_language(tokens, gr)}')

    gr.to_CNF()
    print(gr)

    print(f'Is in grammar: {parser.is_in_language(tokens, gr)}')
    for res in parser.parse(tokens, gr):
        print(res.to_dot())
#     print()
# 
#     parsing_results = parser.parse(tokens, gr)
# 
#     print('Parsing results (in dot format):')
#     for result in parsing_results:
#         print()
#         print(result.to_dot())
# 
#     print(f'A total of {len(parsing_results)} parsing results were found.')

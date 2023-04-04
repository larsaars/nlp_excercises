from grammar import *
from parse import *


def is_in_language(words: list, grammar: Grammar) -> bool:
    """returns True if the list of words is in the language of grammar"""""

    # if at least one parse exists, the list of words is in the language
    return len(parse(words, grammar)) > 0
    

def build_parse_tree(words: list, grammar: Grammar, T: list, i: int, j: int, symbol: Symbol) -> ParseTree:
    """builds a parse tree for the list of words with grammar and returns it.
    """

    for k in range(i, j):
        for rule in grammar.rules:
            if len(rule.rhs) == 2 and rule.rhs[0] in T[i][k] and rule.rhs[1] in T[k + 1][j]:
                if rule.lhs == symbol:
                    return ParseTree(symbol,
                                     [build_parse_tree(words, grammar, T, i, k, rule.rhs[0]),
                                      build_parse_tree(words, grammar, T, k + 1, j, rule.rhs[1])])

    # if we reach this point, the symbol is a terminal symbol
    return ParseTree(symbol, [words[i]])


def parse(words: list, grammar: Grammar) -> list:
    """parses the list of words with grammar and returns the (possibly empty) list
    of possible parses. The ordering of possible parses is arbitrary.
    returns a list of ParseTree
    """

    # the length of the list of words
    n = len(words)

    # create the table T with a size of n x n
    # where each field T[i][j] can contain a set of symbols
    T = [[set([]) for _ in range(n)] for _ in range(n)]


    # fill the table T:
    # go from outer diagonal to inner diagonal, for example, search in the following order:
    # iteration 0: T[0][0], T[1][1], T[2][2], T[3][3], T[4][4]
    # iteration 1: T[1][0], T[2][1], T[3][2], T[4][3]
    # iteration 2: T[2][0], T[3][1], T[4][2]
    # iteration 3: T[3][0], T[4][1]
    # iteration 4: T[4][0]

    # the first iteration l (iteration 0) is special (and done beforehand);
    # here we fill the diagonal of the table T
    # with the terminal symbols that can create the words
    # l = 0
    for w in range(n):
        for rule in grammar.rules:
            if len(rule.rhs) == 1 and rule.rhs[0] == words[w]:
                T[w][w].add(rule.lhs)

    # now we start from the second iteration on
    # we fill the table T with the non-terminal symbols that can create the words
    #  1 <= l < n
    for l in range(1, n):
        # loop with r as row index and c as column index
        # iterate from r = l to r = n - 1
        # the corresponding column indexes are respectively c - l
        for r in range(l, n):
            c = r - l

            # search for the rules that can create the matching symbols of the current field
            for k in range(c, r):
                for rule in grammar.rules:
                    if len(rule.rhs) == 2 and rule.rhs[0] in T[k][c] and rule.rhs[1] in T[r][k + 1]:
                        T[c][r].add(rule.lhs)



    # the goal is, that in the end, the start symbol is in the bottom left corner of the table T
    # (corresponds to T[n - 1][0])


    return T

    # check if the start symbol is in the top right field of the table
#     if grammar.start_symbol in T[0][n - 1]:
# if yes, build all possible parse trees
#         parse_trees = []
#         for rule in grammar.rules:
#             if len(rule.rhs) == 2 and rule.rhs[0] in T[0][n - 2] and rule.rhs[1] in T[n - 1][n - 1]:
#                 parse_trees.append(build_parse_tree(words, grammar, T, 0, n - 1, rule.lhs))
#         return parse_trees
#     else:
# if not, return an empty list
#         return []




def example_telescope_parse():
    return \
        ParseTree(Symbol("$S"),
                  [ParseNode(Symbol("$NP"),
                             [ParseNode(Symbol("I"))]),
                   ParseNode(Symbol("$VP"),
                             [ParseNode(Symbol("$VP"),
                                        [ParseNode(Symbol("$V"),
                                                   [ParseNode(Symbol("saw"))]),
                                         ParseNode(Symbol("$NP"),
                                                   [ParseNode(Symbol("$Det"),
                                                              [ParseNode(Symbol("the"))]),
                                                    ParseNode(Symbol("$N"),
                                                              [ParseNode(Symbol("duck"))])])]),
                              ParseNode(Symbol("$PP"),
                                        [ParseNode(Symbol("$P"),
                                                   [ParseNode(Symbol("with"))]),
                                         ParseNode(Symbol("$NP"),
                                                   [ParseNode(Symbol("$Det"),
                                                              [ParseNode(Symbol("a"))]),
                                                    ParseNode(Symbol("$N"),
                                                              [ParseNode(Symbol("telescope"))])])])])])

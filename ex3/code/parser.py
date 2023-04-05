from grammar import *
from parse import *


def is_in_language(words: list, grammar: Grammar) -> bool:
    """returns True if the list of words is in the language of grammar"""""

    # if at least one parse exists, the list of words is in the language
    return len(parse(words, grammar)) > 0
    



def parse(words: list, grammar: Grammar) -> list:
    """parses the list of words with grammar and returns the (possibly empty) list of possible parses. The ordering of possible parses is arbitrary.
    returns a list of ParseTree
    """

    # the length of the list of words
    n = len(words)

    # create the table T with a size of n x n
    # where each field T[i][j] can contain a set of symbols
    T = [[set([]) for _ in range(n)] for _ in range(n)]

    # we are building the parsing trees at the same time
    # they are built from bottom to top,
    # the same way the algorithm flows

    # build the table F with a size of n x n which will contain the parse nodes
    F = [[[] for _ in range(n)] for _ in range(n)]


    # fill the table T:
    # go from outer diagonal to inner diagonal, for example, search in the following order:
    # iteration 0: T[0][0], T[1][1], T[2][2], T[3][3], T[4][4]
    # iteration 1: T[1][0], T[2][1], T[3][2], T[4][3]
    # iteration 2: T[2][0], T[3][1], T[4][2]
    # iteration 3: T[3][0], T[4][1]
    # iteration 4: T[4][0]

    # note that the indexing here assumes a left triangular matrix

    # the first iteration l (iteration 0) is special (and done beforehand);
    # here we fill the diagonal of the table T
    # with the terminal symbols that can create the words
    # l = 0
    for w in range(n):
        for rule in grammar.rules:
            if len(rule.rhs) == 1 and rule.rhs[0].symbol == words[w]:
                T[w][w].add(rule.lhs)
                # build the parse tree terminal nodes
                F[w][w].append(ParseNode(rule.lhs, [ParseNode(rule.rhs[0])]))


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
            # and add the left hand side of the rule to the current field
            for k in range(c, r):  # c <= k < r
                for rule in grammar.rules:
                    # compare the rules that contain two non-terminals on the rhs
                    # with the symbols in the current field
                    if len(rule.rhs) == 2 and rule.rhs[0] in T[k][c] and rule.rhs[1] in T[r][k + 1]:
                        T[r][c].add(rule.lhs)

                        # build for each possible left node and right node
                        # a new parse node with the left hand side of the rule
                        for left_node in F[k][c]:
                            for right_node in F[r][k + 1]:
                                F[r][c].append(ParseTree(rule.lhs, [left_node, right_node]))


    # the goal is, that in the end, the start symbol is in the bottom left corner of the table T
    # (corresponds to T[n - 1][0])
    # so if the start symbol is in the bottom left corner of the table T, we can collect all possible parse trees
    # from this field F[n - 1][0] and return the ones with having the start symbol as the root node symbol
    if grammar.start_symbol in T[n - 1][0]:
        return [node for node in F[n - 1][0] if node.symbol == grammar.start_symbol]
    else:
        # otherwise we return an empty list
        return []



def example_telescope_parse():
    return ParseTree(Symbol("$S"),
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

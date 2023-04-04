from grammar import *
from parse import *


def is_in_language(words: list, grammar: Grammar) -> bool:
    """returns True if the list of words is in the language of grammar"""""

    # if at least one parse exists, the list of words is in the language
    return len(parse(words, grammar)) > 0
    


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

    # note that the indexing here assumes a left triangular matrix

    # the first iteration l (iteration 0) is special (and done beforehand);
    # here we fill the diagonal of the table T
    # with the terminal symbols that can create the words
    # l = 0
    for w in range(n):
        for rule in grammar.rules:
            if len(rule.rhs) == 1 and rule.rhs[0].symbol == words[w]:
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
            # and add the left hand side of the rule to the current field
            for k in range(c, r):  # c <= k < r
                for rule in grammar.rules:
                    # compare the rules that contain two non-terminals on the rhs
                    # with the symbols in the current field
                    if len(rule.rhs) == 2 and rule.rhs[0] in T[k][c] and rule.rhs[1] in T[r][k + 1]:
                        T[r][c].add(rule.lhs)



    # the goal is, that in the end, the start symbol is in the bottom left corner of the table T
    # (corresponds to T[n - 1][0])
    # so if the start symbol is in the bottom left corner of the table T, we can build all possible parse trees
    # and return them
    if grammar.start_symbol in T[n - 1][0]:
        # we start with the start symbol in the bottom left corner of the table T
        # and build the parse trees recursively
        def build_parse_trees(symbol: Symbol, row: int, column: int) -> list:
            """builds the parse trees recursively and returns them as a list"""

            # we create a list of parse trees
            parse_trees = []

            # we loop through all rules that contain the current symbol on the left hand side
            for rule in grammar.rules:
                if rule.lhs == symbol:

                    # if the rule contains one terminal symbol on the right hand side
                    # we create a parse tree with the terminal symbol as a leaf
                    if len(rule.rhs) == 1 and rule.rhs[0].symbol in words:
                        parse_trees.append(
                            ParseTree(rule.lhs,
                                      [ParseNode(rule.rhs[0])]))

                    # if the rule contains two non-terminal symbols on the right hand side
                    # we create a parse tree with the non-terminal symbols as nodes
                    # and we build the parse trees recursively for the non-terminal symbols
                    elif len(rule.rhs) == 2:
                        # we loop through all possible rows and columns for the first non-terminal symbol
                        for k in range(column, row):
                            # we get the parse trees for the first non-terminal symbol
                            parse_trees_1 = build_parse_trees(rule.rhs[0], k, column)

                            # we loop through all possible rows and columns for the second non-terminal symbol
                            for l in range(k + 1, row + 1):
                                # we get the parse trees for the second non-terminal symbol
                                parse_trees_2 = build_parse_trees(rule.rhs[1], row, l)

                                # we create a parse tree with the current rule and the parse trees for the non-terminal symbols
                                parse_trees.append(
                                    ParseTree(rule.lhs,
                                              [ParseNode(rule.rhs[0], parse_trees_1),
                                               ParseNode(rule.rhs[1], parse_trees_2)]))

            # return the list of parse trees
            return parse_trees

        return build_parse_trees(grammar.start_symbol, n - 1, 0)
    else:
        # otherwise we return an empty list
        return []



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

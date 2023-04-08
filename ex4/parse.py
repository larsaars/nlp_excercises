from grammar import Symbol
from operator import itemgetter

_node_id = 0  # counter to ensure that _next_node_id() will create unique IDs


def _next_node_id():
    global _node_id
    _node_id += 1
    return _node_id


class ParseNode:
    """a parse node consists of the constituent symbol (for non-terminals) or the terminal symbol"""
    id: int
    symbol: Symbol
    productions: list  # of ParseNode or empty (for terminal symbols)

    def __init__(self, symbol: Symbol, productions: list = []):
        self.id = _next_node_id()
        self.symbol = symbol
        assert symbol.terminal == (len(productions) == 0), "a terminal can't produce anything {} !".format(symbol)
        self.productions = productions

    def _to_dot_productions(self):
        output = ""
        for p in self.productions:
            output += str(self.id) + " [label=\"" + self.symbol.symbol + "\"];\n"
            output += str(self.id) + " -> " + str(p.id) + ";\n"
            output += p._to_dot_productions()
        return output

    def collect_terminals(self):
        if self.symbol.terminal:
            return [(self.id, self.symbol)]
        else:
            return sum([p.collect_terminals() for p in self.productions], start=[])

    def __repr__(self):
        return "[" + repr(self.symbol) + " " + " ".join(map(repr, self.productions)) + "]" if self.productions else repr(self.symbol)

    # replace the extra created symbols with the original symbols
    # this is necessary after in case the grammar has been normalized to CNF
    def replace_extra_symbols(self, node, prod_collection: list):
        for prod in node.productions:
            # if is collecting the non-extra children symbols
            # and the current symbol is extra, pass the given list and
            # append all non-extra children symbols to the list
            if prod_collection is not None:
                if prod.symbol.is_extra:
                    self.replace_extra_symbols(prod, prod_collection)  # collect children 
                else:
                    prod_collection.append(prod)  # add to list of parent node
            else:
                # if is not collecting, but child is extra,
                # start collecting (without losing the current node's productions)
                # and set the current's node productions equal to the collected list
                if prod.symbol.is_extra:
                    prod_collection = [p for p in node.productions if not p.symbol.is_extra]
                    self.replace_extra_symbols(prod, prod_collection)
                    node.productions = prod_collection
                else:
                    # in all other cases just keep on going
                    # without collecting
                    self.replace_extra_symbols(prod, None)


class ParseTree(ParseNode):
    """a parse tree is just a regular node that also knows how to draw itself"""

    def to_dot(self):
        # make sure extra symbols are replaced with the original symbols
        # when drawing the tree
        self.replace_extra_symbols(self, None)

        output = "digraph parsetree {\n"
        output += self._to_dot_terminals_subgraph()
        output += "rankdir=\"TB\";\n" + \
                  str(self.id) +";\n" \
                  "node [shape=\"none\"]\n" \
                  "edge [style=\"solid\"];\n"
        output += self._to_dot_productions()
        output += "}"
        return output

    def _to_dot_terminals_subgraph(self):
        terminals = self.collect_terminals()
        output = "{\n" \
                 "rankdir=\"LR\";\n" \
                 "node [shape=\"box\"];\n" \
                 "edge [style=\"invis\"];\n" \
                 "rank=\"same\";\n"
        for id,s in terminals:
            output += str(id) + " [label=\"" + str(s.symbol) + "\"];\n"
        output += " -> ".join(map(str, map(itemgetter(0), terminals)))
        output += ";\n}\n"
        return output

import re
from collections import defaultdict
from typing import List, Tuple, Mapping


class Symbol:
    """symbols of the grammar"""

    terminal: bool
    symbol: str

    is_symbol: bool = False  # whether this symbol is an extra symbol created by normalization

    def __init__(self, symbol: str, is_extra=False):
        self.terminal = not symbol.startswith("$")
        self.symbol = symbol if self.terminal else symbol[1:]
        self.is_extra = is_extra

    def __repr__(self):
        return ("" if self.terminal else "$") + self.symbol

    def __eq__(self, other):
        return self.symbol == other.symbol and self.terminal == other.terminal

    def __hash__(self):
        return hash(self.symbol)


class GrammarRule:
    """
    simple sequence rule.
    We don't support anything more complex;
    alternatives will have to be split into multiple sub-rules """

    lhs: Symbol
    rhs: List[Symbol]  # it's a list of Symbols

    def __init__(self, lhs: Symbol, rhs: list):
        self.lhs, self.rhs = lhs, rhs

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __repr__(self):
        return str(self.lhs) + " = " + " ".join([str(s) for s in self.rhs]) + ";"


class Grammar:
    language: str
    start_symbol: Symbol
    rules: List[GrammarRule] = []  # list of GrammarRules
    symbols: Mapping[str, Symbol] = {}  # map from strings to symbols
    rule_map: Mapping[tuple, GrammarRule] # map from RHSs to the matching rules
    extra_norm_id: int = 0  # used to generate new symbols (counter)

    """initialize a new grammar from a srgs grammar file"""
    def __init__(self, lines, grammar_format="SRGS"):  # FIXME: maybe implement JSGF import in the future
        assert grammar_format == "SRGS", "illegal format descriptor: {}".format(grammar_format)
        lines = [re.sub("//.*$", "", line) for line in lines]  # remove comment lines
        lines = [line.strip() for line in lines if not re.match(r"^ *$", line)]  # remove empty lines
        assert lines.pop(0).lower() == "#abnf v1.0 utf-8;", "maybe something is wrong with header?"
        lang = re.match(r"language\s+(\S*)\s*;", lines.pop(0).lower())
        assert lang and len(lang.groups()) == 1, "cannot find correct language tag: {}".format(lang)
        self.language = lang.group(0)
        for line in lines:
            match = re.match(r"((?:public)?)\s*(\$\S+)\s*=\s*(.*)\s*;", line)
            assert match and len(match.groups()) == 3, "cannot parse line {}".format(line)
            is_public = match.group(1) != ""
            lhs = self.get_symbol(match.group(2))
            rhs = [self.get_symbol(s) for s in re.split(r"\s+", match.group(3))]
            rule = GrammarRule(lhs, rhs)
            self.rules.append(rule)
            if is_public:
                self.start_symbol = lhs
        self.build_rule_map()

    def build_rule_map(self):
        self.rule_map = defaultdict(lambda: [])
        for r in self.rules:
            self.rule_map[tuple(r.rhs)].append(r)


    def get_symbol(self, symbol: str, is_extra=False):
        if symbol not in self.symbols:
            self.symbols[symbol] = Symbol(symbol, is_extra=is_extra)

        return self.symbols[symbol]

    def __repr__(self):
        return "#ABNF V1.0 utf-8\n" + \
               "language " + self.language + "\n" + \
               "\n".join([str(r) if r.lhs != self.start_symbol else "public " + str(r) for r in self.rules])

    def to_CNF(self):
        """transforms grammar to "relaxed" CNF"""

        # the idea is to split rules with more than 2 symbols on the right hand side
        # into multiple rules with excactly two symbols on the right hand side
        for rule in self.rules:

            # rules that have a length of 1 or 2 are already in CNF
            if len(rule.rhs) > 2:
                # the lhs for the new rules will be the second rhs of the old rule
                # for the first rule, we use the original lhs
                new_lhs = rule.lhs

                # loop trough all symbols on the right hand side
                # except the last one (since we don't need to create a new rule for that one)
                for i in range(len(rule.rhs) - 1):
                    # if is the last symbol, we don't need to create a new symbol
                    # and just use the rightest rhs symbol of the old rule
                    if i == len(rule.rhs) - 2:
                        new_rhs = rule.rhs[-1]
                    else:
                        # else we create a new symbol
                        # define which symbol is the parent of all newly created symbols in this rule iteration
                        self.extra_norm_id += 1
                        new_rhs = self.get_symbol(f'$E{self.extra_norm_id}', is_extra=True)

                    # and append the new rule with the new lhs;
                    # for the rhs we use the current rhs symbol of the old rule and the newly created symbol
                    # that will be the lhs of the next rule
                    # (or in the case of the last rule, the rightest rhs symbol of the old rule as already described above)
                    self.rules.append(
                        GrammarRule(new_lhs, [rule.rhs[i], new_rhs])
                    )

                    new_lhs = new_rhs  # newly created rhs will be next lhs


        # rebuild rule map
        self.build_rule_map()



    def is_CNF(self):
        """check if the grammar is in Chomsky Normal Form"""

        # if the start symbol is a terminal, it's not CNF
        if self.start_symbol.terminal:
            return False

        for rule in self.rules:
            # if any rule has more than 2 or 0 symbols on the right hand side, it's not CNF 
            if len(rule.rhs) == 0 or len(rule.rhs) > 2:
                return False

            # is in CNF, if
            # each rules produces (exactly) two non-terminals
            # OR exactly one terminal symbol
            if len(rule.rhs) == 2 and (rule.rhs[0].terminal or rule.rhs[1].terminal): 
                return False

            if len(rule.rhs) == 1 and not rule.rhs[0].terminal:
                return False

        return True

    def is_relaxed_CNF(self):
        """check if the grammar is in a relaxed Chomsky Normal Form,
        where we allow rules with one non-terminal on the right hand side"""

        # if the start symbol is a terminal, it's not CNF
        if self.start_symbol.terminal:
            return False

        for rule in self.rules:
            # if any rule has more than 2 or 0 symbols on the right hand side, it's not CNF 
            if len(rule.rhs) == 0 or len(rule.rhs) > 2:
                return False

            # is in "relaxed" CNF, if
            # each rules produces one or two non-terminals
            # OR exactly one terminal symbol
            if len(rule.rhs) == 2 and not (rule.rhs[0].terminal and rule.rhs[1].terminal): 
                return False


        return True

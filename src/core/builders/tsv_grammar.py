from .grammar_builder import GrammarBuilder

class TSVGrammarBuilder(GrammarBuilder):
    def __init__(self, predicates: list):

        def grammar_formatting_fun(class_name: str, terms: list) -> str:
            joined_terms = "\t".join(terms).lower()
            return f"\"{class_name}\t\"{joined_terms}\n"

        def to_predicate_syntax(line: str) -> str:
            tokens = line.split(",")
            return f"{tokens[0]}({','.join(tokens[1:])}).".lower()


        super().__init__(predicates, grammar_formatting_fun, to_predicate_syntax)

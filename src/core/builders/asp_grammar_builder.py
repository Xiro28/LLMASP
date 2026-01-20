from .grammar_builder import GrammarBuilder

class ASPGrammarBuilder(GrammarBuilder):
    def __init__(self, predicates: list):

        def grammar_formatting_fun(class_name: str, terms: list) -> str:
            joined_terms = ('","'.join(terms).lower()).replace(")", "")
            return f"\"{class_name}(\"{joined_terms}\")."

        # ASP grammar does not need any conversion to predicate syntax since it is already in that format
        def to_predicate_syntax(line: str) -> str:
            return line

        super().__init__(predicates, grammar_formatting_fun, to_predicate_syntax)

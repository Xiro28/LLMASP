class GrammarBuilder:

    def __init__(self, predicates: list, grammar_formatting_fun: callable, to_predicate_syntax: callable):

        self.__grammars = {}
        self.__to_predicate_syntax = to_predicate_syntax

        for predicate in predicates:
            for key in predicate.keys():
                
                data = key.split("(")
                class_name = data[0].replace("_", " ")
                terms = []

                data[1] = data[1].replace("\"", "")

                if ',' in data[1]:
                    terms = data[1].split(",")
                    terms[-1] = terms[-1].replace(")", "").replace(".", "")
                else:
                    terms.append(data[1].replace(")", "").replace(".", ""))
    
                current_grammar = (
                    f"root ::= (output | \"empty_predicate\")\n"
                    f"output ::= {class_name} newline ({class_name} newline?)*\n"
                    f"newline ::= \"\\n\"\n"
                    f"{class_name} ::= \"{grammar_formatting_fun(class_name, terms)}\"\n"
                    f"__numbers__ ::= \"0\" | \"-\"?[1-9][0-9]*\n"
                    f"__strings__ ::= [a-zA-Z_][a-zA-Z_0-9]*\n"
                )

                G_COMBINED = "(__numbers__ | __strings__)"

                for term in terms:
                    term_name = term.strip().replace(")", "")
                    name = term_name.strip().replace("_", "").lower()
                    current_grammar += f"{name} ::= {G_COMBINED}\n"

                self.__grammars[class_name] = current_grammar


    def get_grammars(self) -> dict:
        return (self.__grammars, self.__to_predicate_syntax)
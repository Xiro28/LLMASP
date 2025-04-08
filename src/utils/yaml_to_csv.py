class GrammarsBuilder:

    def __init__(self, predicates: list):

        """
            Build csv grammars from the predicates dictionary.

            Parameters:
                predicates (list): List of dictionaries containing the predicates.

            Returns:
                Dictionary with the grammar generated from the predicates.

            Input example:
                predicates: [{"somepredicates(arg1, arg2).": "extract the arguments from the predicate."}, {"somepredicates2(arg3, arg4).": "..."}]

            Output example:
                {"somepredicates" : "root ::= somepredicates arg1 \"\t\"arg2 \"\narg1 ::= [1-9][0-9]{0,15}\narg2::=[a-z]*\n"}

            TODO: At the end of the dictionary, there's a grammar that is used to generate all the predicates in once (to be used with the single call LLM).
        """


        self.__grammars = {}

        for predicate in predicates:
            for key in predicate.keys():
                if key == "_":
                    continue

                data = key.split("(")
                class_name = data[0]
                terms = []

                data[1] = data[1].replace("\"", "")

                if ',' in data[1]:
                    terms = data[1].split(",")
                    terms[-1] = terms[-1].replace(").", "")
                else:
                    terms.append(data[1].replace(").", ""))

                #remove :int and :str from the terms if any
                terms_no_type = []
                for term in terms:
                    if ":" in term:
                        term = term.split(":")[0]
                    terms_no_type.append(term.strip().replace("_", ""))
                
                
                joined_terms = '"\t"'.join(terms_no_type)
                joined_terms_no_tab = " ".join(terms_no_type)

                # Build the main grammar rule; note the use of escaped newline and tab.
                current_grammar = (
                    f"root ::= lines*\n"
                    f"lines ::= \"{class_name}\t\"{joined_terms} (\"\\n\")?\n"
                )

                # This is needed to be instruct the LLM to generate the predicates how we want
                output_example = f"{class_name} {joined_terms_no_tab}\n"

                ENABLE_TYPES = True

                # String and numbers
                G_STRING = "[a-z0-9]+"
                G_INT = "[0-9]{1,15}"
                G_COMBINED = f"({G_STRING}|{G_INT})"

                for term in terms:
                    term_name = term.strip().replace(")", "")

                    if ENABLE_TYPES and ":" in term_name:
                        name, term_type = term_name.split(":")
                    
                        name = name.strip().replace("_", "")
                        term_type = term_type.strip()
                        if term_type == "int":
                            current_grammar += f"{name} ::= {G_INT}\n"
                        else:
                            current_grammar += f"{name} ::= {G_STRING}\n"
                    else:
                        current_grammar += f"{name} ::= {G_COMBINED}\n"

                    
                def str_method(str):
                    tokens = str.split("\t")
                    return f"{tokens[0]}({",".join(tokens[1:])})."

                self.__grammars[class_name] = [current_grammar, output_example, str_method]

    def get_grammars(self):
        return self.__grammars

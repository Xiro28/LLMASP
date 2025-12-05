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
                
                
                joined_terms = '"\t"'.join(terms_no_type).lower()
                joined_terms_no_tab = " ".join(terms_no_type)

                structure_str = class_name + " " + " ".join(terms_no_type)

                class_name_no_tab = class_name.replace("_", " ")
                #Make the first letter of each word uppercase
                class_name_no_tab = "".join([word.capitalize() for word in class_name_no_tab.split()])

                if type(predicate[key]) is list:
                    # in value we have a list that contains prompt and optionally if and kb, They are stored in a dict
                    for v in predicate[key]:
                        if "prompt" in v:
                            description = v["prompt"].strip().replace("\n", " ").replace("\t", " ")
                else:
                    description = predicate[key].strip().replace("\n", " ").replace("\t", " ")


                # Build the main grammar rule; note the use of escaped newline and tab.
                current_grammar = (
                    f"root ::= (output | \"empty_predicate\")\n"
                    f"output ::= {class_name_no_tab} newline ({class_name_no_tab} newline?)*\n"
                    f"newline ::= \"\\n\"\n"
                    f"{class_name_no_tab} ::= \"{class_name}\t\"{joined_terms}\n"
                )

                # This is needed to be instruct the LLM to generate the predicates how we want
                # output_example = f"{class_name} {joined_terms_no_tab}\n"

                ENABLE_TYPES = True

                # String and numbers
                G_STRING = "[a-z_]"
                G_INT = "[0-9]"
                G_COMBINED = f"({G_INT} | {G_STRING})"

                for term in terms:
                    term_name = term.strip().replace(")", "")
                    
                    name, term_type = term_name.split(":")
                    name = name.strip().replace("_", "")

                    if ENABLE_TYPES and ":" in term_name:

                        term_type = term_type.strip()
                        if term_type == "int":
                            current_grammar += f"{name} ::= {G_INT}+\n"
                        elif "$" in term_type:
                            # Custom type
                            custom_grammar = f"{name} ::= "
                            for el in term_type.split("$"):
                                el = el.strip()

                                print(el)

                                if el == "?int":
                                    custom_grammar += f"{G_INT}*"
                                elif el == "int" or el == "int+":
                                    custom_grammar += f"{G_INT}+"

                                elif el == "str" or el == "str+":
                                    custom_grammar += f"{G_STRING}+"
                                elif el == "?str":
                                    custom_grammar += f"{G_STRING}*"

                                else:
                                    custom_grammar += f"\"{el}\""
                            
                            print(f"Custom grammar for {name}: {custom_grammar}")
                                
                            current_grammar += custom_grammar + "\n"

                        else:
                            current_grammar += f"{name} ::= {G_COMBINED}+\n"
                    else:
                        current_grammar += f"{name} ::= {G_COMBINED}+\n"


                self.__grammars[class_name] = [current_grammar, (class_name, joined_terms_no_tab)]

    def get_grammars(self):
        return self.__grammars
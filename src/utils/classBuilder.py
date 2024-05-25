from pydantic import BaseModel

class ClassBuilder:
    def __init__(self):
        self.__classes = {}

    def build_classes(self, predicates: list):

        """
            Build classes from the predicates dictionary.

            Parameters:
                predicates (list): List of dictionaries containing the predicates.

            Returns:
                ClassBuilder: The ClassBuilder instance with the classes generated from the predicates dictionary.

            Input example:
                predicates: [{"somepredicates(arg1, arg2).": "extract the arguments from the predicate."}, {"somepredicates2(arg3, arg4).": "..."}]
        """

        code = ""

        for predicate in predicates:
            for key in predicate.keys():

                if key == "_":
                    continue

                data = key.split("(")
                predicate = data[0]
                terms = []

                data[1] = data[1].replace("\"", "")

                if ',' in data[1]:
                    terms = data[1].split(",")
                    terms[-1] = terms[-1].replace(").", "")
                else:
                    terms.append(data[1].replace(").", ""))
                
                code += f"class {predicate}(BaseModel):\n"

                # Adding terms to the class definition
                for term in terms:
                    code += f"\t{term.strip()}: str\n"
        
        # unsafe but it's limited to just generate classes so heavily constrained 
        # and the user input cannot control the code that is being executed
        
        # Let's clear the __classes dictionary to not have any security issues nor memory leaks
        for key in self.__classes.keys():
            del self.__classes[key]

        self.__classes.clear()
        exec(code, globals(), self.__classes)

        print(code)

        return self
    
    def get_classes(self):
        return self.__classes


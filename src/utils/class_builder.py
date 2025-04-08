from pydantic import BaseModel, Field

from typing import Optional

class ClassBuilder:

    def __init__(self, predicates: list):

        """
            Build classes from the predicates dictionary.

            Parameters:
                predicates (list): List of dictionaries containing the predicates.

            Returns:
                ClassBuilder: The ClassBuilder instance with the classes generated from the predicates dictionary.

            Input example:
                predicates: [{"somepredicates(arg1, arg2).": "extract the arguments from the predicate."}, {"somepredicates2(arg3, arg4).": "..."}]

            Output example:
                class_1:
                    arg1: str | int | None
                    arg2: str | int | None

                list_class_1:
                    list_class_1: list[class_1]
            
                etc...

            NB: The list_ prefix is added to the class name to generate a list of instances of the same class. Useful for single inference with LLM.
            Since then the LLM will be called with this wrapper class:

                atom_class:
                    _list_class_1: list[list_class_1]
                    _list_class_2: list[list_class_2] 
        """


        self.__classes = {}

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

                class_dict = {}
                annotations = {}

                ENABLE_TYPES = True

                for term in terms:
                    term_name = term.strip().replace(")", "")

                    if ":" in term_name:
                        name, term_type = term_name.split(":")
                        
                        name = name.strip()
                        term_type = term_type.strip()

                        class_dict[name] = Field()

                        if ENABLE_TYPES:
                            if term_type == "int":
                                annotations[name] = int
                            else:
                                annotations[name] = str
                        else:
                            annotations[name] =  str | int
                    else:
                        class_dict[term_name] = Field()
                        annotations[term_name] = int | str

                class_dict['__annotations__'] = annotations
                class_dict['__name__'] = class_name

                def str_method(self):
                    atom = f"{self.__name__}("
                    for _, value in self.dict().items():
                        if value is None:
                            return ""  
                        
                        # spaces are not allowed inside the parameter of an atom
                        if isinstance(value, str) and " " in value:
                            return ""

                        atom += f"{value}, "
                    return f"{atom[:-2]}).".lower()

                class_dict['__str__'] = str_method

                # Create the new class dynamically
                new_class = type(class_name, (BaseModel,), class_dict)
                self.__classes[class_name] = new_class

                wrapper_name = f"list_{class_name}"

                wrapper = type(
                    wrapper_name,
                    (BaseModel,),
                    {
                        "__name__": f"{class_name}_list",
                        "__annotations__": {f"list_{class_name}": list[new_class | None]},
                        "__description__": predicate[key],
                        "__class_params__": terms
                    },
                )

                self.__classes[wrapper_name] = wrapper

    def get_classes(self):
        return self.__classes

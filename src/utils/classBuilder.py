from pydantic import BaseModel, Field, SkipValidation
from typing import Optional, List, ForwardRef

class ClassBuilder:

    def __init__(self, predicates: list, custom_instructor: bool = False):

        """
            Build classes from the predicates dictionary.

            Parameters:
                predicates (list): List of dictionaries containing the predicates.

            Returns:
                ClassBuilder: The ClassBuilder instance with the classes generated from the predicates dictionary.

            Input example:
                predicates: [{"somepredicates(arg1, arg2).": "extract the arguments from the predicate."}, {"somepredicates2(arg3, arg4).": "..."}]
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

                for term in terms:
                    term_name = term.strip()
                    if term_name in {"__annotations__", "__name__", "__str__"}:
                        term_name = f"field_{term_name}"

                    class_dict[term_name] = Field()
                    annotations[term_name] = str | None

                class_dict['__annotations__'] = annotations
                class_dict['__name__'] = class_name

                def str_method(self):
                    # Ensure items are processed properly
                    atom = f"{self.__name__}("
                    for key, value in self.dict().items():
                        if value is None:
                            return ""  # Invalid atom
                        atom += f"{value.replace(' ', '_')}, "
                    return f"{atom[:-2]}).".lower()

                class_dict['__str__'] = str_method

                # Create the new class dynamically
                new_class = type(class_name, (BaseModel,), class_dict)
                self.__classes[class_name] = new_class

                # Ollama needs a list to generate multiple instances of the same class
                wrapper_name = f"list_{class_name}"

                wrapper = type(
                    wrapper_name,
                    (BaseModel,),
                    {
                        "__name__": f"{class_name}_list",
                        f"list_{class_name}" : Field(description=predicate[key]),
                        "__annotations__": {f"list_{class_name}": list[new_class]},  # Use ForwardRef for dynamic evaluation
                    },
                )

                self.__classes[wrapper_name] = wrapper

                print(wrapper)
        
        for classes in self.__classes.values():
            for key, value in classes.__annotations__.items():
                print(f"{key}: {value}")

    def get_classes(self):
        return self.__classes

from pydantic import BaseModel

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
                    class_dict[term.strip()] = ''
                    annotations[term.strip()] = list[str] # Fix this to str. TODO: Put the correct type.

                class_dict['__annotations__'] = annotations
                class_dict['__name__'] = class_name

                def str_method(self):
                    # self.dict().items() -> [("arg1", ["t1", "t2"]), ("arg2", ["t1", "t2"])]
                    
                    data = self.dict()
                    len_args = len(next(iter(data.values())))  
                    ret_buff = [f"{self.__class__.__name__}(" for _ in range(len_args)]

                    for key, variables in data.items():
                        for i, var in enumerate(variables):
                            ret_buff[i] += f"{var.replace(' ', '_')}, "

                    # Remove the trailing comma and space from each buffer entry and close the parentheses
                    for i in range(len(ret_buff)):
                        ret_buff[i] = ret_buff[i][:-2] + "). "

                    # BE sure to return the string in lowercase
                    return "".join(ret_buff).lower()



                class_dict['__str__'] = str_method

                new_class = type(class_name, (BaseModel, ), class_dict)
                
                self.__classes[class_name] = new_class

    def get_classes(self):
        return self.__classes

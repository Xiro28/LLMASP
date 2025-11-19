
from dumbo_asp.primitives.models import Model
from fact_manager import FactManager

class Predicate:

    def __init__(self, predicate, value):
        
        self._predicate = predicate.replace(":str", "").replace(":int", "")

        if isinstance(value, list):
            self.obj_type = True

            # in value we have a list that contains prompt and optionally if and kb, They are stored in a dict
            value_dict = {}
            for v in value:
                if "prompt" in v:
                    value_dict["prompt"] = v["prompt"]
                elif "kb" in v:
                    value_dict["kb"] = v["kb"]
                elif "if" in v:
                    value_dict["if"] = v["if"]

            self.value = value_dict
        else:
            self.obj_type = False
            self.value = value


    def __str__(self):
        return self._predicate

    @property
    def prompt(self):
        if self.obj_type:
            return self.value["prompt"]
        
        return self.value

    @property
    def predicate(self):
        return self._predicate

    def execute_condition(self, condition: str):

        if "&&" in condition:
            conditions = condition.split("&&")
            for cond in conditions:
                if not self.execute_condition(cond.strip()):
                    return False
            return True
        elif "||" in condition:
            conditions = condition.split("||")
            for cond in conditions:
                if self.execute_condition(cond.strip()):
                    return True
            return False

        parameters = condition.split(" ")

        op = parameters[0]
        if op == "any":
            return parameters[1] in FactManager.get_all_facts()
        elif op == "not":
            return parameters[1] not in FactManager.get_all_facts()
        
        return False
            

    def check_existence_condition(self):
        if self.obj_type:
            condition = self.value.get("if", "")
            if condition != "":
                return self.execute_condition(condition)
        return True

    def run_kb(self):
        if self.obj_type:
            kb = self.value.get("kb", "")
            if kb != "":
                new_facts = Model.of_program(kb, FactManager.get_all_facts(), sort=False).as_facts
                print(f"Adding KB facts for predicate {self._predicate}:\n{new_facts}")
                return new_facts
        return ""
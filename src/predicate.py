
from dumbo_asp.primitives.models import Model
from fact_manager import FactManager

class Predicate:

    def __init__(self, predicate, value):
        
        self.advanced_prompt_type = False
        self.defined_predicate = predicate.replace(":str", "").replace(":int", "")

        self.__prompt = ""
        self.__condition = ""
        self.__kb = ""

        if isinstance(value, list):
            self.advanced_prompt_type = True

            for v in value:
                if "prompt" in v:
                    self.__prompt = v["prompt"]
                elif "kb" in v:
                    self.__kb = v["kb"]
                elif "if" in v:
                    self.__condition = v["if"]
        else:
            self.__prompt = value


    def __str__(self):
        return self.defined_predicate

    @property
    def prompt_description(self):
        return self.__prompt

    @property
    def predicate(self):
        return self.defined_predicate

    @property
    def predicate_head(self):
        return self.defined_predicate.split("(")[0]

    def execute_condition(self, condition: str):

        complex_condition = False

        try:
            uuid8 = f"uid{rand() * 1000}"
            model = Model.of_program(f"""
                {uuid8} :- {condition}.
                #show {uuid8}.
            """, sort=False)
        except Exception as e:
            complex_condition = True


        if complex_condition:
            try:
                model = Model.of_program(condition, FactManager.get_all_facts(), sort=False)
            except Exception as e:    
                raise ValueError(f"Error executing condition: {e}")
                return False
        
        return len(model.as_facts) > 0
            

    def has_to_be_extracted(self):
        if self.advanced_prompt_type and self.__condition != "":
            return self.execute_condition(self.__condition)
        return True

    def run_kb(self, extracted_facts=""):

        result = extracted_facts

        if self.advanced_prompt_type and self.__kb != "":
            try:
                result = Model.of_program(self.__kb, FactManager.get_all_facts() + extracted_facts, sort=False).as_facts
            except Exception as e:
                raise ValueError(f"Error running kb: {e}")

        return result

from dumbo_asp.primitives.models import Model
from random                      import randint

from  src.utils.logger      import Logger
from  src.utils.statistics import Statistics
from .predicate_container   import PredicateContainer

from src.core.predicate.condition_cache       import ConditionCache

class Predicate:

    def __init__(self, predicate, value):
        
        self.advanced_prompt_type = False
        self.defined_predicate = predicate.replace(":str", "").replace(":int", "")

        self.__prompt = ""
        self.__condition_info = {"condition": "", "monotone": False}
        self.__kb = ""

        if isinstance(value, list):
            self.advanced_prompt_type = True

            for v in value:
                if "prompt" in v:
                    self.__prompt = v["prompt"]
                elif "knowledge_base" in v:
                    self.__kb = v["knowledge_base"]
                elif "extraction_condition" in v:
                    if isinstance(v["extraction_condition"], dict):
                        self.__condition_info["condition"] = v["extraction_condition"].get("condition", "")
                        self.__condition_info["monotone"] = v["extraction_condition"].get("monotone", False)
                    else:
                        self.__condition_info["condition"] = v["extraction_condition"]
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
    
    def generate_uuid8(self) -> str:
        return f"uuid{randint(1000, 9999)}"
    
    def generate_min_program(self, condition) -> str:

        uuid8 = self.generate_uuid8()
        
        # instead of checking one condition at a tim, we build a single program with all conditions
        # all the condition must be checked singly, so we use a unique uuid for each of them
        # the uuid has an idx at the end in order to get which condition passed
        if isinstance(condition, list):
            program_parts = []
            for idx, cond in enumerate(condition):
                program_parts.append(f"""
                    {uuid8}_{idx} :- {cond}.
                    #show {uuid8}_{idx}/0.
                """)
            return "\n".join(program_parts)
        
        return f"""
            {uuid8} :- {condition}.
            #show {uuid8}/0.
        """
    
    def evaluate_program(self, condition: str | list[str], monotone: bool = False, result: str = "") -> bool:
        has_model = False
        if isinstance(condition, list):
            for idx, cond in enumerate(condition):
                has_model = f"{idx}" in result
                Logger.debug(f"Condition '{cond}' evaluated to {has_model} with result '{result}'")
                ConditionCache.update(cond, has_model, monotone)
        else:
            has_model = len(result) > 0
            Logger.debug(f"Condition '{condition}' evaluated to {has_model} with result '{result}'")
            ConditionCache.update(condition, has_model, monotone)

        return has_model

    def execute_condition(self, condition: str | list[str], monotone: bool = False) -> bool:
        has_model = False
        self.complex_condition = False

        Statistics.log_solver_call()

        try:
            min_program = self.generate_min_program(condition)
            model = Model.of_program(min_program, PredicateContainer.get_all_predicates(), sort=False)
            has_model = self.evaluate_program(condition, monotone, model.as_facts)
        except Exception as e:
            #not a minimal condition, we can use the complex evaluation
            Logger.debug(f"Condition is complex, executing complex evaluation. Error: {e}, condition: {condition}, predicate: {self.predicate}, monotone: {monotone}")
            self.complex_condition = True

        if self.complex_condition and isinstance(condition, str):
            try:
                model = Model.of_program(condition, PredicateContainer.get_all_predicates(), sort=False)
                has_model = self.evaluate_program(condition, monotone, model.as_facts)
            except Exception as e:    
                Logger.error(f"Error executing complex condition:\n{condition}\n\n{e}.")
        
        return has_model
            

    def has_to_be_extracted(self):
        if not self.advanced_prompt_type:
            return True
        
        condition = self.__condition_info.get("condition", "")
        monotone = self.__condition_info.get("monotone", False)

        if isinstance(condition, str) and ConditionCache.canSkipSolver([condition], monotone):
            Logger.debug(f"Skipping extraction of predicate {self.predicate} with conditions {condition} due to condition cache. Monotone: {monotone}")
            return ConditionCache.get(condition, monotone)
        elif isinstance(condition, list) and ConditionCache.canSkipSolver(condition, monotone):
            Logger.debug(f"Skipping extraction of predicate {self.predicate} with conditions {condition} due to condition cache. Monotone: {monotone}")
            return ConditionCache.get(condition, monotone)

        Logger.debug(f"Evaluating extraction of predicate {self.predicate} with conditions {condition}. Monotone: {monotone}")
        return self.execute_condition(condition, monotone)

    def run_kb(self, extracted_facts=""):

        result = extracted_facts

        if self.advanced_prompt_type and self.__kb != "":
            try:
                result = Model.of_program(self.__kb, PredicateContainer.get_all_facts() + extracted_facts, sort=False).as_facts
            except Exception as e:
                #raise ValueError(f"Error running kb: {e}")
                return extracted_facts
                
        return result
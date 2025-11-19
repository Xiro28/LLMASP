import yaml

from typeguard import typechecked
from dataclasses import dataclass, field

from dumbo_asp.primitives.models import Model

from evaluate_input import EvaluateInput
from evaluate_output import EvaluateOuput



@typechecked
@dataclass(frozen=False)
class LLMASP:
    __configFilename: str = field(init=True, default="./config.yml")
    __config_behaviour: str = field(init=True, default="")
    __llm_model_extractor: str = field(init=True, default="")
    __llm_model_reasoner: str = field(init=True, default="")
    __config: dict = field(init=False)
    __b_config: dict = field(init=False)
    
    def __post_init__(self):
        self.preds = ""
        self.calc_preds = ""

        assert self.__llm_model_extractor != "", "The LLM extractor cannot be empty"

        if self.__llm_model_reasoner == "":
            self.__llm_model_reasoner = None

        self.__config = self.__load_config__(self.__configFilename)
        self.__b_config = self.__load_config__(self.__config_behaviour)
        self.evaluator = EvaluateInput((self.__llm_model_extractor, self.__llm_model_reasoner), self.__config, self.__b_config["preprocessing"])

    def __load_config__(self, path: str) -> dict | list:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)

    
    def infer(self, _input:str, _format:str) -> "LLMASP":
        """
            This method extracts predicates from the input handler by converting the input
            to ASP format.
                
            Returns:
                self object: The current LLMASP object with the extracted predicates.
        """
        
        self.preds = self.evaluator.run(_input, _format)

        return self
    
    def run_asp(self, use_preserved=False) -> "LLMASP":
        """
            Run ASP (Answer Set Programming) solver on the provided ASP code with predicates.
            
            This method initializes an ASP control instance, loads the ASP code from the specified file,
            adds predicates extracted from the user input, grounds the program, and solves it using an ASP solver.

            parameters:
                use_preserved (bool): A flag to determine whether to use the preserved predicates, calculated at each run.
            
            Returns:
                self object: The current LLMASP object with the calculated predicates.
        """

        assert self.preds != "", "No predicates to run ASP on. LLM might have failed to extract predicates from the user input."

        if (not use_preserved):
            self.calc_preds = Model.of_program(self.__config['knowledge_base'], self.preds, sort=False).as_facts
        else:
            self.calc_preds += Model.of_program(self.__config['knowledge_base'], self.preds + self.calc_preds, sort=False).as_facts

        return self

    
    def explain(self) -> str:
        """
            Convert the current LLMASP object to the specified class.
            
            This method converts the current LLMASP object to the specified class, which must be a subclass of TaskHandler.

            Parameters:
                _class: any: The class to convert the current LLMASP object to.
                
            Returns:
                any: The current LLMASP object converted to the specified class.
        """
        
        return EvaluateOuput(self.__llm_model, self.__config, self.preds, self.calc_preds).run()



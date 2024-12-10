import yaml

from openai import OpenAI

from typeguard import typechecked
from dataclasses import dataclass, field

from dumbo_asp.primitives.models import Model

from inputHandlers.abstractInputHandler import AbstractInputHandler
from outputHandlers.abstractOutputHandler import AbstractOutputHandler

@typechecked
@dataclass(frozen=False)
class LLMASP:
    __configFilename: str = field(init=True, default="./config.yml")
    __config: dict = field(init=False)
    
    def __post_init__(self):
        self.preds = ""
        self.calc_preds = ""

        self.__config = self.__load_config__(self.__configFilename)

    def __load_config__(self, path: str) -> dict | list:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)

    
    def infer(self, __input_evaluator_class, custom_input = "") -> "LLMASP":
        """
            This method extracts predicates from the input handler by converting the input
            to ASP format.
                
            Returns:
                self object: The current LLMASP object with the extracted predicates.
        """

        assert issubclass(__input_evaluator_class, AbstractInputHandler), "The input evaluator must be a subclass of Abstract"

        
        self.preds = __input_evaluator_class(self.__config).run(custom_input)

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

    
    def _as(self, _class) -> "any":
        """
            Convert the current LLMASP object to the specified class.
            
            This method converts the current LLMASP object to the specified class, which must be a subclass of TaskHandler.

            Parameters:
                _class: any: The class to convert the current LLMASP object to.
                
            Returns:
                any: The current LLMASP object converted to the specified class.
        """
        
        assert issubclass(_class, AbstractOutputHandler), "The class must be a subclass of AbstractOutputHandler."
        
        return _class(self.__config, self.preds, self.calc_preds)



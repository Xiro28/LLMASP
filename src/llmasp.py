import yaml

from dumbo_asp.primitives.models    import Model
from typeguard                      import typechecked
from dataclasses                    import dataclass, field

from evaluate_input import EvaluateInput


@typechecked
@dataclass
class LLMASP:
    __application_config_filename: str = field(init=True, default="")
    __behaviour_config_filename:   str = field(init=True, default="")
    
    __llm_model: str = field(init=True, default="")

    __behaviour_config:   dict = field(init=False)
    __application_config: dict = field(init=False)

    __extracted_preds: str = field(init=False, default="")
    __result_preds:    str = field(init=False, default="")

    
    def __post_init__(self):
        assert self.__llm_model != "", "The LLM extractor cannot be empty"

        self.__application_config = self.__load_config__(self.__application_config_filename)
        self.__behaviour_config = self.__load_config__(self.__behaviour_config_filename)

        self.evaluator = EvaluateInput(self.__llm_model, self.__application_config, self.__behaviour_config["preprocessing"])

    def __load_config__(self, path: str) -> dict | list:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)

    
    def infer(self, prompt:str, context:str, mode:str) -> "LLMASP":
        """
            This method extracts predicates from the input handler by converting the input
            to ASP format.
                
            Returns:
                self object: The current LLMASP object with the extracted predicates.
        """
        
        self.__extracted_preds = self.evaluator.run(prompt, context, mode)
        return self
    
    def run_asp(self) -> "LLMASP":
        """
            Run ASP (Answer Set Programming) solver on the provided ASP code with predicates.
            
            This method initializes an ASP control instance, loads the ASP code from the specified file,
            adds predicates extracted from the user input, grounds the program, and solves it using an ASP solver.

            parameters:
                use_preserved (bool): A flag to determine whether to use the preserved predicates, calculated at each run.
            
            Returns:
                self object: The current LLMASP object with the calculated predicates.
        """

        assert self.__extracted_preds != "", "No predicates to run ASP on. LLM might have failed to extract predicates from the user input."

        self.__result_preds = Model.of_program(self.__application_config['knowledge_base'], self.__extracted_preds, sort=False).as_facts
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
        
        #return EvaluateOuput(self.__llm_model, self.__application_config, self.__extracted_preds, self.__result_preds).run()

        return "NOT IMPLEMENTED YET"

    @property
    def asp_result(self) -> str:
        return self.__result_preds

    @property
    def extracted_preds(self) -> str:
        return self.__extracted_preds
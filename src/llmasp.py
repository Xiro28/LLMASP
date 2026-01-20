import yaml

from dumbo_asp.primitives.models    import Model
from typeguard                      import typechecked
from dataclasses                    import dataclass, field

from core.input.evaluate_prompt         import EvaluatePrompt


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

        self.evaluator = EvaluatePrompt(self.__llm_model,  self.__behaviour_config["preprocessing"], self.__application_config)

    def __load_config__(self, path: str) -> dict | list:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)

    
    def infer(self, prompt:str, context:str, mode:str) -> "LLMASP":
        self.__extracted_preds = self.evaluator.run(prompt, context, mode)
        return self
    
    def run_asp(self) -> "LLMASP":
        assert self.__extracted_preds != "", "No predicates to run ASP on. LLM might have failed to extract predicates from the user input."

        self.__result_preds = Model.of_program(self.__application_config['knowledge_base'], self.__extracted_preds, sort=False).as_facts
        return self

    
    def explain(self) -> str:
        raise NotImplementedError("NOT IMPLEMENTED YET")
    
    @property
    def extracted_preds(self) -> str:
        return self.__extracted_preds
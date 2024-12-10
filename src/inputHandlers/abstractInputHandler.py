import re

from utils.LLMHandler import LLMHandler
from utils.links import Links

from dataclasses import dataclass, field
from typeguard import typechecked

from utils.classBuilder import ClassBuilder

@typechecked
@dataclass(frozen=False)
class AbstractInputHandler:
    __config: dict = field(default=None)
    __system_prompt: str = field(default='')

    def __post_init__(self):
        assert self.__system_prompt != '', "The system prompt cannot be empty."
        
        self.__llm_instance = LLMHandler(self.__system_prompt)

        ## Create the classes needed for the instructor LLM
        self.__classes = ClassBuilder(self._AbstractInputHandler__config['preprocessing'], True).get_classes()
        self.links = Links(self._AbstractInputHandler__config['links'])

    def __filter_asp_atoms__(self, req: str) -> str:
        return " ".join(re.findall(r"\b[a-zA-Z][\w_]*\([^)]*\)\.", req))

    def run(self) -> str:
        raise NotImplementedError("The run method must be implemented.")
    
    def get_classes(self) -> dict:
        """
        Get the classes.

        Returns:
            list: The classes.
        """
        return self.__classes

    def get_system_prompt(self) -> str:
        """
        Get the system prompt.

        Returns:
            str: The system prompt.
        """
        return self.__system_prompt
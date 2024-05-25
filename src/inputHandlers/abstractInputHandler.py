import re

from utils.LLMHandler import LLMHandler

from dataclasses import dataclass, field
from typeguard import typechecked

@typechecked
@dataclass(frozen=False)
class AbstractInputHandler:
    __config: dict = field(default=None)
    __system_prompt: str = field(default='')

    def __post_init__(self):
        assert self.__system_prompt != '', "The system prompt cannot be empty."
        
        self.__llm_instance = LLMHandler(self.__system_prompt)

    def __filter_asp_atoms__(self, req: str) -> str:
        return " ".join(re.findall(r"\b[a-zA-Z][\w_]*\([^)]*\)\.", req))

    def run(self) -> str:
        raise NotImplementedError("The run method must be implemented.")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt.

        Returns:
            str: The system prompt.
        """
        return self.__system_prompt
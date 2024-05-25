from dataclasses import dataclass
from typeguard import typechecked


@typechecked
@dataclass(frozen=False)
class AbstractOutputHandler:
    __config: dict
    __preds: str
    __calc_preds: str

    def __post_init__(self):
        assert self.__config == '', "The config array must not be empty."
        assert self.__preds  == '', "Input predicates must not be empty. LLM might not have found any predicates."

    def run(self) -> None:
        raise NotImplementedError("Not implemented yet.")

    def get_info(self) -> str:
        """
        Get the calculated and extracted predicates.

        Returns:
            str: The calculated and extracted predicates.
        """
        return f"Atoms extracted: {self.__preds}\nAtoms calculated: {self.__calc_preds}"
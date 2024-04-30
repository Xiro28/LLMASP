from dataclasses import dataclass
from typeguard import typechecked


@typechecked
@dataclass(frozen=False)
class TaskHandler:
    __config: dict
    __preds: str
    __calc_preds: str

    def __post_init__(self):
        assert len(self.__config) > 0, "The config file must not be empty."
        #assert len(self.__calc_preds) > 0, "The calculated predicates must not be empty. ASP might not have found any predicates."

    def get_info(self) -> str:
        """
        Get the calculated and extracted predicates.

        Returns:
            str: The calculated and extracted predicates.
        """
        return f"Atoms extracted: {self.__preds}\nAtoms calculated: {self.__calc_preds}"
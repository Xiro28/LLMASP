from dataclasses import dataclass
from typeguard import typechecked

@typechecked
@dataclass(frozen=True)
class TaskHandler:
    __config: dict
    __preds: str
    __calc_preds: str

    def __post_init__(self):

        if len(self.__config) == 0:
            raise ValueError("The config file must not be empty.")
        
        if len(self.__calc_preds) == 0:
            print("Warning: The calculated predicates are empty.")
            #raise ValueError("The calculated predicates must not be empty.")

    def __toGPTDict__(self, text: str) -> dict:
        return {"role": "user", "content": text}

    def getInfo(self) -> str:
        """
        Get the calculated and extracted predicates.

        Returns:
            str: The calculated and extracted predicates.
        """
        return f"Atoms extracted: {self.__preds}\nAtoms calculated: {self.__calc_preds}"
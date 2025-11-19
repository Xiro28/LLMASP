from dataclasses import dataclass
from utils.yaml_to_csv import GrammarsBuilder
from typeguard import typechecked
from pydantic import BaseModel, Field

from predicate import Predicate
from fact_manager import FactManager

import re
from utils.class_builder import ClassBuilder
from utils.llm_handler import LLMHandler

@typechecked
@dataclass(frozen=False)
class EvaluateInput:

    ## TODO: Move part of this logic to a better place (Consider creating a class Reasoning)

    def __init__ (self, _llm_models, config, b_config):
        #self.__llm_instance_extractor = LLMHandler(_llm_models[0], """You are an expert in data extraction.""")
        self.__llm_instance_reasoner = LLMHandler(_llm_models[1], """You are an expert in data description.""")
        self.__llm_instance_extractor = LLMHandler(_llm_models[0], b_config["init"])
        self.__classes = ClassBuilder(config['predicates']).get_classes()
        self.__grammars = GrammarsBuilder(config['predicates']).get_grammars()
            
        self.__predicates = [Predicate(*pred.popitem()) for pred in config.get('predicates', [])]
        self.__config = config
        self.__b_config = b_config

        print("Predicates:", [str(p) for p in self.__predicates])
        print("Grammars:", self.__grammars)

        #self.__reasoning_out = {}

    def __filter_asp_atoms__(self, req: str) -> str:
        return " ".join(re.findall(r"\b[a-zA-Z][\w_]*\([^)]*\)\.", req))
    
    
    def __natural_to_asp__(self, _input: str, _format:str) -> str:

        problem_definition = self.__config.get('problem_definition', '')
        _class_dict = self.__classes
        
        # Get only the main classes and not the list of classes
        main_class = [main_class for main_class in _class_dict.items() if "list_" not in main_class[0]]

        #for each main_class, define the fields and annotations
        dict_ = {f"{class_[0]}":  Field(title=class_[0], description=self.__predicates[idx].prompt, default=None) for idx, class_ in enumerate(main_class)}
        dict_["__annotations__"] = {f"{name}": list[cls] for name, cls in main_class}

        # Create the atoms class dynamically during runtime
        atoms_class =  type(
            "atoms",
            (BaseModel,), 
            dict_
        )

        mapping = self.__b_config["mapping"]
        mapping = mapping.replace("{input}", _input)
        mapping = mapping.replace("{instructions}", "\n".join(atom_descriptions))
        mapping = mapping.replace("{atom}", " ".join(atom_to_extract))
        real_context = self.__b_config["context"].replace("{context}", f"{_format}")

        response =  self.__llm_instance_extractor.invoke_llm_constrained(mapping, atoms_class, real_context)

        if response is not None:
            for c, _ in main_class:
                list_of_atoms = response.dict().get(f"{c}")

                if list_of_atoms:
                    for atoms in list_of_atoms:
                        if atoms is not None:
                            FactManager.add_fact(str(_class_dict[c](**atoms)) + "\n")

        return FactManager.get_all_facts()
    
    def __natural_no_reason_to_asp_multi__(self, _input: str, _format:str) -> str:

        _list = [list_class for list_class in self.__classes.items() if "list_" in list_class[0]]
        main_class = [main_class[0] for main_class in self.__classes.items() if "list_" not in main_class[0]]

        mapping = self.__b_config["mapping"]
        mapping = mapping.replace("{input}", _input)
        
        for i, predicate in enumerate(self.__predicates):

            if predicate.check_existence_condition() == False:
                continue

            real_context = self.__b_config["context"].replace("{context}", f"{_format}")
            
            appl_mapping = mapping.replace("{instructions}", predicate.prompt)
            appl_mapping = appl_mapping.replace("{atom}", predicate.predicate)

            response = self.__llm_instance_extractor.invoke_llm_constrained(appl_mapping, _list[i][1], real_context)

            if response != None:

                atom_list = response.dict().get(f"list_{main_class[i]}")

                if atom_list != None:
                    for atom in atom_list:
                        if atom != None:
                            class_name = main_class[i]
                            class_instance = str(self.__classes[class_name](**atom))

                            FactManager.add_fact(class_instance + "\n")
                    FactManager.add_fact(predicate.run_kb())
        
        return FactManager.get_all_facts()

    def __natural_no_reason_to_asp_single__(self, _input: str, _format:str) -> str:

        _list = [list_class for list_class in self.__classes.items() if "list_" in list_class[0]]
        main_class = [main_class[0] for main_class in self.__classes.items() if "list_" not in main_class[0]]

        mapping = self.__b_config["mapping"]
        mapping = mapping.replace("{input}", _input)
        
        for i, predicate in enumerate(self.__predicates):

            real_context = self.__b_config["context"].replace("{context}", f"{_format}")
            
            appl_mapping = mapping.replace("{instructions}", predicate.prompt)
            appl_mapping = appl_mapping.replace("{atom}", predicate.predicate)

            response = self.__llm_instance_extractor.invoke_llm_constrained(appl_mapping , _list[i][1], real_context)

            if response != None:

                atom_list = response.dict().get(f"list_{main_class[i]}")

                if atom_list != None:
                    for atom in atom_list:
                        if atom != None:
                            class_name = main_class[i]
                            class_instance = str(self.__classes[class_name](**atom))

                            FactManager.add_fact(class_instance + "\n")
        
        return FactManager.get_all_facts()

    def run(self, _input:str, _format:str) -> str:
        """
            Run the input handler to convert the user input to ASP format.
            
            This method takes user input and converts it to ASP format using the natural_to_asp method.
            It then returns the ASP-formatted output.
                
            Returns:
                str: The ASP-formatted output generated from the user input.
        """
        response = self.__natural_no_reason_to_asp_multi__(_input, _format)

        FactManager.reset_facts()

        return self.__filter_asp_atoms__(response)

import re

from dataclasses import dataclass
from typeguard   import typechecked
from pydantic    import BaseModel, Field

from predicate    import Predicate
from fact_manager import FactManager

from utils.to_tsv_grammar import GrammarsBuilder
from utils.to_json_class  import ClassBuilder
from utils.llm_handler    import LLMHandler

@typechecked
@dataclass
class EvaluateInput:
    llm_model_name: str = Field(init=True)
    application_config: dict = Field(init=True)
    behaviour_config: dict = Field(init=True)

    def __post_init__ (self):
        self.__llm_instance_extractor = LLMHandler(self.llm_model_name, self.behaviour_config["init"])

        self.__json_classes = ClassBuilder(self.application_config['predicates']).get_classes()
        self.__csv_grammars = GrammarsBuilder(self.application_config['predicates']).get_grammars()

        self.__predicates_to_extract = [Predicate(*pred.popitem()) for pred in self.application_config.get('predicates', [])]


    def __filter_asp_atoms__(self, req: str) -> str:
        return " ".join(re.findall(r"\b[a-zA-Z][\w_]*\([^)]*\)\.", req))
    
    def __extract_predicates_multi_call_json(self, prompt: str, context:str) -> str:

        json_grammars = [predicate_class[1] for predicate_class in self.__json_classes.items()]

        behaviour_mapping = self.behaviour_config["mapping"].replace("{input}", prompt)
        behaviour_context = self.behaviour_config["context"].replace("{context}", f"{context}")
        
        for i, predicate in enumerate(self.__predicates_to_extract):

            if not predicate.has_to_be_extracted():
                continue
            
            appl_mapping = behaviour_mapping.replace("{instructions}", predicate.prompt_description)
            appl_mapping = appl_mapping.replace("{atom}", predicate.predicate)

            response = self.__llm_instance_extractor.invoke_llm_constrained(appl_mapping, json_grammars[i], behaviour_context)

            if response:
                class_name = predicate.predicate_head
                atom_list = getattr(response, f"list_{class_name}", None)

                if atom_list:
                    extracted_facts = " ".join([str(atom) for atom in atom_list])
                    FactManager.add_fact(predicate.run_kb(extracted_facts))
        
        return FactManager.get_all_facts()

    def __extract_predicates_multi_call_tsv(self, prompt: str, context:str) -> str:

        def from_tsv_to_asp(line):
            tokens = line.split("\t")
            return f"{tokens[0]}({','.join(tokens[1:])})."

        behaviour_mapping = self.behaviour_config["mapping"].replace("{input}", prompt)
        behaviour_context = self.behaviour_config["context"].replace("{context}", context)
            
        for i, predicate in enumerate(self.__predicates_to_extract):

            #csv grammar returs also an example of usage (not used now)
            grammar, example = self.__csv_grammars[predicate.predicate_head]

            if not predicate.has_to_be_extracted():
                continue
            
            appl_mapping = behaviour_mapping.replace("{instructions}", f"{predicate.prompt_description}")
            appl_mapping = appl_mapping.replace("{atom}", f"{predicate.predicate}")

            response = self.__llm_instance_extractor.invoke_llm_constrained(appl_mapping, grammar, behaviour_context)

            if response and response != "empty_predicate":

                extracted_atoms_list = [
                    from_tsv_to_asp(line) 
                    for line in response.splitlines() 
                    if line and "empty_predicate" not in line
                ]

                if extracted_atoms_list:
                    result_atoms = "\n".join(extracted_atoms_list) + "\n"
                    FactManager.add_fact(predicate.run_kb(result_atoms))

        return FactManager.get_all_facts()



    def run(self, prompt:str, context:str, grammar_type:str) -> str:
        """
            Run the input handler to convert the user input to ASP format.
            
            This method takes user input and converts it to ASP format using the natural_to_asp method.
            It then returns the ASP-formatted output.
                
            Returns:    
                str: The ASP-formatted output generated from the user input.
        """

        mode: dict[str, any] = {
            "json": self.__extract_predicates_multi_call_json,
            "tsv": self.__extract_predicates_multi_call_tsv
        }

        if grammar_type in mode:
            response = mode[grammar_type](prompt, context)
        else:
            raise ValueError(f"Unsupported grammar type: {grammar_type}")

        FactManager.reset_facts()
        return self.__filter_asp_atoms__(response)

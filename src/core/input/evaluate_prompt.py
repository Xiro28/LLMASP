import re

from typing         import Optional
from dataclasses    import dataclass, field

from ..predicate.predicate            import Predicate
from ..predicate.predicate_container  import PredicateContainer

from ..builders.tsv_grammar           import TSVGrammarBuilder
from ..builders.csv_grammar_builder   import CSVGrammarBuilder
from ..builders.asp_grammar_builder   import ASPGrammarBuilder
from ..builders.json_schema           import JSONSchemaBuilder

from ..llm_handler                    import LLMHandler


@dataclass()
class EvaluatePrompt:
    llm_model:          str
    behaviour_config:   dict
    application_config: dict

    __llm_instance:         Optional[LLMHandler]    = field(init=False, default=None)
    __predicates:           list[Predicate]         = field(init=False, default_factory=list)
    __structured_output:    dict                    = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.__system_prompt = f"{self.behaviour_config['init']}\n{self.application_config['problem_definition']}"
        self.__llm_instance = LLMHandler(self.llm_model, self.__system_prompt)

        # Build all the grammars with their specific builders
        self.__structured_output["json"] = JSONSchemaBuilder(self.application_config['predicates']).get_classes()
        self.__structured_output["tsv"]  = TSVGrammarBuilder(self.application_config['predicates']).get_grammars()
        self.__structured_output["csv"]  = CSVGrammarBuilder(self.application_config['predicates']).get_grammars()
        self.__structured_output["asp"]  = ASPGrammarBuilder(self.application_config['predicates']).get_grammars()

        # Get all the predicates from the application config
        self.__predicates = [Predicate(*pred.popitem()) for pred in self.application_config.get('predicates', [])]

    def __filter_asp_atoms__(self, req: str) -> str:
        return " ".join(re.findall(r"\w+\([a-zA-Z0-9_]+(?:,\s*[a-zA-Z0-9_]+)*\)\.", req))
    

    def __structured_output_call(self, mode: str, prompt: str, context: str) -> tuple[str, Predicate] | None:
        behaviour_mapping = self.behaviour_config["mapping"].replace("{input}", prompt)
        behaviour_context = self.behaviour_config["context"].replace("{context}", f"{context}")
        
        for predicate in self.__predicates:

            if not predicate.has_to_be_extracted():
                continue
            
            appl_mapping = behaviour_mapping.replace("{instructions}", f"{predicate.prompt_description}")
            appl_mapping = appl_mapping.replace("{atom}", predicate.predicate)

            yield self.__llm_instance.invoke_llm_constrained(appl_mapping, self.__structured_output[mode][0][predicate.predicate_head], behaviour_context), predicate

    def __extract_predicates_multi_call_grammar(self, mode: str, prompt: str, context:str) -> str:

        for response, predicate in self.__structured_output_call(mode, prompt, context):

            # if a class-based output (only json since it uses the json schema and each predicate is a class. The class itself has the to_string method overriden to return the asp atom)
            if response and self.__structured_output[mode][1] is None:
                class_name = predicate.predicate_head
                atom_list = getattr(response, f"list_{class_name}", None)

                if atom_list:
                    extracted_facts = self.__filter_asp_atoms__(" ".join([str(atom) for atom in atom_list]))
                    PredicateContainer.add_predicate(predicate.run_kb(extracted_facts))

            elif response and response != "empty_predicate":
                # if a grammar-based output (tsv, csv, asp), use the returned grammar to parse the output lines (it can be found in the second position of the structured output tuple)

                extracted_atoms_list = [
                    self.__structured_output[mode][1](line) 
                    for line in response.splitlines() 
                    if line and "empty_predicate" not in line
                ]

                if extracted_atoms_list:
                    result_atoms = self.__filter_asp_atoms__("\n".join(extracted_atoms_list) + "\n")
                    PredicateContainer.add_predicate(predicate.run_kb(result_atoms))

        return PredicateContainer.get_all_predicates()

    def run(self, prompt:str, context:str, grammar_type:str) -> None:

        if grammar_type in self.__structured_output.keys():
            response = self.__extract_predicates_multi_call_grammar(grammar_type,prompt, context)
        else:
            raise ValueError(f"Unsupported grammar type: {grammar_type}")

        PredicateContainer.reset_container()
        return response
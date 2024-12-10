from typeguard import typechecked
from dataclasses import dataclass
from outputHandlers.abstractOutputHandler import AbstractOutputHandler
from utils.LLMHandler import LLMHandler

@typechecked
@dataclass(frozen=False)
class EvaluateOuput(AbstractOutputHandler):

    def __post_init__(self):
        super().__post_init__()

        self.__llm_instance = LLMHandler("""You are an expert in Datalog to Natural Language translator. 
                                         Summarize the response given in a detailed form.""")
    
    def __post_output_seasoning__(self) -> list:
        """
            Enhances the given input with additional information from the config file to help with the natural language conversion.

            Returns:
                str: The seasoned datalog output calculated after runASP function with added information to help the LLM for natural language conversion.
        """

        questions = self._AbstractOutputHandler__config['postprocessing']
        the_asp_output = f"[FACTS]{self._AbstractOutputHandler__calc_preds} {self._AbstractOutputHandler__preds}[/FACTS]."

        prompt = [the_asp_output]

        for q in questions:

            q_key, q_value = list(q.items())[0]

            if q_key == '_':
                prompt.append(f"""Here is some context that you MUST analyze and remember.
                                  {q_value}   
                                  Remember this context and don't say anything!\n""")
            else:
                #check if the predicate that we're going to explain is in the ASP output
                if q_key.split('(')[0] in the_asp_output:
                    prompt.append(f"Each fact matching {q_key} must be interpreted as follows: {q_value}")


        return prompt

    def run(self) -> str:
        """
            Convert ASP (Answer Set Programming) to natural language format.
            
            
            This method takes ASP atoms and converts them into natural language format 
            using the GPT-3.5-turbo model via the Gemini API.

            Parameters:
                asp_atoms (str): The ASP atoms to be converted to natural language.
            
            Returns:
                str: The natural language output generated from the ASP atoms.
        """

        R = ""

        for prompt in self.__post_output_seasoning__():
            response = self.__llm_instance.invoke_llm([prompt])
            R += response
        
        return self.__llm_instance.invoke_llm([f"Summerize the following responses: {R}"])

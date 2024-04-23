from typeguard import typechecked
from dataclasses import dataclass
from TaskHandler import TaskHandler

@typechecked
@dataclass(frozen=True)
class Evaluator(TaskHandler):

    def __gpt_system_start_prompt__(self) -> dict:

        def build_example():
            #TODO: Implement the build_example function
            return ""
        
        return {"role": "system", "content": '\n'.join([
            build_example(),
            """
                You are now a Datalog to Natural Language translator.
                You will be given relational facts and mapping instructions.
                Relational facts are given in the form [FACTS]atoms[/FACTS].
                Remember these instructions and don't say anything!
            """.strip() + '\n'])}
    
    def __post_output_seasoning__(self) -> str:
        """
            Enhances the given input with additional information from the config file to help with the natural language conversion.

            Returns:
                str: The seasoned datalog output calculated after runASP function with added information to help the LLM for natural language conversion.
        """

        questions = self._TaskHandler__config['postprocessing']
        the_asp_output = f"[FACTS]{self._TaskHandler__calc_preds} {self._TaskHandler__preds}[/FACTS]"

        for q_key, q_value in questions.items():

            if q_key == '_':
                prompt += f"""
                            Here is some context that you MUST analyze and remember.
                            {q_value}
                            Remember this context and don't say anything!\n
                            """
            else:
                prompt += f"""
                            {the_asp_output}
                            Each fact matching {q_key} must be interpreted as follows: {q_value}\n
                            """

        return prompt + '\nSummarize the following responses'

    def __asp_to_natural__(self) -> str:
        """
            Convert ASP (Answer Set Programming) to natural language format.
            
            
            This method takes ASP atoms and converts them into natural language format 
            using the GPT-3.5-turbo model via the Gemini API.

            Parameters:
                asp_atoms (str): The ASP atoms to be converted to natural language.
            
            Returns:
                str: The natural language output generated from the ASP atoms.
        """
        return self.__llm.create(
                model="TheBloke/CodeLlama-7B-Instruct-GGUF/codellama-7b-instruct.Q5_K_M.gguf",
                temperature=0.0,
                messages=[self.__gpt_system_start_prompt__(), self.__to_gpt_dict__(self.__post_output_seasoning__())],
                stream=False,
            )
    

    
    def get_natural_output(self) -> str:
        """
        Convert the output of the ASP solver into a natural language string.

        Returns:
            str: The natural language representation of the ASP output.
        """
        return self.__asp_to_natural__()

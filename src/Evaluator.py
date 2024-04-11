from typeguard import typechecked
from dataclasses import dataclass
from TaskHandler import TaskHandler
from g4f import ChatCompletion, Provider

@typechecked
@dataclass(frozen=True)
class Evaluator(TaskHandler):
    def __postOutputSeasoning__(self) -> str:
        """
            Enhances the given input with additional information from the config file to help with the natural language conversion.

            Returns:
                str: The seasoned datalog output calculated after runASP function with added information to help the LLM for natural language conversion.
        """

        questions = self._TaskHandler__config['postprocessing']
        the_asp_output = f"[ASP_OUTPUT]{self._TaskHandler__calc_preds}[/ASP_OUTPUT]"
        the_asp_input  = f"[ASP_INPUT]{self._TaskHandler__preds}[/ASP_INPUT]"

        return '\n'.join([the_asp_input,
            """
                You are a Datalog to NaturalLanguage translator.
                To translate your input to NaturalLanguage, you will be asked a series of questions.
                The answer are inside the asp output provided with [ASP_OUTPUT]output[/ASP_OUTPUT]. 
                Try to explain the output in a natural and human way.
                If you want to add more info have a look at the input given to obtain the output [ASP_INPUT]input[/ASP_INPUT].
                Once you answered the questions, the output as to be a natural language phrase.
            """.strip() + '\n',
            '\n'.join(
                q['prompt'].replace('§', the_asp_output, 1) + "\n"
                for q in questions
            ),

        ])

    def __asp2Natural__(self) -> str:
        """
            Convert ASP (Answer Set Programming) to natural language format.
            
            
            This method takes ASP atoms and converts them into natural language format 
            using the GPT-3.5-turbo model via the Gemini API.

            Parameters:
                asp_atoms (str): The ASP atoms to be converted to natural language.
            
            Returns:
                str: The natural language output generated from the ASP atoms.
        """
        return ChatCompletion.create(
                model="gpt-3.5-turbo",
                provider=Provider.Gemini,
                messages=[self.__toGPTDict__(self.__postOutputSeasoning__())],
                stream=False,
            )
    
    def getNaturalOutput(self) -> str:
        """
        Convert the output of the ASP solver into a natural language string.

        Returns:
            str: The natural language representation of the ASP output.
        """
        return self.__asp2Natural__()

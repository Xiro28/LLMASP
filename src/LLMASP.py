import re
import yaml

from ExecutorHandler import ExecutorHandler
from Evaluator import Evaluator
from typeguard import typechecked
from g4f import ChatCompletion, Provider
from dataclasses import dataclass, field
from dumbo_asp.primitives.models import Model
from g4f.cookies import set_cookies, load_cookies_from_browsers


@typechecked
@dataclass(frozen=False)
class LLMASP:
    __configFilename: str
    __ragDatabaseFilename: str
    __aspCodeFilename: str

    __config: dict = field(init=False)
    __docs_rag: list = field(init=False)
    
    def __post_init__(self):
        self.__config = self.__loadConfig__(self.__configFilename)
        self.__docs_rag = self.__loadConfig__(self.__ragDatabaseFilename)

        self.preds = ""
        self.calc_preds = ""

        load_cookies_from_browsers(".google.com")

    def __loadConfig__(self, path: str) -> dict | list:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)
    
    def __toGPTDict__(self, text: str) -> dict:
        return {"role": "user", "content": text}
 
    def __filterASPAtoms__(self, req: str) -> str:
        return " ".join(re.findall(r"\b[a-zA-Z][\w_]*(?:\([^)]*\))?\.", req))

    def __preInputSeasoning__(self, user_input: str) -> str:
        """
            Enhances the given input with additional information from the config file to help with the ASP atom extraction.
            
            Parameters:
                user_input: str: The input to be seasoned.
                
            Returns:
                str: The seasoned input with added information to help the LLM for ASP atom extraction.
        """

        def buildExample():
            if len(self.__docs_rag) == 0:
                return "[EXAMPLE][/EXAMPLE]"
            
            return ''.join(
                f"[EXAMPLE][USER_INPUT]{doc['prompt']}[/USER_INPUT]\n[ANSWER_FORMAT]{doc['response']}[/ANSWER_FORMAT][/EXAMPLE]"
                for doc in self.__docs_rag
            )


        questions = self.__config['preprocessing']
        the_user_input = f"[USER_INPUT]{user_input}[/USER_INPUT]"

        return '\n'.join([
            buildExample(),
            """
                You are a Natural Language to Datalog translator.
                To translate your input to Datalog, you will be asked a series of questions.
                The answer are inside the user input provided with [USER_INPUT]input[/USER_INPUT] and 
                the format is provided with [ANSWER_FORMAT]predicate(terms).[/ANSWER_FORMAT].
                Predicate is a lowercase string (possibly including underscores).
                Terms is a comma-separated list of either double quoted strings or integers.
                Be sure to control the number of terms in each answer!
                A Natural Language to Datalog translator should work as showed inside [EXAMPLE][/EXAMPLE].
                An answer must not be answered if it is not present in the user input, so general form predicate shoud be present.
            """.strip() + '\n',
            '\n'.join(
                q['prompt'].replace('§', the_user_input, 1) + f" [ANSWER_FORMAT]{q['predicate']}[/ANSWER_FORMAT]\n"
                for q in questions
            )
        ])

    def __natural2ASP__(self, user_input: str) -> str:
        """
            Convert natural language input to ASP (Answer Set Programming) format.
            
            This method takes a natural language input provided by the user and converts it
            into ASP format using the GPT-3.5-turbo model via the Gemini API. It preprocesses
            the input by performing input seasoning to extract the atoms contained into the config file.
            
            Parameters:
                user_input (str): The natural language input provided by the user.
                
            Returns:
                str: The ASP-formatted output generated from the natural language input.
        """
        
        return ChatCompletion.create(
                model="gpt-3.5-turbo",
                provider=Provider.Gemini,
                messages=[self.__toGPTDict__(self.__preInputSeasoning__(user_input))],
                stream=False,
            )
        
    
    def extractPreds(self, user_input: str, TRAIN_ON: bool = False) -> "LLMASP":
        """
            Extract predicates from the given user input.
            
            This method extracts predicates from the user input by converting the input
            to ASP format using the __natural2ASP__ method, and then filtering out the
            relevant ASP atoms using the __filterASPAtoms__ method.

            If TRAIN_ON is set to True, the extracted predicates will be saved 
            to the rag_doc database.
            
            Parameters:
                user_input (str): The natural language input provided by the user.
                TRAIN_ON (bool): A flag to determine whether to save the extracted predicates 
                to the rag_doc database.
                
            Returns:
                self object: The current LLMASP object with the extracted predicates.
        """
        
        res = self.__natural2ASP__(user_input)
        self.preds = self.__filterASPAtoms__(res)

        print("RAW OUTPUT: ", res)
        if TRAIN_ON:
            out: str = input(f"Do you want to salve to rag_doc these results: {self.preds}? (y/n): ")

            if out == "y":
                self.__docs_rag.append({"prompt": user_input, "response": self.preds})
                yaml.dump(self.__docs_rag, open(self.__ragDatabaseFilename, "w"))

        return self
    
    def runASP(self) -> "LLMASP":
        """
            Run ASP (Answer Set Programming) solver on the provided ASP code with predicates.
            
            This method initializes an ASP control instance, loads the ASP code from the specified file,
            adds predicates extracted from the user input, grounds the program, and solves it using an ASP solver.
            
            Returns:
                self object: The current LLMASP object with the calculated predicates.
        """

        self.calc_preds = Model.of_program(open(self.__aspCodeFilename).read(), self.preds, sort=False)
        return self
    
    def getEvaluator(self) -> "Evaluator":
        return Evaluator(self.__config, self.preds, str(self.calc_preds))



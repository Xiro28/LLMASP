import re
from dataclasses import dataclass, field

import g4f
import yaml
from dumbo_asp.primitives.models import Model
from g4f.cookies import set_cookies
from typeguard import typechecked


@typechecked
@dataclass(frozen=False)
class LLMASP:
    configFilename: str
    valaspConfigFilename: str
    aspCodeFilename: str
    _1PSID: str
    _1PSIDTS: str

    __config: dict = field(init=False)
    __valasp_yaml: dict = field(init=False)
    
    def __post_init__(self):
        set_cookies(".google.com", {
            "__Secure-1PSID": self._1PSID,
            "__Secure-1PSIDTS": self._1PSIDTS
        })

        self.__config = self.__loadConfig__(self.configFilename)
        #self.__valasp_yaml = self.__loadConfig__(self.valaspConfigFilename)

    def __loadConfig__(self, path: str) -> dict:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)
   
    def __toGPTDict__(self, text: str) -> dict:
        return {"role": "user", "content": text}
 
    def __filterASPAtoms__(self, req: str) -> str:
        return " ".join(re.findall(r"\b[a-zA-Z][\w_]*(?:\([^)]*\))?\.", req))

    def __inputSeasoning__(self, user_input: str) -> str:
        """
            Enhances the given input with additional information from the config file to help with the ASP atom extraction.
            
            Parameters:
                user_input: str: The input to be seasoned.
                
            Returns:
                str: The seasoned input with added information to help the LLM for ASP atom extraction.
        """

        questions = self.__config['preprocessing']
        the_user_input = f"[USER_INPUT]{user_input}[/USER_INPUT]"

        return '\n'.join([
            """
You are a NaturalLanguage to Datalog translator.
You are going to be asked a series of questions. The answer are inside the user input provided with [USER_INPUT]input[/USER_INPUT]. The answer format is provided with [ANSWER_FORMAT]predicate(terms).[/ANSWER_FORMAT].
Predicate is a lowercase string (possibly including underscores).
Terms is a comma-separated list of either double quoted strings or integers.
Be sure to control the number of terms in each answer!
If a question doesn't have a clear answer, skip it.
            """.strip() + '\n',
            '\n'.join(
                q['prompt'].replace('§', the_user_input, 1) + f" [ANSWER_FORMAT]{q['predicate']}[/ANSWER_FORMAT]\n"
                for q in questions
            ),
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
        
        return g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                provider=g4f.Provider.Gemini,
                messages=[self.__toGPTDict__(self.__inputSeasoning__(user_input))],
                stream=False,
            )
    
    def extractPreds(self, user_input: str) -> "LLMASP":
        """
            Extract predicates from the given user input.
            
            This method extracts predicates from the user input by converting the input
            to ASP format using the __natural2ASP__ method, and then filtering out the
            relevant ASP atoms using the __filterASPAtoms__ method.
            
            Parameters:
                user_input (str): The natural language input provided by the user.
                
            Returns:
                self object: The current LLMASP object with the extracted predicates.
        """
        
        res = self.__natural2ASP__(user_input)
        self.preds = self.__filterASPAtoms__(res)
        return self
    
    def runASP(self) -> "LLMASP":
        """
            Run ASP (Answer Set Programming) solver on the provided ASP code with predicates.
            
            This method initializes an ASP control instance, loads the ASP code from the specified file,
            adds predicates extracted from the user input, grounds the program, and solves it using an ASP solver.
            
            Returns:
                self object: The current LLMASP object with the calculated predicates.
        """

        self.calc_preds = Model.of_program(open(self.aspCodeFilename).read(), self.preds, sort=False)
        return self
    
    def getInfo(self) -> str:
        """
            Get the calculated predicates from the ASP solver.
            
            Returns:
                str: The calculated predicates from the ASP solver.
        """
        
        return f"Atoms extracted: {self.preds}\nAtoms calculated: {self.calc_preds}"


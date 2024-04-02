from typing import AnyStr
from clingo import Control
from typeguard import typechecked
from dataclasses import InitVar, dataclass, field
from g4f.cookies import set_cookies

import re
import g4f
import yaml

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
            "__Secure-1PSIDTS" : self._1PSIDTS
        })

        self.__config = self.__loadConfig__(self.configFilename)
        self.__valasp_yaml = self.__loadConfig__(self.valaspConfigFilename)

    def __loadConfig__(self, path: str) -> dict:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)
   
    def __toGPTDict__(self, text: str) -> dict:
        return {"role": "user", "content": text}
 
    def __cleanOutputRequest__(self, req: str) -> str:
        return " ".join(re.findall(r"\b[a-zA-Z][\w_]*(?:\([^)]*\))?\.", req))

    def __natural2ASP__(self, user_input: str) -> str:

        questions =  self.__config['preprocessing']

        res =  "You are a NaturalLanguage to AnswerSetProgramming translator\n"
        res += "You are going to be asked a series of questions and the answer are inside the user input provided with: [USRIN] input [/USRIN]\n"
        res += "Be sure to control the arity of the predicates!\n"
        res += "If a question doesn't have a clear answer, skip it.\n"
        res += "Also, keep everything lowercase! \n\n" 
        
        inputToBeProcessed = f"[USRIN] {user_input} [/USRIN]\n\n"

        for q in questions:
            if q['prompt'].strip()[-1] == '$':
                res += q['prompt'][:-1] + inputToBeProcessed + '\n'
            else:
                res += inputToBeProcessed + q['prompt'][1:]  + '\n'

        res += '\nFill the answer in the following structure:\n'

        for q in questions:
            res += q['predicate'] + '\n'

        return res

    def __makeRequest__(self, user_input: str) -> str:
        return g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                provider=g4f.Provider.Gemini,
                messages=[self.__toGPTDict__(self.__natural2ASP__(user_input))],
                stream=False,
            )
    
    def extractPreds(self, user_input: str) -> str:
        req = self.__makeRequest__(user_input)
        self.preds = self.__cleanOutputRequest__(req)
        return self.preds
    
    def runASP(self):
        control = Control()
        control.load(self.aspCodeFilename)
        control.add("base", [], self.preds)
        control.ground([("base", [])])
        self.calc_preds = control.solve(on_model=print)
        return self.calc_preds


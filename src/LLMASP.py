import re
import yaml

from openai import OpenAI

from ExecutorHandler import ExecutorHandler
from Evaluator import Evaluator

from typeguard import typechecked
from dataclasses import dataclass, field

from dumbo_asp.primitives.models import Model


@typechecked
@dataclass(frozen=False)
class LLMASP:
    __configFilename: str
    __ragDatabaseFilename: str

    __config: dict = field(init=False)
    __docs_rag: list = field(init=False)
    
    def __post_init__(self):
        self.__config = self.__load_config__(self.__configFilename)
        self.__docs_rag = self.__load_config__(self.__ragDatabaseFilename)

        self.__llm = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio").chat.completions
        
        self.preds = ""
        self.calc_preds = ""


    def __load_config__(self, path: str) -> dict | list:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)
    
    def __gpt_system_start_prompt__(self) -> list:
        res = [{"role": "system", "content": '\n'.join([
            """
                You are a Natural Language to Datalog translator. To translate your
                input to Datalog, you will be asked a sequence of questions. The 
                answers are inside the user input provided with 
                [USER_INPUT]input[/USER_INPUT] and the format is provided with 
                [ANSWER_FORMAT]predicate(terms).[/ANSWER_FORMAT]. Predicate is a 
                lowercase string (possibly including underscores). Terms is a 
                comma-separated list of either double quoted strings or integers. 
                Be sure to control the number of terms in each answer!
                An answer MUST NOT be answered if it is not present in the user input.
                Remember these instructions and don't say anything!
            """.strip() + '\n',])}]
        for prompt, response in self.__docs_rag:
            res.append({"role": "user", "content": f"{self.__pre_input_seasoning__(prompt)}\n["})
            res.append({"role": "system", "content": f"{response}"})
        
        return res
    
    def __to_gpt_user_dict__(self, text: str) -> dict:
        return {"role": "user", "content": text}
 
    def __filter_ASP_atoms__(self, req: str) -> str:
        return " ".join(re.findall(r"\b[a-zA-Z][\w_]*(?:\([^)]*\))?\.", req))

    def __pre_input_seasoning__(self, user_input: str) -> str:
        """
            Enhances the given input with additional information from the config file to help with the ASP atom extraction.
            
            Parameters:
                user_input: str: The input to be seasoned.
                
            Returns:
                str: The seasoned input with added information to help the LLM for ASP atom extraction.
        """

        questions = self.__config['preprocessing']
        the_user_input = f"[USER_INPUT]{user_input}[/USER_INPUT]"
        prompt = ""

        for q in questions:

            q_key, q_value = list(q.items())[0]

            if q_key == '_':
                prompt += f"""
                            Here is some context that you MUST analyze and remember.
                            {q_value}
                            Remember this context and don't say anything!\n
                            """
            else:
                prompt += f"""
                            {the_user_input}
                            {q_key}
                            [ANSWER_FORMAT]{q_value}[/ANSWER_FORMAT]\n
                            """

        return prompt

    def __natural_to_asp__(self, user_input: str) -> str:
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

        chrono = [prompt for prompt in self.__gpt_system_start_prompt__()]
        chrono.append(self.__to_gpt_user_dict__(self.__pre_input_seasoning__(user_input)))

        print("\n".join([f"{i['role']}: {i['content']}" for i in chrono]))

        res =  self.__llm.create(
            model="TheBloke/CodeLlama-7B-Instruct-GGUF/codellama-7b-instruct.Q5_K_M.gguf",
            temperature=0.0,
            messages=chrono,
            stream=False,
        )

        return res.choices[0].message.content
        
    
    def extract_preds(self, user_input: str, TRAIN_ON: bool = False) -> "LLMASP":
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
        
        res = self.__natural_to_asp__(user_input)
        self.preds = self.__filter_ASP_atoms__(res)

        if TRAIN_ON:
            out: str = input(f"Do you want to salve to rag_doc these results: {self.preds}? (y/n): ")

            if out == "y":
                self.__docs_rag.append({"prompt": user_input, "response": self.preds})
                yaml.dump(self.__docs_rag, open(self.__ragDatabaseFilename, "w"))

        return self
    
    def run_asp(self, use_preserved=False) -> "LLMASP":
        """
            Run ASP (Answer Set Programming) solver on the provided ASP code with predicates.
            
            This method initializes an ASP control instance, loads the ASP code from the specified file,
            adds predicates extracted from the user input, grounds the program, and solves it using an ASP solver.

            parameters:
                use_preserved (bool): A flag to determine whether to use the preserved predicates, calculated at each run.
            
            Returns:
                self object: The current LLMASP object with the calculated predicates.
        """
        if (not use_preserved):
            self.calc_preds = Model.of_program(self.__config['knowledge_base'], self.preds, sort=False).as_facts
        else:
            self.calc_preds += Model.of_program(self.__config['knowledge_base'], self.preds + self.calc_preds, sort=False).as_facts

        return self
    
    def get_evaluator(self) -> "Evaluator":
        return Evaluator(self.__config, self.preds, self.calc_preds)



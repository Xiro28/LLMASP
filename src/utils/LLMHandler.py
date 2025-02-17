from typing import List, Type
from ollama import chat
from pydantic import BaseModel, Field

from utils.classBuilder import DynamicLiteralBase

#MODEL_OLLAMA = 'llama3.1'
MODEL_OLLAMA = 'llama3.2:3b-instruct-q8_0'

class LLMHandler:
    def __init__(self, system_prompt: str):

        # not used yet
        assert system_prompt is not None, "The system prompt must not be None."

        self.__llm = chat

    def __to_gpt_user_dict__(self, text: str) -> dict:
        return {"role": "user", "content": text}
    
    def __to_gpt_system_dict__(self, text: str) -> str:
        return {"role": "system", "content": text}
    
    def invoke_llm_constrained(self, prompt: str, class_response: any, accepted_values: list[str] = None, command: str = "") -> dict:
        """
            Invoke the LLM (Large Language Model)

            Parameters:
                prompt (list): The prompt to be used for the LLM.
                temperature (float): The temperature to be used for the LLM. A value between 0.0 (always same response, zero randomness) 
                                     and 1.0 (high creativity, more randomness).

            Returns:
                str: The natural language output generated from the LLM.
        """


        model_json = class_response.model_json_schema()

        # Chain-of-thought
        cot = f"""
            Extract only the relevant information from user_prompt.
            Before producing your final answer, follow these internal steps:
            Reason over the text and identify key entities.
            Determine their relationships and positions.
            Validate your result to ensure it adheres to the schema.
            After these internal steps, output ONLY the final JSON result without showing your internal reasoning.
            
            {command}
            """
        
        print(cot)

        ret_ =  self.__llm(
                model=MODEL_OLLAMA,
                messages=[
                    {
                        "role": "system",
                        "content": cot,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={'temperature': 0.0},
                format=model_json
            )
        
        return class_response.model_validate_json(ret_["message"]["content"])

    def invoke_llm(self, prompts: list, temperature = 0.0) -> dict:
        """
            Invoke the LLM (Large Language Model)

            Parameters:
                prompt (list): The prompt to be used for the LLM.
                temperature (float): The temperature to be used for the LLM. A value between 0.0 (always same response, zero randomness) 
                                     and 1.0 (high creativity, more randomness).

            Returns:
                str: The natural language output generated from the LLM.
        """

        chrono = []

        for p in prompts:
            chrono.append(self.__to_gpt_user_dict__(p))

        completation = self.__llm(
            messages=chrono,
            model=MODEL_OLLAMA,
            options={'temperature': temperature},
        )

        return completation['message']['content']
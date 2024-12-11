from typing import List, Type
from ollama import chat
from pydantic import BaseModel, Field

from utils.classBuilder import DynamicLiteralBase

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
    
    def invoke_llm_constrained(self, prompt: str, class_response: any, link: list[str]) -> dict:
        """
            Invoke the LLM (Large Language Model)

            Parameters:
                prompt (list): The prompt to be used for the LLM.
                temperature (float): The temperature to be used for the LLM. A value between 0.0 (always same response, zero randomness) 
                                     and 1.0 (high creativity, more randomness).

            Returns:
                str: The natural language output generated from the LLM.
        """

        # With this, we improve our performance by providing the model with the expected output.
        if link is not None:
            # this ugly code is needed to get the refernce of the main class used inside the definition of the list class
            # Example: class list_class: List[Class]
            # This cose gets the Class reference, which is useful since we have to rebuild this class with the 
            # partial information found by the reasoning process did before (here's how the link works)
            main_class = class_response.__annotations__[list(class_response.__annotations__.keys())[0]].__args__[0]


            # For the moment the link works by connecting the first parameter of the linked class with the main class
            # So they have to match
            # Example: person(name, age) -> gender(name, gender)
            # The link in that case is the name parameter and both classes have it as the first parameter

            # This will also act as a constraint for the LLM
            # Since there we can control which output we want to get
            # By changing the link list values
            
            # For example, if we don't want to generate Lorenzo, we can just remove it from the list
            # and the LLM will not generate the associated atom

            for i, param in enumerate(main_class.__annotations__.keys()):
                if i == 0:
                    DynamicLiteralBase.add_allowed_values(param, ["Lorenzo"]) # link the classes
                else:
                    DynamicLiteralBase.add_allowed_values(param, "*")

            # create the class with the first parameter containing the partial information
            class_with_partial_info = DynamicLiteralBase.create_model(main_class.__name__)

            linked_class = type(class_response.__name__, (BaseModel,), 
                                {"__annotations__": {class_response.__name__: List[class_with_partial_info]},
                                 class_response.__name__: Field(description=class_response.__extra_info__)
                                })

            class_response = linked_class

        model_json = class_response.model_json_schema()

        ret_ =  self.__llm(
                model=MODEL_OLLAMA,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a world class AI that excels at extracting user data from a sentence. 
                                    Be sure about the relationship between the entities.""",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={'temperature': 0},
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
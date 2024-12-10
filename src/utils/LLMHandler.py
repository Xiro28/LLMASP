from ollama import chat

MODEL_OLLAMA = 'llama3.1'

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
        model_json = class_response.model_json_schema()
        if link is not None:
            model_json["properties"][class_response.__name__]["description"] = f"Just lorenzo"

            print(model_json["properties"][class_response.__name__]["description"])

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
                options={'temperature': 0, "low_vram": True},
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
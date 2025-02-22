from ollama import chat

class LLMHandler:
    def __init__(self, llm_model: str, system_prompt: str) -> None:

        # not used yet
        assert system_prompt is not None, "The system prompt must not be None."
        assert system_prompt is not None, "The system prompt must not be empty."

        self.llm_model = llm_model
        
        self.system_prompt = system_prompt
        self.__llm = chat

    def __to_gpt_dict__(self, role: str, text: str) -> dict:
        return {"role": role, "content": text}
    
    
    def invoke_llm_constrained(self, prompt: str, class_response: any, command: str) -> dict:
        """
            Invoke the LLM (Large Language Model)

            Parameters:
                prompt (str): The prompt to be used for the LLM.

            Returns:
                str: The class filled with the output generated from the LLM.
        """

        model_json = class_response.model_json_schema()

        ret_ =  self.__llm(
                model=self.llm_model,
                messages=[
                    self.__to_gpt_dict__("system", self.system_prompt),
                    self.__to_gpt_dict__("assistant", command),
                    self.__to_gpt_dict__("user", prompt)
                ],
                options={'temperature': 0, "top_k": 5, "top_p": 0.4},
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
            model=self.llm_model,
            options={'temperature': temperature},
        )

        return completation['message']['content']
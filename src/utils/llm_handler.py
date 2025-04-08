from ollama import chat

class LLMHandler:
    def __init__(self, llm_model: str, system_prompt: str) -> None:

        # not used yet
        assert system_prompt is not None, "The system prompt must not be None."
        assert system_prompt is not None, "The system prompt must not be empty."

        self.llm_model = llm_model
        
        self.system_prompt = system_prompt
        self.__llm = chat

        self.CONTEXT_WINDOW = 8192

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

        model_json = None
        if type(class_response) != str:
            model_json = class_response.model_json_schema(mode='serialization')

        _messages = [self.__to_gpt_dict__("system", self.system_prompt), 
        self.__to_gpt_dict__("system", command),
        self.__to_gpt_dict__("user", prompt)]
        
        # If the promp is larger than the contex window, try to chunck it
        """
        if len(user_instructions.split(" ")) > self.CONTEXT_WINDOW:
            for chunck in [prompt[i:i+self.CONTEXT_WINDOW] for i in range(0, len(prompt), self.CONTEXT_WINDOW)]:
                _messages.append(self.__to_gpt_dict__("user", chunck))
        else:
            _messages.append(self.__to_gpt_dict__("user", user_instructions))
        """

        _ret = ""

        # Stream it since large outputs could make Ollama hang
        i = 0
        for chunk in self.__llm(
            model=self.llm_model,
            messages=_messages,
            options={
                'temperature': 0,
                "num_ctx": self.CONTEXT_WINDOW,
                'penalize_newline': True
            },
            format = class_response,
            stream=True
        ):
            _ret += chunk["message"]["content"]
            i = i + 1

            # if we looped more than 65536 (2^16) times means that probably our model is in a loop of generation.
            # Return empty so we won't fill our set of generated atoms with bad atoms
            if i > 8196:
                ## TODO: Put a real check to see if we are in a loop
                print("Exceeded output limit:", _ret)
                return None

        print(_ret)

        if model_json is not None:
            return class_response.model_validate_json(_ret)
        return _ret

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

        chrono = [self.__to_gpt_dict__("system", self.system_prompt)]

        for p in prompts:
            chrono.append(self.__to_gpt_dict__("user", p))

        completation = self.__llm(
            messages=chrono,
            model=self.llm_model,
            options={'temperature': temperature},
        )

        return completation['message']['content']
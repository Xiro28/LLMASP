from g4f import ChatCompletion, Provider
from g4f.cookies import load_cookies_from_browsers

from openai import OpenAI

import instructor
from utils.customInstructor import CustomInstructor

USE_GEMINI_FLAG = True

class LLMHandler:
    def __init__(self, system_prompt: str):

        assert system_prompt is not None, "The system prompt must not be None."

        self.__system_prompt = system_prompt

        if USE_GEMINI_FLAG:
            # Gemini API have custom instructor based on asking specific questions

            print("Using Gemini API")

            load_cookies_from_browsers(".google.com")
            self.__llm = ChatCompletion
            self.__llm_constrained = CustomInstructor(self.__llm)

        else:
            # Custom Model will use LLAMA.cpp and grammar checker

            self.__llm = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio").chat.completions
            self.__llm_constrained = instructor.patch(OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")).chat.completions


    def __to_gpt_user_dict__(self, text: str) -> dict:
        return {"role": "user", "content": text}
    
    def __to_gpt_system_dict__(self, text: str) -> str:
        return {"role": "system", "content": text}
    
    def invoke_llm_constrained(self, prompt: str, class_response: any) -> dict:
        """
            Invoke the LLM (Large Language Model)

            Parameters:
                prompt (list): The prompt to be used for the LLM.
                temperature (float): The temperature to be used for the LLM. A value between 0.0 (always same response, zero randomness) 
                                     and 1.0 (high creativity, more randomness).

            Returns:
                str: The natural language output generated from the LLM.
        """

        print(class_response[1])

        if USE_GEMINI_FLAG:
            return self.__llm_constrained.create(
                response_model=class_response[1],
                message=self.__to_gpt_user_dict__(prompt)
            )


        return self.__llm_constrained.create(
            model="TheBloke/CodeLlama-7B-Instruct-GGUF",
            max_tokens=1024,
            response_model=class_response[1],
            messages=[self.__to_gpt_user_dict__(prompt)],
            stream=False)

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

        chrono = [self.__to_gpt_system_dict__(self.__system_prompt)]

        for p in prompts:
            chrono.append(self.__to_gpt_user_dict__(p))

        if USE_GEMINI_FLAG:
            return self.__llm.create(
                model="gpt-3.5-turbo",
                provider=Provider.Gemini,
                temperature=temperature,
                seed=0,
                messages=chrono,
                stream=False)
        else:
            return self.__llm.create(
                model="TheBloke/CodeLlama-7B-Instruct-GGUF",
                temperature=temperature,
                messages=chrono,
                seed=0,
                stream=False).choices[0].message.content
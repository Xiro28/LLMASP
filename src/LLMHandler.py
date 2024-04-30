from g4f import ChatCompletion, Provider
from g4f.cookies import load_cookies_from_browsers

from openai import OpenAI

USE_GEMINI_FLAG = True

class LLMHandler:
    def __init__(self, system_prompt: str):

        assert system_prompt is not None, "The system prompt must not be None."

        self.__system_prompt = system_prompt

        if USE_GEMINI_FLAG:
            load_cookies_from_browsers(".google.com")
            self.__llm = ChatCompletion

            print("Using Gemini API.")
        else:
            self.__llm = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio").chat.completions

    def __to_gpt_user_dict__(self, text: str) -> dict:
        return {"role": "user", "content": text}
    
    def __to_gpt_system_dict__(self, text: str) -> dict:
        return {"role": "system", "content": text}

    def invoke_llm(self, prompt: list, temperature = 0.0) -> dict:
        """
            Invoke the LLM (Large Language Model)

            Parameters:
                system_prompt (str): The system prompt to be used for the LLM.
                prompt (list): The prompt to be used for the LLM.
                temperature (float): The temperature to be used for the LLM. A value between 0.0 (same response, zero randomness) 
                                     and 1.0 (high creativity, more randomness).

            Returns:
                dict: The natural language output generated from the LLM.
        """

        chrono = [self.__to_gpt_system_dict__(self.__system_prompt)]

        for p in prompt:
            chrono.append(self.__to_gpt_user_dict__(p))

        if USE_GEMINI_FLAG:
            return self.__llm.create(
                model="gpt-3.5-turbo",
                provider=Provider.Gemini,
                temperature=temperature,
                messages=chrono,
                stream=False)
        else:
            return self.__llm.create(
                model="TheBloke/CodeLlama-7B-Instruct-GGUF/codellama-7b-instruct.Q5_K_M.gguf",
                temperature=temperature,
                messages=chrono,
                stream=False).choices[0].message.content
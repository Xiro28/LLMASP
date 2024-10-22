from openai import OpenAI
from g4f import ChatCompletion, Provider
from g4f.cookies import load_cookies_from_browsers
from utils.customInstructor import CustomInstructor


import ollama
import instructor


USE_GEMINI_FLAG = False
MODEL_OLLAMA = 'llama3.1'

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

            self.__llm = OpenAI(
                            base_url="http://localhost:11434/v1",
                            api_key="ollama",
                        )
            self.__llm_constrained = instructor.from_openai(self.__llm, mode=instructor.Mode.JSON)

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

        if USE_GEMINI_FLAG:
            return self.__llm_constrained.create(class_response, self.__to_gpt_user_dict__(prompt))

        print(class_response)
        return self.__llm_constrained.chat.completions.create(
                model=MODEL_OLLAMA,
                temperature=0.0,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a world class AI that excels at extracting user data from a sentence.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                response_model=class_response,
            )

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
            completation = self.__llm.chat.completions.create(
                model=MODEL_OLLAMA,
                temperature=temperature,
                messages=chrono,
                seed=0
            )

            return completation.choices[0].message.content
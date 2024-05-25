from g4f import ChatCompletion, Provider
from typeguard import typechecked
from dataclasses import dataclass


"""
    This is intended to be used with free model from g4f since they don't support grammar directed output
    It's also a trade-off between precision and speed since grammar still slows down a lot the inference
"""
class CustomInstructor:
    
    def __init__(self, _llm):
        self._llm = _llm

    def create(self, response_model, message):

        members = ''
        for m in dir(response_model):
            if not callable(getattr(response_model, m)):
                members += str(m) + ' '

        print(members)

        _sysPrompt = {'role': 'system', 'content': f"""You are a query executor.
                           Follow this schema:
                           Given a user phrase, exctract those [""" + members + """] from the user message.
                           The output has to be inside [] and it has to be a list of a list of elements."""}
        
        print(_sysPrompt)
        
        out = self._llm.create(
                model="gpt-3.5-turbo",
                provider=Provider.Gemini,
                temperature=0.0,
                seed=0,
                messages=[_sysPrompt, message],
                stream=False)
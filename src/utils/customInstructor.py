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
        for m in response_model[1].__dict__:
            if '__' not in m:
                members += str(m) + ' '

        _sysPrompt = {'role': 'system', 'content': \
                          f"""You are a query executor and you have to extract specific elements from the user message.
                           Query: """ + message['content'].split('.')[0] +"""
                           exctract:""" + members + """
                           context: """ + response_model[0] + """
                           The output has to be inside [] and it has to be a tuple of elements.
                           Don't format the string! Just return the elements separated by commas.
                           if the information is not present in the user message return: None.
                           Exact follow those instruction without saying anything else!"""}
        
        out = self._llm.create(
                model="gpt-3.5-turbo",
                provider=Provider.Gemini,
                temperature=0.0,
                seed=0,
                messages=[_sysPrompt],
                stream=False)
        
        print(out)

        if '[' in out or ']' in out:
            filtered = out.split('[')[1].split(']')[0]
        else:
            return "None"

        ## ADD output control here

        return filtered
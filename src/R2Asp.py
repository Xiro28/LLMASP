import valasp
import g4f
import yaml

class R2Asp:
    
    def __init__(self):
        self.config = self.__loadConfig__("config.yml")

    def __loadConfig__(self, path: str) -> dict:
        return yaml.load(open(path, "r"), Loader=yaml.Loader)
   
    def __userInputToGPT__(self, text: str) -> dict:
        return {"role": "user", "content": text}
    
    def __getCodeFromResponse__(self, response: str) -> str:
        return response[
            response.find("```") + 3:
            response.rfind("```")
            ]

    def __cleanOutputRequest__(self, req: str) -> str:
        if "```" in req :
            req = self.getCodeFromResponse(req)
        if 'asp\n' in req:
            req = req.replace('asp', '')
        return req

    def __request_body__(self, user_input: str) -> dict:
            if user_input is None:
                inputs = [x.split('(')[0] for x in self.config['predicates']['input']]
                requests = [self.config['arguments'][x]['request'] for x in inputs]
                data_types = [self.config['arguments'][x]['data_type'] for x in inputs]

                return self.__userInputToGPT__(
                    f"{requests[0]} and answer with that structure (ASP atoms):"
                    f"{self.config['predicates']['input'][0]} with the following types {data_types[0]}.\n"
                    f"You MUSTN'T provide the explanation of the output"
                )

            return self.__userInputToGPT__(f"{self.config['extract_value']} from this '{user_input}' (in ASP atom) with this structure:\n"
                                f"{self.config['predicates']['user_request'][0]}.\n"
                                f"You MUSTN'T provide the explanation of the output")

    def __makeRequest__(self, user_input: str) -> tuple:
        return (g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            provider=g4f.Provider.Gemini,
            messages=[self.request_body(None)],
            stream=False,
        ), g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            provider=g4f.Provider.Gemini,
            messages=[self.request_body(user_input)],
            stream=False,
        ))


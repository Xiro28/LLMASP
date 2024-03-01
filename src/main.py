import valasp
import g4f
import yaml

def userInputToGPT(text: str) -> dict:
    return {"role": "user", "content": text}

def loadConfig(path: str) -> dict:
    return yaml.load(open(path, "r"), Loader=yaml.Loader)

def request_body(user_input: str, config: dict) -> dict:
    if user_input is None:
        inputs = [x.split('(')[0] for x in config['predicates']['input']]
        requests = [config['arguments'][x]['request'] for x in inputs]
        data_types = [config['arguments'][x]['data_type'] for x in inputs]

        return userInputToGPT(
            f"{requests[0]} and answer with that structure (ASP atoms):"
            f"{config['predicates']['input'][0]} with the following types {data_types[0]}.\n"
            f"You MUSTN'T provide the explanation of the output"
        )

    return userInputToGPT(f"{config['extract_value']} from this '{user_input}' (in ASP atom) with this structure:\n"
                          f"{config['predicates']['user_request'][0]}.\n"
                          f"You MUSTN'T provide the explanation of the output")


def makeRequest(user_input: str, config: dict) -> tuple:
    return (g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        provider=g4f.Provider.Gemini,
        messages=[request_body(None, config)],
        stream=False,
    ), g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        provider=g4f.Provider.Gemini,
        messages=[request_body(user_input, config)],
        stream=False,
    ))


def getCodeFromResponse(response: str) -> str:
    return response[
           response.find("```") + 3:
           response.rfind("```")
           ]

def cleanOutputRequest(req: str) -> str:
    if "```" in req :
        req = getCodeFromResponse(req)
    if 'asp' in req:
        req = req.replace('asp', '')
    return req

def main():
    config = loadConfig("config.yml")
    req = makeRequest(input("Enter message to be converted to ASP:\n"), config)
    code = cleanOutputRequest(req[0]) + cleanOutputRequest(req[1])
    print(code)


if __name__ == "__main__":
    main()

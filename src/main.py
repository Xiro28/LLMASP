from openai import OpenAI


def loadAPI() -> str:
    import json

    json_loaded = json.load(open("config/api_key.json"))

    if 'api' not in json_loaded.keys() or json_loaded['api'] is None:
        raise Exception("API key not valid: config/api_key.json")

    return json_loaded['api']


def userInputToGPT(text: str) -> dict:
    return {"role": "user", "content": text}


def request_body(user_input: str) -> dict:
    return userInputToGPT(
        f"With the following user input [{user_input}] " +
        "Using your knowlage about ASP, extract the following information:" +
        "Atoms and function" +
        "Make sure that all the functions are with the same ariety when called" +
        "Once you extracted the ASP atoms and functions, give the whole ASP program" +
        "Without adding further information"
    )


def createGPT() -> "OpenAI.completions":
    API_KEY = loadAPI()
    return OpenAI(api_key=API_KEY).chat.completions


def makeRequest(client_gpt: "OpenAI.completions", user_input: str) -> str:
    return client_gpt.create(
        model="gpt-3.5-turbo",
        messages=request_body(user_input),
        temperature=1.0  # 0.0 - 2.0
    ).choices[0].message


def main():
    client_gpt = createGPT()
    makeRequest(client_gpt, input("Enter message to be converted to ASP"))


if __name__ == "__main__":
    main()

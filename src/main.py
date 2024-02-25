
def loadAPI():
    import json

    json_loaded = json.load(open("config/api_key.json"))

    if 'api' not in json_loaded.keys():
        raise Exception("No api key found in config/api_key.json")

    return json_loaded['api']


def main():
    print(loadAPI())


if __name__ == "__main__":
    main()

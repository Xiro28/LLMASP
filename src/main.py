from LLMASP import LLMASP

def main():
    
    _instance = LLMASP("./restaurant_example/config.yml")

    while True:
        out = _instance.extract_preds(input("Enter message to be converted to ASP:\n"), False)\
            .run_asp(use_preserved=False)
        print(out.get_evaluator().get_natural_output())


if __name__ == "__main__":
    main()

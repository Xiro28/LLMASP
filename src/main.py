from outputHandlers.evaluateOutput import EvaluateOuput
from inputHandlers.evaluateInput import EvaluateInput
from LLMASP import LLMASP

def main():
    
    _instance = LLMASP("restaurant_example/config.yml")

    while True:
        out = _instance.infer(EvaluateInput).run_asp()
        print(out._as(EvaluateOuput).run())


if __name__ == "__main__":
    main()

import time
import json

from outputHandlers.evaluateOutput import EvaluateOuput
from inputHandlers.evaluateInput import EvaluateInput
from LLMASP import LLMASP

def main():
    
    _dataset = json.load(open("./src/dataset.json", "r"))
    f = open("./src/output.txt", "w")
    
    time_start = time.time()
    
    lines = ""
    problems_solved = 0

    for obj in _dataset:

        yaml : str = obj["problem_name"].replace(" ", "") 

        _instance = LLMASP(f"./src/applications/{yaml}.yml")
        out = _instance.infer(EvaluateInput, obj["text"]).preds
        lines += out + "\n" + obj["output"] + "\n\n"
 
        print(f"Story {problems_solved} done. {out}, \n{time.time() - time_start}")

        f.seek(0)
        f.write(lines)

        problems_solved += 1
    
    f.seek(0)
    f.write(lines)
    f.write(f"Time taken: {time.time() - time_start}")
    f.close()
    

if __name__ == "__main__":
    main()



from llmasp import LLMASP

import json

# models: llama3.2:3b-instruct-q8_0

def main():
    _dataset = json.load(open("./dataset.json", "r"))
    f = open("./test_with_default_none.txt", "w")

    for problem_n, obj in enumerate(_dataset):

        #if problem_n <= 138:
        #    continue

        #if obj["problem_name"] != "VisitAll":
        #    continue

        yaml : str = obj["problem_name"].replace(" ", "") 

        _instance = LLMASP(f"applications/{yaml}.yml", 'llama3.1:8b')
        out = _instance.infer(obj["text"], obj["format"]).preds + "\n"

        print(f"Problem N {problem_n} done. Output: {out}")

        f.write(out)

    f.close()

    
    

if __name__ == "__main__":
    main()



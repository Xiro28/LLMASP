from llmasp import LLMASP

import json

# models: llama3.2:3b-instruct-q8_0

def main():
    _dataset = json.load(open("./dataset.json", "r"))
    f = open("./output.txt", "w")

    for problem_n, obj in enumerate(_dataset):

        yaml : str = obj["problem_name"].replace(" ", "") 

        _instance = LLMASP(f"applications/{yaml}.yml", 'qwen2.5:1.5b-instruct-q8_0')
        out = _instance.infer(obj["text"]).preds + "\n" #+ obj["output"] + "\n\n"

        print(f"Problem N {problem_n} done. Output: {out}")

        f.write(out)

    f.close()

    
    

if __name__ == "__main__":
    main()



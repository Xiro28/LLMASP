from llmasp import LLMASP

import json

# models: llama3.2:3b-instruct-q8_0
FEW_SAMPLE_MODE = True

def main():

    _dataset = json.load(open("./dataset.json", "r"))
    f = open("./test_csv.txt", "w")

    _new_dataset = []

    if FEW_SAMPLE_MODE:
        samples = 6
        current_problem = "None"
        for obj in _dataset:
            if samples > 0:
                current_problem = obj["problem_name"]
                _new_dataset.append(obj)
                samples -= 1
            elif samples <= 0:
                if current_problem == obj["problem_name"]:
                    _new_dataset.append(None)
                    continue

                samples = 5
                _new_dataset.append(obj)
    else:
        _new_dataset = _dataset

    
    current_problem = None

    for problem_n, obj in enumerate(_new_dataset):

        if obj is None:
            f.write("\n")
            continue

        if current_problem != obj["problem_name"]:
            current_problem = obj["problem_name"]
            yaml : str = obj["problem_name"].replace(" ", "") 
            _instance = LLMASP(f"applications/{yaml}.yml", "behaviour/v4_csv.yml", 'llama3.2:3b-instruct-q8_0', "llama3.2:3b-instruct-q8_0")

        #if current_problem != "Valves Location Problem":
        #    f.write("\n")
        #    continue

        #if problem_n <= 0:
        #    continue

        out = _instance.infer(obj["text"], obj["format"]).preds + "\n"
        print(f"Problem N {problem_n} done. Output: {out}")

        f.write(out)
        f.flush()

    f.close()

    
    

if __name__ == "__main__":
    main()



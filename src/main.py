from llmasp import LLMASP

import json

mode = "json"
llm_model = "llama3.1:8b"
use_problem_description = False
solve_single_problem_batch_name = ""

configurations = {
    "tsv": "behaviour/v4_tsv.yml",
    "json": "behaviour/v4.json.yml"
}


FEW_SAMPLE_MODE = False

def main():

    _dataset = json.load(open("./dataset.json", "r"))
    f = open("./temp.txt", "w")

    _new_dataset = []

    if FEW_SAMPLE_MODE:
        samples = 6
        current_problem_name = "None"
        for obj in _dataset:
            if samples > 0:
                current_problem_name = obj["problem_name"]
                _new_dataset.append(obj)
                samples -= 1
            elif samples <= 0:
                if current_problem_name == obj["problem_name"]:
                    _new_dataset.append(None)
                    continue

                samples = 5
                _new_dataset.append(obj)
    else:
        _new_dataset = _dataset

    
    current_problem_name = None

    for problem_n, obj in enumerate(_new_dataset):

        if obj is None:
            f.write("\n")
            continue

        if current_problem_name != obj["problem_name"]:
            current_problem_name = obj["problem_name"]
            yaml : str = current_problem_name.replace(" ", "") 
            llmasp_instance: "LLMASP" = LLMASP(f"applications/{yaml}.yml", configurations[mode], llm_model)

        if solve_single_problem_batch_name != "" and current_problem_name != solve_single_problem_batch_name:
            f.write("\n")
            continue

        if use_problem_description:
            out = llmasp_instance.infer(obj["text"], f"{obj["description"]}{obj["format"]}", mode).extracted_preds + "\n"
        else:
            out = llmasp_instance.infer(obj["text"], obj["format"], mode).extracted_preds + "\n"

        f.write(out)
        f.flush()

    f.close()

    
    

if __name__ == "__main__":
    main()



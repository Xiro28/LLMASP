from llmasp import LLMASP

import json
from check_validity import check_validity
import utils

# models: llama3.2:3b-instruct-q8_0
FEW_SAMPLE_MODE = 3

"""
    Set the mode for the input handler.
    
    This method allows you to set the mode of the input handler, which determines how the input will be processed.
    The available modes are:
        - "single_cot": Single-step reasoning with chain of thought.
        - "single_no_reason": Single-step reasoning without chain of thought.
        - "multi_no_reason": Multi-step reasoning without chain of thought.
        - "multi_no_reason_csv": Multi-step reasoning without chain of thought, output in CSV format.
        - "multi_no_reason_atom": Multi-step reasoning without chain of thought, output in atom format.
        
    Parameters:
        mode (str): The mode to set for the input handler.
"""


def main(mode, full_description=False):

    _dataset = json.load(open("./dataset.json", "r"))
    f = open("./temp.txt", "w")

    yaml_to_load = {"single_cot": "behaviour/v4_2.yml",
                   "single_no_reason": "behaviour/v4_2.yml",
                   "multi_no_reason": "behaviour/v4_2.yml",
                   "multi_no_reason_csv": "behaviour/v4_csv.yml",
                   "single_no_reason_csv": "behaviour/v4_csv_2_no_examples.yml",
                   "single_no_grammar": "behaviour/v4_originale.yml",
                   }

    _new_dataset = []

    if FEW_SAMPLE_MODE > 0:
        samples = FEW_SAMPLE_MODE
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

                samples = FEW_SAMPLE_MODE
                _new_dataset.append(obj)
    else:
        _new_dataset = _dataset

    
    current_problem = None

    #take also the time of execution
    import time
    start_time = time.time()


    for problem_n, obj in enumerate(_new_dataset):

        if obj is None:
            f.write("\n")
            continue

        if current_problem != obj["problem_name"]:
            current_problem = obj["problem_name"]
            yaml : str = obj["problem_name"].replace(" ", "") 
            _instance = LLMASP(f"applications/{yaml}.yml", yaml_to_load[mode], 'llama3.1', "llama3.1")
            _instance.set_mode(mode)

            

        #if current_problem != "Ricochet Robots":
        #    f.write("\n")
        #    continue

        #if problem_n <= 128:
        #    continue

        if full_description:
            out = _instance.infer(f"{obj["text"]}", f"{obj["description"]}{obj["format"]}").preds + "\n"
        else:
            out = _instance.infer(f"{obj["text"]}", f"{obj["format"]}").preds + "\n"
       
        print(f"Problem N {problem_n} done. Output: {out}")

        
        print(f"Tokens used: {utils.llm_handler.total_tokens}")

        f.write(out)
        f.flush()
    
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")

    check_validity(mode=mode, graph_name=mode, time=end_time - start_time, full_description=full_description, tokens=utils.llm_handler.total_tokens)
    f.close()
    utils.llm_handler.total_tokens = 0
    
    

if __name__ == "__main__":
    #clean the validation file
    open("./validity_results.txt", "w").close()

    tests = [
             #"single_cot", 
             #"single_no_reason", 
             #"multi_no_reason", 
             #"multi_no_reason_csv",
             "single_no_reason_csv",
             #"multi_no_grammar",
             #"single_no_grammar"
             ]

    for mode in tests:
        print(f"Running mode: {mode}")
        main(mode, False)
    
    print("Starting test with problem description and format")
    for mode in tests:
        print(f"Running mode: {mode}")
        main(mode, True)



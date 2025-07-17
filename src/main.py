from llmasp import LLMASP

import json

# models: llama3.2:3b-instruct-q8_0
FEW_SAMPLE_MODE = 3

def main():

    _dataset = json.load(open("./dataset.json", "r"))
    f = open("./test_csv_3_2.txt", "w")

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

    example_prompt, example_output = None, None

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
            _instance = LLMASP(f"applications/{yaml}.yml", "behaviour/v4_csv_2.yml", 'llama3.1', "llama3.1")
            example_prompt = obj["text"]
            example_output = obj["output"]

            

        #if current_problem != "Ricochet Robots":
        #    f.write("\n")
        #    continue

        #if problem_n <= 128:
        #    continue

        _instance.set_mode("")
        out = _instance.infer(f"{obj["text"]}", f"{obj["description"]}{obj["format"]}").preds + "\n"
        #out = _instance.infer(f"{obj["text"]}", f"{obj["format"]}").preds + "\n"
        print(f"Problem N {problem_n} done. Output: {out}")

        f.write(out)
        f.flush()
    
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")

    f.close()

    
    

if __name__ == "__main__":
    main()



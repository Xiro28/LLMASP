import json

with open("./output.txt", "r") as f:
    output = f.readlines()

_dataset = json.load(open("./dataset.json", "r"))

TP_total = 0
FP_total = 0
FN_total = 0
TN_total = 0 

problem_acc = {}
i = 0  

for problem in _dataset:
    name = problem["problem_name"]
    expected_atoms = problem["output"]

    if i >= len(output):
        print(f"Warning: 'output' is exhausted at problem {name}")
        break

    expected_line = output[i].strip()
    i += 3
    
    if ") " in expected_atoms:
        expected_atoms = expected_atoms.replace(") ", "). ")
        print(expected_atoms.split("."))

    predicted_atoms = [atom.strip().replace(" ", "")  for atom in expected_line.split(".") if atom.strip()]
    expected_atoms = [atom.strip().replace(" ", "") 
                       for atom in expected_atoms.split(".") if atom.strip()]

    if name not in problem_acc:
        problem_acc[name] = {
            "TP": 0, "FP": 0, "FN": 0, 
            "accuracy": 0.0, "f1": 0.0
        }

    tp = 0
    fp = 0

    set_expected = set(expected_atoms)
    set_predicted = set(predicted_atoms)

    tp = len(set_expected.intersection(set_predicted))
    fp = len(set_predicted - set_expected)
    fn = len(set_expected - set_predicted)

    TP_total += tp
    FP_total += fp
    FN_total += fn

    problem_acc[name]["TP"] += tp
    problem_acc[name]["FP"] += fp
    problem_acc[name]["FN"] += fn

for name, stats in problem_acc.items():
    print(f"Problem: {name}")

    tp = stats["TP"]
    fp = stats["FP"]
    fn = stats["FN"]

    print(f"  TP: {tp}")
    print(f"  FP: {fp}")
    print(f"  FN: {fn}")

    denom = tp + fp + fn
    accuracy = (tp / denom) if denom else 0.0

    denom_f1 = (2 * tp + fp + fn)
    f1 = (2 * tp / denom_f1) if denom_f1 else 0.0

    print(f"  Accuracy: {accuracy:.3f}")
    print(f"  F1: {f1:.3f}")
    print("-----")

denom_global = TP_total + FP_total + FN_total
global_accuracy = (TP_total / denom_global) if denom_global else 0.0
global_f1 = (2 * TP_total) / (2 * TP_total + FP_total + FN_total) if (2*TP_total + FP_total + FN_total) else 0.0

print("Global metrics:")
print(f"  Accuracy: {global_accuracy:.3f}")
print(f"  F1:       {global_f1:.3f}")
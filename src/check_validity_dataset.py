# to check the validity of a result of a prompt 
# we have to check: len(result) == len(expected_result)
# and for each element in result we have to check if they are equal

from matplotlib import pyplot as plt
from rapidfuzz import process
from termcolor import colored
import difflib

import json

def find_closest_match(element, target_string):
    # Split the target string into individual entities
    entities = target_string
    entities = [entity.strip() for entity in entities]

    # Find the closest match
    match, score, _ = process.extractOne(element, entities)
    return match, score

def highlight_differences(wrong, correct):
    diff = difflib.ndiff(wrong, correct)
    highlighted = []
    for char in diff:
        if char.startswith('-'):
            highlighted.append(colored(char[2:], 'red'))  # Wrong character
        elif char.startswith('+'):
            highlighted.append(colored(char[2:], 'green'))  # Correct character
        elif not char.startswith((' ', '?')):  # Skip the '?' line
            highlighted.append(char[2:])
        else:
            highlighted.append(char[2:])  # Unchanged character
    return ''.join(highlighted)

with open("output.txt", "r") as f:
    output = f.readlines()

_dataset = json.load(open("./dataset.json", "r"))

# Global counters (if you also want overall metrics)
TP_total = 0
FP_total = 0
FN_total = 0
TN_total = 0  # Typically 0 if you're not counting "negative" space

problem_acc = {}
i = 0  # index for reading lines from output

for problem in _dataset:
    name = problem["problem_name"]
    predicted_output = problem["output"]  # your model’s output

    # Safeguard: check if `i` is still within the `output` list
    if i >= len(output):
        print(f"Warning: 'output' is exhausted at problem {name}")
        break

    # If you only have **one line** of expected output per problem:
    expected_line = output[i].strip()
    i += 3
    
    if ") " in predicted_output:
        predicted_output = predicted_output.replace(") ", "). ")
        print(predicted_output.split("."))

    # Split into atoms, removing empty or purely whitespace entries
    expected_atoms = [atom.strip() for atom in expected_line.split(".") if atom.strip()]
    predicted_atoms = [atom.strip().replace(" ", "") 
                       for atom in predicted_output.split(".") if atom.strip()]

    # Initialize dictionary for this problem if needed
    if name not in problem_acc:
        problem_acc[name] = {
            "TP": 0, "FP": 0, "FN": 0, 
            "accuracy": 0.0, "f1": 0.0
        }

    # Compute local TP, FP, FN
    tp = 0
    fp = 0

    # You can use sets if you only care about *unique* atoms; 
    # or you can do a list-based approach if duplicates matter.
    # Here, let’s do a set-based approach for clarity:
    set_expected = set(expected_atoms)
    set_predicted = set(predicted_atoms)

    tp = len(set_expected.intersection(set_predicted))
    fp = len(set_predicted - set_expected)
    fn = len(set_expected - set_predicted)

    # Update global counters
    TP_total += tp
    FP_total += fp
    FN_total += fn

    # Save per-problem results
    problem_acc[name]["TP"] += tp
    problem_acc[name]["FP"] += fp
    problem_acc[name]["FN"] += fn

# Print each problem’s metrics
for name, stats in problem_acc.items():
    print(f"Problem: {name}")
    print(f"  TP: {stats['TP']}")
    print(f"  FP: {stats['FP']}")
    print(f"  FN: {stats['FN']}")

    tp = stats["TP"]
    fp = stats["FP"]
    fn = stats["FN"]

    denom = tp + fp + fn
    accuracy = (tp / denom) if denom else 0.0

    # Compute single-problem F1
    denom_f1 = (2 * tp + fp + fn)
    f1 = (2 * tp / denom_f1) if denom_f1 else 0.0

    print(f"  Accuracy: {accuracy}")
    print(f"  F1: {f1}")
    print("-----")

# If you also want overall accuracy / F1 across all problems (micro-average):
denom_global = TP_total + FP_total + FN_total
global_accuracy = (TP_total / denom_global) if denom_global else 0.0
global_f1 = (2 * TP_total) / (2 * TP_total + FP_total + FN_total) if (2*TP_total + FP_total + FN_total) else 0.0

print("Global metrics:")
print(f"  Accuracy: {global_accuracy:.3f}")
print(f"  F1:       {global_f1:.3f}")
import json
import matplotlib.pyplot as plt
import numpy as np

def check_validity(time=None, mode=None, graph_name=None, full_description=False, tokens=None):
    with open("./temp.txt", "r") as f:
        output = f.readlines()

    _dataset = json.load(open("./dataset.json", "r"))

    TP_total = 0
    FP_total = 0
    FN_total = 0
    TN_total = 0 

    problem_acc = {}
    i = 0  

    _new_dataset = []

    FEW_SAMPLE_MODE = 0
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

                samples = FEW_SAMPLE_MODE - 1
                _new_dataset.append(obj)
    else:
        _new_dataset = _dataset


    for problem in _new_dataset:
        
        if problem is None:
            i += 1
            continue

        name = problem["problem_name"]
        expected_atoms = problem["output"].lower()

        #if name != "Stable Marriage":
        #    continue

        if i >= len(output):
            print(f"Warning: 'output' is exhausted at problem {name}")
            break

        expected_line = output[i].strip()
        i += 1
        
        if ") " in expected_atoms:
            expected_atoms = expected_atoms.replace(") ", "). ")
            #print(expected_atoms.split("."))

        predicted_atoms = [atom.strip().replace(" ", "").lower()  for atom in expected_line.split(".") if atom.strip()]
        expected_atoms = [atom.strip().replace(" ", "").lower() 
                        for atom in expected_atoms.split(".") if atom.strip()]

        #print("ATOMS")
        #print(predicted_atoms, expected_atoms)

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

    problem_names = []
    accuracies = []
    f1_scores = []

    for name, stats in problem_acc.items():
        print(f"Problem: {name}")

        if name == "VisitAll":
            break

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

        problem_names.append(f"{name}\nACC:{accuracy:.3f}\nF1:{f1:.3f}")
        accuracies.append(accuracy)
        f1_scores.append(f1)

    denom_global = TP_total + FP_total + FN_total
    global_accuracy = (TP_total / denom_global) if denom_global else 0.0
    global_f1 = (2 * TP_total) / (2 * TP_total + FP_total + FN_total) if (2*TP_total + FP_total + FN_total) else 0.0

    print("Global metrics:")
    print(f"  Accuracy: {global_accuracy:.3f}")
    print(f"  F1:       {global_f1:.3f}")
    print(f"  TP:      {TP_total}")
    print(f"  FP:      {FP_total}")
    print(f"  FN:      {FN_total}")

    description = "descr" if full_description else "no_descr"
    with open("validity_results.txt", "a") as f:
        f.write("Tokens in output: " + str(tokens) + "\n")
        f.write("Time taken: " + str(time) + "\n")
        f.write("Global metrics for " + mode + description + ":\n")
        f.write(f"  Accuracy: {global_accuracy:.3f}\n")
        f.write(f"  F1:       {global_f1:.3f}\n")
        f.write(f"  TP:      {TP_total}\n")
        f.write(f"  FP:      {FP_total}\n")
        f.write(f"  FN:      {FN_total}\n\n")

        for name, stats in problem_acc.items():
            tp = stats["TP"]
            fp = stats["FP"]
            fn = stats["FN"]
            denom_local = tp + fp + fn
            accuracy = (tp / denom_local) if denom_local else 0.0
            f1 = (2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) else 0.0

            f.write(f"Problem: {name}\n")
            f.write(f"  TP: {tp}\n")
            f.write(f"  FP: {fp}\n")
            f.write(f"  FN: {fn}\n")
            f.write(f"  Accuracy: {accuracy:.3f}\n")
            f.write(f"  F1: {f1:.3f}\n\n")


    # Creiamo lo Spider Plot
    categories = problem_names
    N = len(categories)

    # Creiamo un array per i valori di accuratezza e f1_score
    accuracies_values = accuracies
    f1_values = f1_scores

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()

    # Assicuriamoci che il grafico chiuda il cerchio
    accuracies_values += accuracies_values[:1]
    f1_values += f1_values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), dpi=800, subplot_kw=dict(polar=True))

    threshold = 0.5
    angles_full = np.linspace(0, 2 * np.pi, 100)
    ax.plot(angles_full, [threshold]*len(angles_full), color='red', linestyle='--', linewidth=2, label='Threshold 0.5')


    #ax.fill(angles, accuracies_values, color='orange', alpha=0.25, label="Accuracy")
    ax.fill(angles, f1_values, color='blue', alpha=0.25, label="F1 Score")

    #ax.plot(angles, accuracies_values, color='orange', linewidth=2)
    ax.plot(angles, f1_values, color='blue', linewidth=2, )

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, rotation=45, ha="center")

    ax.set_ylim(0, 1)

    # Sposta ulteriormente le etichette lontano dal grafico
    ax.tick_params(axis='x', pad=40)  # Modifica 'pad' per controllare la distanza


    plt.title("Spider Plot of Accuracy and F1 Scores for Each Problem", size=15)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    plt.tight_layout()
    if graph_name:
        plt.savefig(graph_name + description + ".png", dpi=800)
    else:
        plt.savefig("spider_plot.png", dpi=800)

if __name__ == "__main__":
    check_validity()
    print("Spider plot saved as 'spider_plot.png'.")
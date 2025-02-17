# to check the validity of a result of a prompt 
# we have to check: len(result) == len(expected_result)
# and for each element in result we have to check if they are equal

from matplotlib import pyplot as plt
from rapidfuzz import process
from termcolor import colored
import difflib

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
#print(output)
##with open("stories.txt", "r") as f:
#    expected_output = f.readlines()

expected_output = ["in_layer(0,n1). in_layer(0,n10). in_layer(0,n2). in_layer(0,n3). in_layer(0,n4). in_layer(0,n5). in_layer(0,n6). in_layer(0,n7). in_layer(1,n11). in_layer(1,n12). in_layer(1,n13). in_layer(1,n14). in_layer(1,n15). in_layer(1,n16). in_layer(1,n17). in_layer(1,n18). in_layer(2,n21). in_layer(2,n22). in_layer(2,n23). in_layer(2,n24). in_layer(2,n25). in_layer(2,n26). in_layer(2,n27). in_layer(2,n28). in_layer(3,n31). in_layer(3,n32). in_layer(3,n33). in_layer(3,n34). in_layer(3,n35). in_layer(3,n36). in_layer(3,n37). in_layer(3,n38). width(0,8). width(1,8). width(2,8). width(3,8). edge(n1,n20). edge(n10,n13). edge(n10,n19). edge(n11,n22). edge(n11,n25). edge(n11,n30). edge(n12,n22). edge(n12,n23). layers(4)."]
num_wrong_responses = 0

total_atoms = 0

#this will contain a tuple of the atom generated and the expected atom
wrong_responses = []
wrong_lines = []


i = 0
for atoms in output:
    
    if atoms == "\n":
        continue


    if i >= len(expected_output):
        print(i)
        break

    #print(f"Expected Atoms: {expected_output[i]}", "Atoms: ", atoms)
    expected_atoms = expected_output[i].split(".")
    expected_atoms = [atom.strip() for atom in expected_atoms]

    n_expected_atoms = len(expected_atoms)
    total_atoms += n_expected_atoms
    
    print("ATOMS")
    for atom in expected_atoms:
        print(atom)

    i += 3

    local_correct = 0
    local_wrong = 0

    for atom in atoms.split("."):
        
        atom = atom.strip()
        atom = atom.replace(" ", "")

        if atom == "":
            continue

        if atom not in expected_atoms:
            local_wrong += 1

            # since they are not ordered we have to find the expected atom
            # that corresponds to the wrong atom
            # to do so we can take as a reference the atom and 
            # calculate the similarity between the atom and the atoms inside the expected_atoms
            # the atom that has the highest similarity will be the expected atom

            match, score = find_closest_match(atom, expected_atoms)

            if score > 80:
                wrong_responses.append((atom, match, score, i-2, atoms))

                # remove the expected atom from the list
                # so that we don't consider it again
                #expected_atoms = expected_atoms.replace(match, "")
            else:
                wrong_responses.append((atom, "", 0, i-2, atoms))
            
            wrong_lines.append(highlight_differences(atoms, expected_atoms))
        else:
            local_correct += 1
    
    # include also the atoms that aren't generated. They threaded as wrong
    left = n_expected_atoms - (local_wrong + local_correct)
    if left >= 0:
        num_wrong_responses += local_wrong + left
    


    

   
if wrong_responses:
    print("\nVisualizing Differences Between Wrong and Correct Responses:")
    for generated, expected, _, idx, gen_atoms in wrong_responses:
        print("\nGenerated String:")
        print(colored(generated, 'blue'))
        print("Expected String:")
        print(colored(expected, 'green'))
        print("Atoms:")
        print(idx, gen_atoms)
        print("Differences Highlighted:")
        print(highlight_differences(generated, expected))

print(f"Number of wrong atoms: {num_wrong_responses} over {total_atoms} atoms. Number of not generated atoms {left}")
# Plot the wrong responses
plt.pie([num_wrong_responses, total_atoms - num_wrong_responses], labels=["Wrong Responses", "Correct Responses"], autopct="%1.1f%%")
plt.title("Response Validity")
plt.show()
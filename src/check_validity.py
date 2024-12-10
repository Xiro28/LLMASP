# to check the validity of a result of a prompt 
# we have to check: len(result) == len(expected_result)
# and for each element in result we have to check if they are equal

from matplotlib import pyplot as plt
from rapidfuzz import process
from termcolor import colored
import difflib

def find_closest_match(element, target_string):
    # Split the target string into individual entities
    entities = target_string.split(".")
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

with open("stories.txt", "r") as f:
    expected_output = f.readlines()

num_wrong_responses = 0

total_atoms = 0

#this will contain a tuple of the atom generated and the expected atom
wrong_responses = []
wrong_lines = []

i = 1
for atoms in output:
    
    if atoms == "\n":
        continue

    if i >= len(expected_output):
        print(i)
        break

    expected_atoms = expected_output[i]

    for atom in atoms.split("."):
        
        atom = atom.strip()
        total_atoms += 1

        if atom not in expected_atoms:
            num_wrong_responses += 1

            # since they are not ordered we have to find the expected atom
            # that corresponds to the wrong atom
            # to do so we can take as a reference the atom and 
            # calculate the similarity between the atom and the atoms inside the expected_atoms
            # the atom that has the highest similarity will be the expected atom

            match, score = find_closest_match(atom, expected_atoms)

            if score > 80:
                wrong_responses.append((atom, match, score))

                # remove the expected atom from the list
                # so that we don't consider it again
                expected_atoms = expected_atoms.replace(match, "")
            else:
                wrong_responses.append((atom, "", 0))
            
            wrong_lines.append(highlight_differences(atoms, expected_atoms))

    i += 3

    
print(f"Number of wrong atoms: {num_wrong_responses} over {total_atoms} atoms")

if wrong_responses:
    print("\nVisualizing Differences Between Wrong and Correct Responses:")
    for generated, expected, _ in wrong_responses:
        print("\nGenerated String:")
        print(colored(generated, 'blue'))
        print("Expected String:")
        print(colored(expected, 'green'))
        print("Differences Highlighted:")
        print(highlight_differences(generated, expected))

# Plot the wrong responses
plt.pie([num_wrong_responses, len(output) - num_wrong_responses], labels=["Wrong Responses", "Correct Responses"], autopct="%1.1f%%")
plt.title("Response Validity")
plt.show()
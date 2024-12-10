import random
from fpdf import FPDF

# Person names and food preferences
persons = ["Marco", "Alex", "Julia", "Sarah", "Luke", "Lorenzo", "Claire", "Matt", "David", "Martina", "Frances", "Andrew"]
foods = ["pizza", "sushi", "burgers", "pasta", "salad", "tacos", "ramen", "Chinese food", "Indian food", "kebab", "paella", "poke"]

# Context phrases
locations = [
    "at the restaurant downtown",
    "at the trattoria nearby",
    "at an ethnic place",
    "by the seaside",
    "at the new bistro",
    "at the pub in the square",
    "at a popular food truck"
]

reasons = [
    "because they wanted to spend some time together",
    "to celebrate a birthday",
    "because they had not seen each other for a while",
    "to relax after a long day",
    "to try something new",
    "just to enjoy each other's company"
]

def generate_story_and_facts(n_people=4):
    # Select a subset of people
    selected_people = random.sample(persons, n_people)
    preferences = {person: random.choice(foods) for person in selected_people}
    location = random.choice(locations)
    reason = random.choice(reasons)

    # Create the story
    facts = []
    story_segments = []
    
    # Varied introduction
    intro = random.choice([
        f"{', '.join(selected_people[:-1])} and {selected_people[-1]} decided to meet {location} {reason}.",
        f"After planning for a few days, {', '.join(selected_people[:-1])} and {selected_people[-1]} finally met {location}.",
        f"{', '.join(selected_people[:-1])} and {selected_people[-1]} wanted to go out {location} for a nice evening."
    ])
    story_segments.append(intro)
    
    # Preferences and hints
    for person in selected_people:
        hint = random.choice([
            f"{person.capitalize()} was excited to try {preferences[person]}.",
            f"Someone suggested {preferences[person]}, knowing it's one of {person.lower()}'s favorite dishes.",
            f"{person.capitalize()} hadn't had {preferences[person]} for a long time and thought it was a good idea.",
            f"{preferences[person]} seemed to be the dish {person.lower()} liked the most."
        ])
        story_segments.append(hint)
        facts.append(f"person({person.lower()}).")
        facts.append(f"want_food({person.lower()}, {preferences[person].lower().replace(' ', '_')}).")

    # Combine story
    story = " ".join(story_segments)
    return story, facts

# File paths
text_file_path = "stories.txt"
pdf_file_path = "stories.pdf"

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Generate 100 stories and save to a text file
with open(text_file_path, "w") as text_file:
    for i in range(1, 101):
        story, facts = generate_story_and_facts(n_people=random.randint(3, 6))
        story_with_facts = story + "\n" + " ".join(facts) + "\n\n"

        text_file.write(story_with_facts)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Story {i}", ln=True, align="L")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, story)
        pdf.ln(5)
        # Facts section
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Facts for Story {i}", ln=True, align="L")
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 10, " ".join(facts))
        pdf.ln(10)   

        pdf.add_page()  

# Save the PDF to a file
pdf.output(pdf_file_path)

print(f"Stories and facts have been saved to '{text_file_path}' and '{pdf_file_path}'.")

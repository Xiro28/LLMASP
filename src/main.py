import time

from outputHandlers.evaluateOutput import EvaluateOuput
from inputHandlers.evaluateInput import EvaluateInput
from LLMASP import LLMASP

def main():
    
    _instance = LLMASP("examples/restaurant_linked.yml")
    
    inp = open("stories.txt", "r")
    f = open("output.txt", "w")

    story_idx = 1

    time_start = time.time()

    lines = ""

    for line in inp:
        if line == "\n" or "person" in line or "want_food" in line:
            continue
        out = _instance.infer(EvaluateInput, "Lorenzo, Marco, Alex, Sarah, Claire and David wanted to go out at an ethnic place for a nice evening. Someone suggested salad, knowing it's one of lorenzo's favorite dishes. pizza seemed to be the dish marco liked the most. Someone suggested Chinese food, knowing it's one of alex's favorite dishes. Sarah was excited to try Chinese food. pizza seemed to be the dish claire liked the most. David hadn't had Chinese food for a long time and thought it was a good idea.").preds

        lines += out + "\n\n"
        
        print(f"Story {story_idx} done. {out}, \n{time.time() - time_start}")

        if story_idx % 25 == 0 and story_idx != 0:
            f.write(lines)
            f.write(f"Time taken: {time.time() - time_start}")

        story_idx += 1
    
    f.write(f"Time taken: {time.time() - time_start}")
    f.close()
    

if __name__ == "__main__":
    main()



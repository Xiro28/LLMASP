import time

from outputHandlers.evaluateOutput import EvaluateOuput
from inputHandlers.evaluateInput import EvaluateInput
from LLMASP import LLMASP

def main():
    
    _instance = LLMASP("examples/king.yml")
    
    inp = open("stories.txt", "r")
    f = open("output.txt", "w")

    story_idx = 1

    time_start = time.time()

    lines = ""

    for line in inp:
        if line == "\n" or "person" in line or "want_food" in line:
            continue
        out = _instance.infer(EvaluateInput, "There is a hole in position (14, 7). The chess board size is 45*45. The square in position (14, 28) is forbidden. There is a hole in position (12, 21). There is a hole in position (1, 15). There is a hole in position (11, 32). There is a hole in position (10, 26). The square in position (1, 33) is forbidden. The square in position (11, 9) is forbidden.").preds

        lines += out + "\n\n"
        
        print(f"Story {story_idx} done. {out}, \n{time.time() - time_start}")

        if story_idx % 25 == 0 and story_idx != 0:
            f.write(lines)
            f.write(f"Time taken: {time.time() - time_start}")

        story_idx += 1
        break
    
    f.write(f"Time taken: {time.time() - time_start}")
    f.close()
    

if __name__ == "__main__":
    main()



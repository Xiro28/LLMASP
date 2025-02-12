import time

from outputHandlers.evaluateOutput import EvaluateOuput
from inputHandlers.evaluateInput import EvaluateInput
from LLMASP import LLMASP

def main():
    
    _instance = LLMASP("./src/examples/king_v2.yml")
    
    inp = open("./src/stories.txt", "r").readlines()
    f = open("./src/output.txt", "w")

    #inp = "There is a hole in position (14, 7). The chess board size is 45*45. The square in position (14, 28) is forbidden. There is a hole in position (12, 21). There is a hole in position (1, 15). There is a hole in position (11, 32). There is a hole in position (10, 26). The square in position (1, 33) is forbidden. The square in position (11, 9) is forbidden."

    story_idx = 1

    time_start = time.time()

    lines = ""

    for line in inp:
        if line == "\n" or "person" in line or "want_food" in line:
            continue
        out = _instance.infer(EvaluateInput, "There is a hole in position (14, 7). The chess board size is 45*45. The square in position (14, 28) is forbidden. There is a hole in position (12, 21). There is a hole in position (1, 15). There is a hole in position (11, 32). There is a hole in position (10, 26). The square in position (1, 33) is forbidden. The square in position (11, 9) is forbidden.").preds
        #out = _instance.infer(EvaluateInput, line).preds
        #out = _instance.infer(EvaluateInput, "Nodes n12 and n22 are connected by an edge. There is an edge between nodes n10 and n19. Layers 0, 1, 2 and 3 contains eight nodes. Vertices n1 and n20 are connected. The graph consist of four layer/s. Layer three contains nodes n31, n32, n33, n34, n35, n36, n37 and n38. Layer two contains nodes n21, n22, n23, n24, n25, n26, n27 and n28. Layer zero contains nodes n1, n10, n2, n3, n4, n5, n6 and n7. Nodes n11 and n25 are connected by an edge. Layer one contains nodes n11, n12, n13, n14, n15, n16, n17 and n18. There is a link between nodes n11 and n22. Vertices n11 and n30 are connected. There is an edge between nodes n10 and n13. Nodes n12 and n23 are connected by an edge.").preds
        lines += out + "\n\n"

        
        print(f"Story {story_idx} done. {out}, \n{time.time() - time_start}")

        if story_idx % 25 == 0 and story_idx != 0:
            f.seek(0)
            f.write(lines)
            #f.write(f"Time taken: {time.time() - time_start}")

        story_idx += 1
        break
    
    f.seek(0)
    f.write(lines)
    f.write(f"Time taken: {time.time() - time_start}")
    f.close()
    

if __name__ == "__main__":
    main()



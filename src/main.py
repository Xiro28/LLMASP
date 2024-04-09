from LLMASP import LLMASP

def main():
    out = LLMASP("./restaurant_example/config.yml", "./restaurant_example/rag_db.yml", "./restaurant_example/code.asp")\
            .extractPreds(input("Enter message to be converted to ASP:\n"), True)\
            .runASP().getEvaluator()
    
    print(out.getInfo())
    print(out.getNaturalOutput())


if __name__ == "__main__":
    main()

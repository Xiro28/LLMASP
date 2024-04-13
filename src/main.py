from LLMASP import LLMASP

def main():
    out = LLMASP("./restaurant_example/config.yml", "./restaurant_example/rag_db.yml", "./restaurant_example/code.asp")\
            .extract_preds(input("Enter message to be converted to ASP:\n"), True)\
            .run_asp().get_evaluator()
    
    print(out.get_info())
    print(out.get_natural_output())


if __name__ == "__main__":
    main()

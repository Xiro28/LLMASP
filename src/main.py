from LLMASP import LLMASP

def main():
    out = LLMASP("./restaurant_example/config.yml", "./restaurant_example/valasp.yml", "./restaurant_example/code.asp", 
                  "_1PSID token from gemini",
                  "_1PSIDTS token from gemini")\
            .extractPreds(input("Enter message to be converted to ASP:\n"))\
            .runASP()
    print(out)


if __name__ == "__main__":
    main()

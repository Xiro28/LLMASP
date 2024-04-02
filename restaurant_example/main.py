from LLMASP import LLMASP

def main():
    rASP = LLMASP("config.yml", "valasp.yml", "code.asp", 
                  "_1PSID token from gemini",
                  "_1PSIDTS token from gemini")
    preds = rASP.extractPreds(input("Enter message to be converted to ASP:\n"))
    out = rASP.runASP()
    print(out)


if __name__ == "__main__":
    main()

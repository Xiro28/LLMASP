

import R2Asp

def main():
    
    req = makeRequest(input("Enter message to be converted to ASP:\n"), config)
    code = cleanOutputRequest(req[0]) + cleanOutputRequest(req[1])
    print(code)


if __name__ == "__main__":
    main()

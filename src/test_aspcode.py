from llmasp import LLMASP

import json

# models: llama3.2:3b-instruct-q8_0
FEW_SAMPLE_MODE = 3

def main():
    _dataset = json.load(open("./dataset.json", "r"))
    _format = open("./asp_grammar/v1", "r").readlines()
    _format = """root        ::= (comment | statement)+
comment     ::= "%" (ws identifier return)+ return
statement   ::= (rule | directive | query) "." return
rule        ::= head ws ":-" ws body
directive   ::= ":-" ws body
query       ::= "?-" ws body
head        ::= atom
body        ::= literal ( ws? "," ws? literal ){0,10}
literal     ::= "not" ws atom | infix
infix       ::= term ws infixop ws term
infixop    ::= "is" | "="  | "<" | ">" | "=<" | ">="
atom        ::= predicate ( "(" ws? terms ws? ")" )?
terms       ::= term ( ws? "," ws? term ){0,9}
term        ::= function "(" ws? terms ws? ")" | constant | identifier
predicate   ::= identifier
function    ::= identifier
constant    ::= identifier
variable    ::= [A-Z_][a-zA-Z0-9_]*
identifier  ::= [a-z][a-zA-Z0-9_]*
return      ::= "\r\n" | "\n"
ws          ::= (" " | "\t")+"""
    problem = _dataset[0]
    problem_name = problem["problem_name"].replace(" ", "")
    _instance = LLMASP(f"applications/{problem_name}.yml", "behaviour/v4_csv_2.yml", 'llama3.1', "llama3.1")
    _atoms = "size(value:int): value is the size of the region."
    _instance.generate_asp(problem["description"], _format, _atoms)

    
    

if __name__ == "__main__":
    main()



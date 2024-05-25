                






















































 
# LLMASP

LLM reasoner using ASP programming language with custom output handler. 
The output handler can be of two types:
 - Evaluator: The evaluator takes the output from the ASP solver and reason over it explaining to the user what it's happening.
 - Executor: The executor takes the output from the ASP solver and execute user defined actions over it (robot controller, battleship player).

[Valasp](https://github.com/alviano/valasp) will be used to syntax control the output of the LLM. Currently we'll use Gemini from Google for quick test.

Structure example of LLMASP:

![first_example](./battleship_image.png)
 
## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes. See deployment
for notes on deploying the project on a live system.
 
### Prerequisites

- Poetry
- LM Studio for local LLM (optional)
 
### Installing

Run:

    poetry install

in the main folder of the project

And

- Windows:

      poetry run python main.py

- Mac:

      poetry run python3 main.py

inside the src folder to execute the demo provided
 
## Authors

See also the list of contributors who participated in this project.

- **Lorenzo Grillo** - [Xiro28](https://github.com/Xiro28)
- **Mario Alviano** - [alviano](https://github.com/alviano)

 
## Acknowledgments

- [G4F](https://github.com/xtekky/gpt4free) for the library used to comunicate with the Gemini client
- [LM Studio](https://lmstudio.ai) for the tool to inference on local hardware offline
- [MakeReadMe](https://www.makeread.me/generator/purplebooth-a-good-readme-template) for this readme structure

## TODO:
 - Add possibility to load multiple yaml configurations to let the LLM decide which one to use based on user input context
 - Possibility to create ASP knowlage based code by understanding what the user instructs (i.e. user input contains battleship rules, LLMASP learn how to play by converting the user input to asp code to be executed when it's requested to play battleship)
 - BabyLLMASP: embedded version for raspberrian devices (example allowing motor/sensor controls from user input)
 - Valasp

## Further Ideas
 - [LLM Instructor](https://python.useinstructor.com) for better conversion to ASP atoms (or any other LLM Grammar output formatter)
 - Build a little IDE to graphically edit the base knowlage of the config.yaml

## Original Idea (italian):

Input: testo in linguaggio naturale
 
Accoppiamo l'input con delle domande a LLM. Ogni domanda ha l'obiettivo di estrarre qualche parte dell'input e mapparla su qualche predicato.
    usiamo YAML per definire una lista di domande
    - question: str
    - predicates
        predicate con arità e tipo (usiamo valasp)
 
LLM ci fornisce una lista di fatti. Usiamo valasp per controllare la correttezza. Se ci sono errori, ripetiamo la domanda (fornendo l'errore).
 
La lista di fatti la accoppiamo con un programma ASP (base di conoscenza contestuale all'applicazione). Otteniamo un answer set (conosciamo il tipo dei predicati in output).
 
Traduciamo l'answer set in linguaggio naturale
    forniamo l'answer set al LLM + suggerimenti sulla base del tipo dei predicati e delle "domande di output"
    
----
 
Formato YAML di una applicazione:
    
preprocessing:
  - question: "What kind of restaurant are you looking for?"
    predicates:
      - restaurant
      - restaurant_kind
 
valasp:
  VALASP YAML FORMAT
 
knowledge_base:
  PROGRAMMA ASP
 
postprocessing:
  - question: "How you would describe the ordered plates?"   % arricchita con "The **ordered plates** are represented by facts on predicate **order** (argument 1 is of type string)."
    predicates:
      - order: "ordered plates"

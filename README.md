# TextToAsp
Text to ASP programming language using [Valasp](https://github.com/alviano/valasp) and LLM (for now we'll use gpt 3.5 model by openAI).

Idea:

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

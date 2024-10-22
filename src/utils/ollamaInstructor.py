from g4f import ChatCompletion, Provider
from typeguard import typechecked
from dataclasses import dataclass

import ollama


"""
    This is intended to be used with free model from g4f since they don't support grammar directed output
    It's also a trade-off between precision and speed since grammar still slows down a lot the inference
"""
class OllamaInstructor:
    
    def __init__(self, _llm):
        self._llm = _llm

    def create(self, response_model, message):
        
        response = ollama.chat(model='llama3.1', messages=[
            {
                'role': 'user',
                'content': message,
            }, 
        ], temperature=0.0, options = { "grammar": "root ::= (\"true\" | \"false\")"})
        
        
        print(response)

        if '[' in out or ']' in out:
            filtered = out.split('[')[1].split(']')[0]
        else:
            return "None"

        ## ADD output control here

        return filtered



from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

import instructor


class Character(BaseModel):
    name: str
    age: int
    fact: List[str] = Field(..., description="A list of facts about the character")


# enables `response_model` in create call
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    ),
    mode=instructor.Mode.JSON,
)

resp = client.chat.completions.create(
    model="llama3",
    messages=[
        {
            "role": "user",
            "content": "Tell me about the Harry Potter",
        }
    ],
    response_model=Character,
)
print(resp.model_dump_json(indent=2))
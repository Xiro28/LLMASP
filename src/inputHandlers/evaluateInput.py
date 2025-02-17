from dataclasses import dataclass
from pydantic import BaseModel, Field
from typeguard import typechecked
from inputHandlers.abstractInputHandler import AbstractInputHandler

from contextlib import suppress
import networkx as nx
import matplotlib.pyplot as plt

import en_core_web_lg
import spacy
import string

nlp = en_core_web_lg.load()

import torch
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer

from word2number import w2n

model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


@typechecked
@dataclass(frozen=False)
class EvaluateInput(AbstractInputHandler):

    def __post_init__ (self):
        self._AbstractInputHandler__system_prompt: str = f"""You are a Natural Language to Datalog translator. 
                                To translate the input to Datalog, you will be asked a sequence of questions. 
                                The answers are inside the user input provided with 'USER_INPUT: input'.
                                Output predicate is a lowercase string (possibly including underscores).  
                                Terms is a comma-separated list of either double quoted strings or integers. 
                                Be sure to control the number of terms in each answer!
                                A predicate MUST terminate with a period.
                                An answer MUST NOT be answered if it is not present in the user input.
                                Remember these instructions and don't say anything!"""
        self.tree = {}

        super().__post_init__()

    def userinput_to_chunk(self, user_input: str) -> list:
        doc = nlp(user_input)

        # remove useless stuff without changing the meaning
        result = []
        temp_str = ''
        for token in doc:
            if "." in token.text:
                result.append(temp_str + '\n')
                temp_str = ''
                continue

            if token.pos_ == "VERB":
                if token.dep_ == "ROOT":
                    temp_str += f"{token.lemma_.upper()} "
                else:
                    temp_str += token.lemma_.upper() + ' '
            elif token.text not in string.punctuation:
                if token.dep_ == "ROOT":
                    temp_str += f"(IMPORTANT INFO) {token.text.upper()} "
                else:
                    temp_str += f"{token.text} "

        """
        for token in doc:
            word, lemma, pos, dep = token.text, token.lemma_, token.pos_, token.dep_

            if (token.is_sent_start == True or dep == "nsubj") and not any(chld.dep_ == "ccomp" for chld in token.ancestors):
                subj = word if check_subj else "you"

                if subj not in nsubj_dict:
                    nsubj_dict[subj] = [[]]
                    pos_vec[subj] = [[]]
                    idx_vec[subj] = 0
                else:
                    idx_vec[subj] += 1
                    nsubj_dict[subj].append([])
                    pos_vec[subj].append([])
                
                if not check_subj:
                    nsubj_dict[subj][idx_vec[subj]].append(word)
                    pos_vec[subj][idx_vec[subj]].append(token.i)
                
                current_subject = [subj]
            elif dep == "conj" and pos not in {"VERB", "AUX"} and any(chld.dep_ in {"nsubj", "dobj", "nsubjpass"} or token.is_sent_start == True for chld in token.ancestors):
                if word not in nsubj_dict:
                    current_subject.append(word)
                    nsubj_dict[word] = [[]]
                    pos_vec[word] = [[]]
                    idx_vec[word] = 0
            elif current_subject:
                # Collect phrases associated with the current subject
                # Add the phrase with adjectives
                for subj in current_subject:
                    #phrase = get_phrase_with_adjectives(token)
                    if token.dep_ != "conj":
                        nsubj_dict[subj][idx_vec[subj]].append(token.text)
                        pos_vec[subj][idx_vec[subj]].append(token.i)
        """

        """chunks = [result]
        for key, values in nsubj_dict.items():
            iter_pos = iter(pos_vec[key])
            values.sort(key=lambda _:next(iter_pos), reverse=False)
            part_ = ""
            for v in values:
                part_ += " ".join([key, *v]).replace(", ,", "")
                part_ += "\n"
            chunks.append(part_)
        """
        # sort the array to heva similar information near so that the llm model doesn't have to continuosly change contex
        return sorted(result, reverse=True)

    def plot_tree(self, dictionary, root_label="person"):
        """
        Plots a dictionary as a tree using NetworkX and Matplotlib.
        
        Args:
            dictionary (dict): Dictionary to plot as a tree.
            root_label (str): Label for the root node.
        """
        def add_edges(graph, parent, subtree):
            """
            Recursively add edges to the graph from the dictionary.
            """
            if isinstance(subtree, dict):
                for key, value in subtree.items():
                    graph.add_edge(parent, key)
                    add_edges(graph, key, value)
            elif isinstance(subtree, list):
                for item in subtree:
                    graph.add_edge(parent, item)
            else:
                graph.add_edge(parent, subtree)

        # Create a directed graph
        graph = nx.DiGraph()

        print(dictionary)

        # Add edges from the dictionary
        add_edges(graph, root_label, dictionary)

        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(graph, seed=42)  # Position the nodes for a clearer layout

        # Draw nodes and edges with improved styling
        nx.draw_networkx_nodes(graph, pos, node_size=3500, node_color="lightblue", edgecolors="black")
        nx.draw_networkx_edges(graph, pos, arrows=True, arrowstyle='-|>', arrowsize=15, edge_color="gray")
        nx.draw_networkx_labels(graph, pos, font_size=12, font_weight="bold", font_color="darkblue")

        # Add title and adjust layout
        plt.title("Tree Representation of a Dictionary", fontsize=16, fontweight="bold")
        plt.axis("off")  # Turn off axis for better visualization
        plt.tight_layout()
        plt.show()


    def __pre_input_seasoning__(self, user_input: str) -> tuple[list, str]:
        """
            Enhances the given input with additional information from the config file to help with the ASP atom extraction.
            
            Parameters:
                user_input: str: The input to be seasoned.
                
            Returns:
                str: The seasoned input with added information to help the LLM for ASP atom extraction.
        """

        questions = self._AbstractInputHandler__config['preprocessing']
        the_user_input = f"USER_INPUT: {user_input}"
        prompt = []
        extra_info = ""

        for q in questions:

            q_key, q_value = list(q.items())[0]

            if q_key == '_':

                #prompt.append(f"""Here is some context that you MUST analyze and remember.
                #            {q_value}
                #            Remember this context and don't say anything!\n
                #            """)

                #pass
                extra_info += q_value + '\n'

            else:
                prompt.append(q_value)

        return prompt, extra_info
    
    def replace_textual_numbers(self, tokens):
        new_tokens = []
        for token in tokens:
            try:
                number = w2n.word_to_num(token.lower())
                new_tokens.append(str(number))
            except Exception:
                new_tokens.append(token)

        return new_tokens
    
    
    def __natural_to_asp__(self, user_input: str) -> str:
        """
            Convert natural language input to ASP (Answer Set Programming) format.
            
            This method takes a natural language input provided by the user and converts it
            into ASP format using the invoke_llm from the LLMHandler class. It preprocesses
            the input by performing input seasoning to extract the atoms contained into the config file,
            and then filters the ASP atoms from the response generated by the LLMHandler.
            
            Parameters:
                user_input (str): The natural language input provided by the user.
                
            Returns:
                str: The ASP-formatted output generated from the natural language input.
        """

        result_atoms = ""

        _class_dict = self.get_classes()
        main_class = [main_class for main_class in _class_dict.items() if "list_" not in main_class[0]]
        descrs, extra_sys_prompt = self.__pre_input_seasoning__(user_input)

        data = ""
        for i, name in enumerate(main_class):
            encoding = tokenizer.encode_plus(text=descrs[i],text_pair=user_input)
            inputs = encoding['input_ids']  
            sentence_embedding = encoding['token_type_ids'] 
            tokens = tokenizer.convert_ids_to_tokens(inputs)

            outputs = model(input_ids=torch.tensor([inputs]), token_type_ids=torch.tensor([sentence_embedding]))

            start_scores = outputs['start_logits']
            end_scores = outputs['end_logits']     

            start_index = torch.argmax(start_scores)

            end_index = torch.argmax(end_scores)

            tokens = self.replace_textual_numbers(tokens[start_index:end_index+1])

            answer = ' '.join(tokens)
            data += f"{name}: {answer}\n"


        #chunk = "".join(self.userinput_to_chunk(user_input))
        #chunk = self._AbstractInputHandler__llm_instance.invoke_llm([f"Reason over this: {info_needed}. Be detailed but also don't say extra info or reasoning.", chunk])

        print(user_input, data) 


        #dict_ = {f"g_{class_[0]}":  Field(description=descrs[idx]) for idx, class_ in enumerate(main_class)}
        dict_ = {f"g_{class_[0]}":  Field(title=class_[0], description=descrs[idx], ) for idx, class_ in enumerate(main_class)}
        dict_["__annotations__"] = {f"g_{name}": list[cls] for name, cls in main_class}

        wrapper =  type(
            "BaseModelWrapper",
            (BaseModel,), 
            dict_
        )

        response =  self._AbstractInputHandler__llm_instance.invoke_llm_constrained(f"Extra info:\n{data}\n{user_input}", wrapper, command = extra_sys_prompt)

        for c, _ in main_class:
            for atoms in response.dict().get(f"g_{c}"):
                    result_atoms += str(_class_dict[c](**atoms)) + "\n"

        return result_atoms
    

    def run(self, custom_input = "", TRAIN_ON: bool = False) -> str:
        """
            Run the input handler to convert the user input to ASP format.
            
            This method takes user input and converts it to ASP format using the natural_to_asp method.
            It then returns the ASP-formatted output.
                
            Returns:
                str: The ASP-formatted output generated from the user input.
        """
        
        self.user_input = custom_input
        response = self.__natural_to_asp__(self.user_input)

        #Disable for now
        if TRAIN_ON and False:
            out: str = input(f"Do you want to salve to rag_doc these results: {self.preds}? (y/n): ")

            if out == "y":
                self.__docs_rag.append({"prompt": user_input, "response": self.preds})
                yaml.dump(self.__docs_rag, open(self.__ragDatabaseFilename, "w"))

        return self.__filter_asp_atoms__(response)

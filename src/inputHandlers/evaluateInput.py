from dataclasses import dataclass
from typeguard import typechecked
from inputHandlers.abstractInputHandler import AbstractInputHandler

from contextlib import suppress
import networkx as nx
import matplotlib.pyplot as plt

import en_core_web_md
import spacy

nlp = en_core_web_md.load()

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

        nsubj_dict = {}

        # Helper function to recursively collect adjectives and connect to nouns
        def get_phrase_with_adjectives(token):
            adjectives = []
            for child in token.children:
                if child.pos_ == "ADJ":
                    adjectives.append(child.text)  # Collect adjective text
            # Concatenate adjectives with the noun or main token
            if adjectives:
                return " ".join(adjectives + [token.text])
            return token.text

        # Current subject being processed
        current_subject = []
        check_subj = any(token.dep_ == "nsubj" for token in doc)

        pos_vec = {}
        idx_vec = {}

        for token in doc:
            word, lemma, pos, dep = token.text, token.lemma_, token.pos_, token.dep_

            if (token.is_sent_start or dep == "nsubj") and not any(chld.dep_ == "ccomp" for chld in token.ancestors):
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
            elif dep == "conj" and pos not in {"VERB", "AUX"}:
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

        chunks = []
        for key, values in nsubj_dict.items():
            #print(values)
            iter_pos = iter(pos_vec[key])
            values.sort(key=lambda _:next(iter_pos), reverse=False)
            part_ = ""
            for v in values:
                part_ += " ".join([key, *v]).replace(", ,", "")
                part_ += "\n"
            chunks.append(part_)

        return chunks

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


    def __pre_input_seasoning__(self, user_input: str) -> list:
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

        for q in questions:

            q_key, q_value = list(q.items())[0]

            if q_key == '_':

                #prompt.append(f"""Here is some context that you MUST analyze and remember.
                #            {q_value}
                #            Remember this context and don't say anything!\n
                #            """)

                pass

            else:
                prompt.append(q_value)

        return prompt
    
    
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

        F = ""

        chunk = self.userinput_to_chunk(user_input)
        chunk_tokenized = [nlp(line) for line in chunk]

        #print(f"{user_input}\nChunk:\n{chunk}")

        _class_dict = self.get_classes()
        _list = [list_class for list_class in _class_dict.items() if "list_" in list_class[0]]
        main_class = [main_class[0] for main_class in _class_dict.items() if "list_" not in main_class[0]]
        
    
        primary_atoms_params = {}

        self.tree = {}

        for i, descr in enumerate(self.__pre_input_seasoning__(user_input)):
            atom = main_class[i]
            #print(f"Atom: {atom}")
            
            weighted_chunk = []
            sort_chunk = True
            
            for f_chunk, tokens in zip(chunk, chunk_tokenized):
                atom_ = nlp(atom)

                if atom_.vector_norm == 0:
                    sort_chunk = False
                    sim = 0
                else:
                    sim = tokens.similarity(atom_)

                weighted_chunk.append((f_chunk, sim))

            if sort_chunk:
                weighted_chunk.sort(key=lambda x: x[1], reverse=True)

            final_chunk = "\n".join([w[0] for w in weighted_chunk])

            #print(f"Final Chunk:\n{final_chunk}")

            # Get the class similar to the atom
            #atom_ = nlp(atom)
            #word = nlp(chunk)
            #if (word.similarity(atom_) <= 0.15):
            #    continue
            #print(f"Similarity: {word.similarity(atom_).conjugate()}, Atom: {chunk}")

            if primary_class := self.links.isLinked(main_class[i]):
                response =  self._AbstractInputHandler__llm_instance.invoke_llm_constrained(final_chunk, _list[i][1], primary_atoms_params[primary_class], command=descr)
            else:
                response =  self._AbstractInputHandler__llm_instance.invoke_llm_constrained(final_chunk, _list[i][1], command=descr)


            #print(f"Response: {response}")
            for atoms in response.dict().get(f"list_{main_class[i]}"):
                class_name = main_class[i]
                class_instance = str(_class_dict[class_name](**atoms))

                F += class_instance + "\n"

        #Plot the tree
        # self.plot_tree(self.tree)

        return F
    

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

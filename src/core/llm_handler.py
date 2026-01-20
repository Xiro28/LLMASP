import ollama

from src.utils.statistics import Statistics

class LLMHandler:
    def __init__(self, llm_model: str, system_prompt: str) -> None:

        # not used yet
        assert system_prompt is not None, "The system prompt must not be None."
        assert system_prompt is not None, "The system prompt must not be empty."

        self.llm_model = llm_model
        
        self.system_prompt = system_prompt
        self.__llm = ollama.Client(host='http://localhost:11435').chat


    def __to_gpt_dict__(self, role: str, text: str) -> dict:
        return {"role": role, "content": text}
    
    def detect_loop_index(self, lines: list[str], min_pat_len: int = 5, repeat_thresh: int = 2):
            n = len(lines)
            max_check = min_pat_len * (repeat_thresh + 1)
            if n < max_check:
                return None

            tail = lines[-max_check:]

            for pat_len in range(min_pat_len, max_check // (repeat_thresh + 1) + 1):
                pat = tail[-pat_len:]
                ok = True
                for k in range(1, repeat_thresh + 1):
                    if tail[-(k + 1) * pat_len : -k * pat_len] != pat:
                        ok = False
                        break
                if ok:
                    # loop starts at the first appearance of the repeating pattern
                    for i in range(n - len(tail), n - pat_len * repeat_thresh):
                        if lines[i:i + pat_len] == pat:
                            return i
            return None
    
    def invoke_llm_constrained(self, prompt: str, class_response: any, command: any) -> dict:
        grammar = class_response

        # if it's not a user defined grammar, convert the passed class to a grammar 
        if type(class_response) != str:
            grammar = class_response.model_json_schema(mode='serialization')

        _messages = [
            self.__to_gpt_dict__("system", f"{self.system_prompt}\nProblem Statement:\n{command}"), 
            self.__to_gpt_dict__("user", f"{prompt}"),
        ]

        _ret = ""

        if class_response == "":

            _ret = self.__llm(
                model=self.llm_model,
                messages=_messages,
                options={
                    'temperature': 0,
                    'main_gpu': 0
                }
            )

            Statistics.log_llm_call(_ret["prompt_eval_count"], _ret["eval_count"])
            _ret = _ret["message"]["content"]

        else:

            # Stream it since large outputs could make Ollama hang
            i = 0
            for chunk in self.__llm(
                model=self.llm_model,
                messages=_messages,
                options={
                    'temperature': 0,
                    'main_gpu': 0
                },
                format = grammar,
                stream=True
            ): 
                
                if chunk["done"]:
                    Statistics.log_llm_call(chunk["prompt_eval_count"], chunk["eval_count"])
                    
                _ret += chunk["message"]["content"]
                i = i + 1

                # if we looped more than 65536 (2^16) times means that probably our model is in a loop of generation.
                # Return empty so we won't fill our set of generated atoms with bad atoms

                loop_start = self.detect_loop_index(_ret.split("\n"), min_pat_len=16, repeat_thresh=2)
                if loop_start is not None:
                    print("Detected looping generation; removing loop.")
                    clean_lines = _ret.split("\n")[:loop_start]
                    return "\n".join(clean_lines)
        
                if i > 65536:
                    print("Exceeded output limit:", _ret)
                    return None
        
        try:
            if type(class_response) != str:
                return class_response.model_validate_json(_ret)
            return _ret
        except Exception as e:
            print(f"Error validating model response: {e}")
            return None
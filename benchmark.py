import json
import logging
import re
import subprocess
import time
import argparse
from datetime import datetime
from pathlib import Path
from itertools import groupby
from typing import Dict, List, Any

from tqdm import tqdm
from src.llmasp import LLMASP
from src.utils.database_manager import create_dataset_from_problems


from src.utils.statistics import Statistics
from src.utils.logger import Logger
from src.core.predicate.condition_cache import ConditionCache
# 
CONFIG_PATHS = {
    "tsv": "experiments/behaviour/v4_tsv.yml",
    "csv": "experiments/behaviour/v4_csv.yml",
    "asp": "experiments/behaviour/v4_asp.yml",
    "json": "experiments/behaviour/v4_json.yml"
}


def get_gpu_energy_uj(gpu_index: int = 0) -> float:
    """Retrieves accumulated energy (uJ) for a specific GPU via rocm-smi."""
    try:
        result = subprocess.run(["rocm-smi", "--showenergy"], capture_output=True, text=True, check=True)
        match = re.search(fr"GPU\[{gpu_index}\].*?Accumulated Energy \(uJ\): ([\d\.]+)", result.stdout)
        return float(match.group(1)) if match else 0.0
    except (FileNotFoundError, subprocess.CalledProcessError, Exception):
        return 0.0


class BenchmarkRunner:
    def __init__(self, mode: str, model: str, pbd: bool, conditional: bool, samples: int, use_condition_cache: bool, dataset_path: str, output_dir: str, target_problems: List[str]):
        self.mode = mode
        self.model = model
        self.pbd = pbd
        self.conditional = conditional
        self.samples = samples
        self.dataset_path = dataset_path
        self.target_problems = target_problems
        
        self.output_file = self._generate_output_path(output_dir, use_condition_cache)
        self.llmasp = self._init_llmasp(use_condition_cache)
        self.statistics = {}

        Statistics.reset()
        if not use_condition_cache:
            ConditionCache.disable()
        else:
            ConditionCache.enable()


    def _generate_output_path(self, output_dir: str, use_condition_cache: bool) -> str:
        model_suffix = self.model.split(':')[1] if ':' in self.model else self.model
        cond_str = "conditional" if self.conditional else "nonconditional"
        pbd_str = "a2" if self.pbd else "a1"
        cached_str = "cached" if use_condition_cache else "noncached"
        return f"{output_dir}/mixed_{self.mode}_{model_suffix}_{pbd_str}_{cond_str}_{cached_str}.json"

    def _init_llmasp(self, use_condition_cache: bool) -> LLMASP:
        base_config = "single_application" if self.conditional else "single_application_no_condition"
        suffix = "_cached" if use_condition_cache else ""
        config_file = f"./experiments/mixed_applications/{base_config}{suffix}.yml"
        return LLMASP(config_file, CONFIG_PATHS[self.mode], self.model)

    def _infer_single(self, obj: Dict[str, Any]) -> str:
        prompt_suffix = f"{obj['description']}\n{obj['format']}" if self.pbd else f"{obj['format']}"
        try:
            result = self.llmasp.infer(obj["text"], prompt_suffix, self.mode)
            return result.extracted_preds + "\n"
        except Exception as e:
            logging.error("Errore durante l'inferenza", exc_info=True)
            return "ERROR\n"

    def _process_group(self, problem_name: str, problems_list: List[Dict]) -> Dict[str, Any]:
        """Handles metrics and inference for a specific problem group."""
        start_time = datetime.now()
        start_energy = get_gpu_energy_uj()
        last_stats = Statistics.get_stats()

        results = []
        for obj in tqdm(problems_list, desc=f"Inferencing {problem_name}", leave=False):
            results.append(self._infer_single(obj))

        return {
            "results": results,
            "total_energy_uJ": get_gpu_energy_uj() - start_energy,
            "total_time_seconds": (datetime.now() - start_time).total_seconds(),
            **Statistics.get_statistics_since(last_stats)
        }

    def run(self):
        dataset = create_dataset_from_problems(self.dataset_path, self.target_problems, samples=self.samples)
        dataset.sort(key=lambda x: x["problem_name"])
        print(f"Loaded {len(dataset)} problems.")

        global_start = datetime.now()
        global_energy_start = get_gpu_energy_uj()

        for problem_name, group in groupby(dataset, key=lambda x: x["problem_name"]):
            print(f"--> Processing: {problem_name}")
            self.statistics[problem_name] = self._process_group(problem_name, list(group))

        self.statistics["final_data"] = {
            "total_energy_uJ": get_gpu_energy_uj() - global_energy_start,
            "total_time_seconds": (datetime.now() - global_start).total_seconds(),
            **Statistics.get_stats()
        }
        
        self._save_results()
        print(f"Completed {self.mode} | Total Energy: {self.statistics['final_data']['total_energy_uJ']} uJ")

    def _save_results(self):
        path = Path(self.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding='utf-8') as f:
            json.dump(self.statistics, f, indent=4)

        with open(path.parent / "log.txt", "w", encoding='utf-8') as f:
            f.write("\n".join(Logger.get_logs()))

# --- Execution Handling ---
def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding='utf-8') as f:
        return json.load(f)
    
def get_output_folder_fullname(base: str) -> str:
    return base + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "/"

def run_from_config(config_path: str):
    options = load_config(config_path)
    common_args = {
        "dataset_path": options.get("dataset_path", "./experiments/dataset/dataset.json"),
        "output_dir": get_output_folder_fullname(options.get("output_dir","./experiments/results/")),
        "target_problems": options.get("problems", []),
        "samples": options.get("samples", 2)
    }

    # copy the option.json to the output dir for future reference
    output_dir = Path(common_args["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", config_path, str(output_dir / "options.json")])

    for cfg in options.get("configurations", []):
        print(f"Running Config: {cfg}")
        BenchmarkRunner(
            mode=cfg.get("extraction_mode", "csv"),
            model=cfg.get("model", "llama3.1:8b"),
            pbd=cfg.get("include_problem_description", False),
            conditional=cfg.get("conditional", False),
            use_condition_cache=cfg.get("use_condition_cache", False),
            **common_args
        ).run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LLMASP Benchmarks")
    parser.add_argument("--config", type=str, help="Path to configuration JSON file")
    args = parser.parse_args()

    if args.config:
        run_from_config(args.config)
    else:
        # Default fallback run
        BenchmarkRunner(
            mode="json", model="llama3.1:8b", pbd=True, conditional=True, 
            samples=5, use_condition_cache=True, dataset_path="./experiments/dataset/dataset.json", 
            output_dir=get_output_folder_fullname("./experiments/results/"), 
            target_problems=[ "Crossing Minimization", "Incremental Scheduling", "Knight Tour With Holes", "Sokoban", "Valves Location Problem"]
        ).run()
    
    print("Benchmarking completed.")
    print(Statistics.get_stats())
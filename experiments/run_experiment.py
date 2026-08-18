"""Week 1 experiment-runner interface; full pipeline is integrated later."""
import json
from pathlib import Path

def load_config(path: str|Path) -> dict:
    with open(path, encoding="utf-8") as f: return json.load(f)

def main(config_path="experiments/configs/exp001.json"):
    config=load_config(config_path)
    print(f"Loaded experiment {config['experiment_id']}")
    print("Week 1 runner: pipeline execution will be integrated later.")

if __name__=="__main__": main()

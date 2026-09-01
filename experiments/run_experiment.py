"""Week 1 experiment runner foundation."""
import json
from pathlib import Path

def load_config(path):
    with open(path,encoding="utf-8") as f: return json.load(f)

def main(config_path="experiments/configs/exp001.json"):
    config=load_config(config_path)
    print(f"Loaded experiment: {config['experiment_id']}")
    print("Pipeline integration will be added after team modules are available.")

if __name__=="__main__": main()

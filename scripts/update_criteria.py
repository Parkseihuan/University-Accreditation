import os
import yaml
import json
import argparse
from parsers import parse_fulltime_ratio, parse_new_hires
from renderer import update_markdown_block

# Map parser names to functions
PARSERS = {
    "parse_fulltime_ratio": parse_fulltime_ratio,
    "parse_new_hires": parse_new_hires
}

def load_config(criterion_id):
    config_path = os.path.join("criteria", criterion_id, "config.yml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def process_criterion(criterion_id):
    print(f"Processing Criterion {criterion_id}...")
    config = load_config(criterion_id)
    
    metrics = {}
    
    # 1. Parse Data
    for source in config.get('data_sources', []):
        parser_name = source['parser']
        if parser_name in PARSERS:
            files = source['files']
            # Resolve relative paths
            abs_files = [os.path.abspath(os.path.join("criteria", criterion_id, f)) for f in files]
            
            # Check if files exist
            valid_files = [f for f in abs_files if os.path.exists(f)]
            if not valid_files:
                print(f"Warning: No valid files found for {source['id']}")
                continue
                
            print(f"  Parsing {source['id']} from {len(valid_files)} files...")
            data = PARSERS[parser_name](valid_files)
            metrics[source['id']] = data
            
            # Update Markdown immediately (or collect all and update later)
            target_block = source['target_block']
            
            # Map criterion ID to Korean filename
            filename_map = {
                "3.1": "3.1 교원 확보 및 구성.md",
                "3.2": "3.2 교원 인사 및 업적평가.md",
                "3.3": "3.3 교원 처우 및 복지.md",
                "3.4": "3.4 교원의 연구활동 및 성과.md",
                "3.5": "3.5 직원 확보 및 인사.md",
                "3.6": "3.6 직원 복지 및 업무 역량 개발.md"
            }
            
            md_filename = filename_map.get(criterion_id)
            if not md_filename:
                print(f"Error: No filename mapping for {criterion_id}")
                continue
                
            md_file = os.path.join("report", md_filename)
            
            update_markdown_block(md_file, target_block, data)
            
    # 2. LLM Processing (Placeholder)
    # for block in config.get('llm_blocks', []):
    #     ...

    # Save metrics for debugging
    os.makedirs("metrics", exist_ok=True)
    with open(f"metrics/{criterion_id}.json", 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"Finished Criterion {criterion_id}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--criterion", type=str, default="3.1")
    args = parser.parse_args()
    
    process_criterion(args.criterion)

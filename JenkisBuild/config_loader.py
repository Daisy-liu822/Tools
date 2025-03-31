import yaml
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    with open('JenkisBuild/config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) 
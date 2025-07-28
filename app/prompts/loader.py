import yaml
from pathlib import Path
from typing import Dict

_prompt_path = Path(__file__).parent / "templates.yml"

def load_prompts() -> Dict[str, str]:
    """Loads all prompts from the YAML file."""
    with open(_prompt_path, 'r') as f:
        return yaml.safe_load(f)

PROMPTS = load_prompts()

def get_prompt(key: str, **kwargs) -> str:
    """
    Retrieves and formats a prompt from the loaded templates.
    """
    if key not in PROMPTS:
        raise ValueError(f"Prompt key '{key}' not found in templates.")
    
    return PROMPTS[key].format(**kwargs) 
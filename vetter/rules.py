import yaml
from typing import Dict, List, Any, Tuple

def load_rules(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def required_fields_for(doc_type: str, rules: dict) -> List[str]:
    return rules.get("required_by_type", {}).get(doc_type, [])

def cross_doc_checks(rules: dict) -> List[dict]:
    return rules.get("cross_doc_checks", [])

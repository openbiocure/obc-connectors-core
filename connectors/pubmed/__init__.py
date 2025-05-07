"""PubMed connector package."""

import os
import yaml
from typing import Dict, Any, Optional, cast

from .connector import PubMedConnector

def get_version() -> str:
    """Get connector version from YAML configuration."""
    yaml_path = os.path.join(os.path.dirname(__file__), 'connector.yaml')
    if not os.path.exists(yaml_path):
        raise ImportError(f"connector.yaml not found")
        
    with open(yaml_path) as f:
        spec = cast(Dict[str, Any], yaml.safe_load(f))
        if not spec.get('version'):
            raise ImportError(f"Version not specified in connector.yaml")
        return spec['version']

__version__ = get_version()
__all__ = ['PubMedConnector'] 
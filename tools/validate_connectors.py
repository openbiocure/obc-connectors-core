#!/usr/bin/env python3
"""Validate connector YAML files against schema and design guidelines."""

import os
import sys
import json
import yaml
import jsonschema
from typing import Dict, Any, List, Tuple

# Basic schema for connector YAML files
CONNECTOR_SCHEMA = {
    "type": "object",
    "required": ["name", "version", "capabilities", "api"],
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-z_]+$",
            "description": "Connector name in lowercase with underscores"
        },
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$",
            "description": "Semantic version number"
        },
        "capabilities": {
            "type": "object",
            "additionalProperties": {"type": "boolean"},
            "description": "Connector capabilities flags"
        },
        "api": {
            "type": "object",
            "required": ["base_url", "endpoints"],
            "properties": {
                "base_url": {
                    "type": "string",
                    "description": "Base URL for API requests"
                },
                "endpoints": {
                    "type": "object",
                    "additionalProperties": {
                        "$ref": "#/definitions/endpoint"
                    }
                }
            }
        }
    },
    "definitions": {
        "endpoint": {
            "type": "object",
            "required": ["path", "method", "params", "response"],
            "properties": {
                "path": {"type": "string"},
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE"]
                },
                "params": {
                    "type": "object",
                    "additionalProperties": True
                },
                "response": {
                    "type": "object",
                    "required": ["mapping"],
                    "properties": {
                        "mapping": {
                            "type": "object",
                            "additionalProperties": True
                        }
                    }
                }
            }
        }
    }
}

def validate_yaml_structure(content: Dict[str, Any]) -> List[str]:
    """Validate basic YAML structure against schema."""
    validator = jsonschema.Draft7Validator(CONNECTOR_SCHEMA)
    return [e.message for e in validator.iter_errors(content)]

def check_naming_conventions(content: Dict[str, Any]) -> List[str]:
    """Verify naming conventions are followed."""
    errors = []
    
    # Check endpoint names
    for endpoint in content.get("api", {}).get("endpoints", {}):
        if not endpoint.islower() or not endpoint.replace("_", "").isalnum():
            errors.append(f"Endpoint name '{endpoint}' should be lowercase with underscores")
    
    # Check parameter names
    for endpoint in content.get("api", {}).get("endpoints", {}).values():
        for param in endpoint.get("params", {}):
            if not param.islower():
                errors.append(f"Parameter name '{param}' should be lowercase")
    
    return errors

def check_transform_complexity(content: Dict[str, Any]) -> List[str]:
    """Check for overly complex transforms in YAML."""
    errors = []
    
    def check_depth(obj: Any, path: str, depth: int = 0) -> None:
        if depth > 3:  # Max allowed nesting depth for transforms
            errors.append(f"Transform at '{path}' is too deeply nested (max depth: 3)")
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                check_depth(value, new_path, depth + 1)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_depth(item, f"{path}[{i}]", depth + 1)
    
    # Check transform sections
    for endpoint in content.get("api", {}).get("endpoints", {}).values():
        response = endpoint.get("response", {})
        mapping = response.get("mapping", {})
        for key, value in mapping.items():
            if isinstance(value, dict) and "transform" in value:
                check_depth(value["transform"], f"transform.{key}")
    
    return errors

def validate_connector_yaml(file_path: str) -> Tuple[bool, List[str]]:
    """Validate a connector YAML file."""
    try:
        with open(file_path, 'r') as f:
            content = yaml.safe_load(f)
    except Exception as e:
        return False, [f"Failed to load YAML file: {str(e)}"]
    
    errors = []
    
    # Validate against schema
    errors.extend(validate_yaml_structure(content))
    
    # Check naming conventions
    errors.extend(check_naming_conventions(content))
    
    # Check transform complexity
    errors.extend(check_transform_complexity(content))
    
    return len(errors) == 0, errors

def main():
    """Validate all connector YAML files."""
    connectors_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "connectors")
    exit_code = 0
    
    for root, _, files in os.walk(connectors_dir):
        for file in files:
            if file == "connector.yaml":
                file_path = os.path.join(root, file)
                print(f"\nValidating {file_path}...")
                
                valid, errors = validate_connector_yaml(file_path)
                if not valid:
                    exit_code = 1
                    print("❌ Validation failed:")
                    for error in errors:
                        print(f"  - {error}")
                else:
                    print("✅ Validation passed")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 
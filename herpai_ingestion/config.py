from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List, Set
import logging
from datetime import datetime

from herpai_lib.core.config import AppConfig as BaseAppConfig

@dataclass
class BiomedicalAppConfig(BaseAppConfig):
    """Extended application configuration for biomedical data ingestion."""
    
    # Extend base AppConfig with biomedical-specific settings
    pubmed_api_key: Optional[str] = None
    grobid_host: str = "localhost"
    grobid_port: int = 8070
    pdf_storage_path: str = "data/pdfs"
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'BiomedicalAppConfig':
        """Create an instance from a YAML file by extending base implementation."""
        # First use the parent class implementation
        instance = super().from_yaml(config_path)
        
        # Then add our custom properties
        yaml_config = cls._get_yaml_config()
        
        # Set biomedical-specific properties from YAML
        if yaml_config:
            instance.pubmed_api_key = yaml_config.get('sources.pubmed.api_key')
            
            if yaml_config.get('grobid'):
                instance.grobid_host = yaml_config.get('grobid.host', instance.grobid_host)
                instance.grobid_port = yaml_config.get('grobid.port', instance.grobid_port)
            
            if yaml_config.get('storage.pdf_path'):
                instance.pdf_storage_path = yaml_config.get('storage.pdf_path', instance.pdf_storage_path)
        
        return instance

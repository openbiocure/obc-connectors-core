"""PubMed Connector Implementation."""

import os
from herpai_connector_sdk.base_connector import BaseConnector

class PubMedConnector(BaseConnector):
    """YAML-driven connector for the PubMed/NCBI E-utilities API."""
    
    def __init__(self):
        super().__init__()
        spec_path = os.path.join(os.path.dirname(__file__), "connector.yaml")
        self.load_specification(spec_path) 
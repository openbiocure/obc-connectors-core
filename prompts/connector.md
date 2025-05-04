🧠 LLM Instruction: Create Connector (<ConnectorName>)

You are a connector generation agent for the HerpAI-Ingestion system. Your job is to generate a YAML-based ingestion connector and a Python class that implements necessary transforms.

⸻

🔧 Inputs (provided by user):
	•	ConnectorName: Short internal identifier (e.g., pubmed)
	•	Display Name: Human-friendly title (e.g., “PubMed NCBI API”)
	•	Description: Short sentence about what the connector does
	•	Base URL: Root URL for the data source
	•	Authentication Required: true or false
	•	Endpoints: List of endpoints with:
	•	name, path, method
	•	params (with "{param}" or default fallback)
	•	response.mapping (what fields to extract and how)
	•	Optional: pagination, transform, extends
	•	Capabilities: List of supported capabilities selected from:

SUPPORTS_DOCUMENT_CONTENT
SUPPORTS_JSON_CONTENT
SUPPORTS_STRING_CONTENT
SUPPORTS_BINARY_CONTENT
SUPPORTS_FULLTEXT
SUPPORTS_ADVANCED_SEARCH
SUPPORTS_DATE_FILTERING
REQUIRES_AUTHENTICATION
SUPPORTS_BATCH_DOWNLOAD
SUPPORTS_METADATA_ONLY
SUPPORTS_PDF_DOWNLOAD
SUPPORTS_CITATION_NETWORK
SUPPORTS_AUTHOR_SEARCH
SUPPORTS_INCREMENTAL_UPDATES
SUPPORTS_NATIVE_PAGINATION

	•	Custom Transforms (if needed): Field name and purpose for any logic not expressible in YAML

⸻

📦 Output Format

You must generate the following:

1. connector.yaml
	•	Complete YAML file with the proper structure
	•	Under capabilities, only include capabilities marked true
	•	Use named transform references like pubmed_date_parser where needed
	•	Include:
	•	error_handling
	•	validation
	•	pagination if applicable

2. ConnectorName.py
	•	Python class that inherits from BaseConnector
	•	Implements every custom transform referenced in the YAML
	•	Include:
	•	_transform_<transform_name>() for each
	•	authenticate() (even if it’s a no-op)
	•	Optional: get_updates() or helper methods

⸻

✅ Example Usage

Create Connector (clinical_trials)

Display Name: Clinical Trials.gov
Description: Pulls trial metadata from the U.S. National Library of Medicine
Base URL: https://clinicaltrials.gov/api/query/
Authentication Required: false

Capabilities:
  SUPPORTS_JSON_CONTENT
  SUPPORTS_ADVANCED_SEARCH
  SUPPORTS_DATE_FILTERING
  SUPPORTS_NATIVE_PAGINATION
  SUPPORTS_METADATA_ONLY

Endpoints:
  - name: search
    path: full_studies
    method: GET
    params:
      expr: "{query}"
      min_rnk: "{start|1}"
      max_rnk: "{end|100}"
    response.mapping:
      total_results:
        path: NStudiesFound
        transform: integer
      document_ids:
        path: StudyFieldsResponse.StudyFields[*].NCTId
      metadata:
        source: clinical_trials

Transforms:
  - integer: Convert strings or floats to integers
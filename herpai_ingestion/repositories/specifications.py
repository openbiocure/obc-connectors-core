from herpai_lib.core.repositories import Specification
from sqlalchemy import and_, or_, func
from datetime import datetime

from src.models.document import Document
from src.models.ingestion_state import IngestionState
from src.models.scheduled_job import ScheduledJob

# Document specifications
class DocumentBySourceSpecification(Specification[Document]):
    """Specification for finding documents by source."""
    
    def __init__(self, source: str):
        self.source = source
    
    def to_expression(self):
        return Document.source == self.source

class DocumentByExternalIdSpecification(Specification[Document]):
    """Specification for finding documents by external ID."""
    
    def __init__(self, source: str, external_id: str):
        self.source = source
        self.external_id = external_id
    
    def to_expression(self):
        return and_(Document.source == self.source, Document.external_id == self.external_id)

class DocumentByDoiSpecification(Specification[Document]):
    """Specification for finding documents by DOI."""
    
    def __init__(self, doi: str):
        self.doi = doi
    
    def to_expression(self):
        return Document.doi == self.doi

class DocumentByPmidSpecification(Specification[Document]):
    """Specification for finding documents by PMID."""
    
    def __init__(self, pmid: str):
        self.pmid = pmid
    
    def to_expression(self):
        return Document.pmid == self.pmid

class DocumentByPmcidSpecification(Specification[Document]):
    """Specification for finding documents by PMCID."""
    
    def __init__(self, pmcid: str):
        self.pmcid = pmcid
    
    def to_expression(self):
        return Document.pmcid == self.pmcid

class UnprocessedDocumentSpecification(Specification[Document]):
    """Specification for finding unprocessed documents."""
    
    def to_expression(self):
        return Document.processed == False

class DocumentByDateRangeSpecification(Specification[Document]):
    """Specification for finding documents by publication date range."""
    
    def __init__(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date
    
    def to_expression(self):
        return and_(
            Document.publication_date >= self.start_date,
            Document.publication_date <= self.end_date
        )

class DocumentSearchSpecification(Specification[Document]):
    """Specification for searching documents by title or abstract."""
    
    def __init__(self, query: str):
        self.query = query
    
    def to_expression(self):
        return or_(
            Document.title.ilike(f"%{self.query}%"),
            Document.abstract.ilike(f"%{self.query}%")
        )

# IngestionState specifications
class IngestionStateByJobIdSpecification(Specification[IngestionState]):
    """Specification for finding ingestion state by job ID."""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
    
    def to_expression(self):
        return IngestionState.job_id == self.job_id

class IngestionStateByStatusSpecification(Specification[IngestionState]):
    """Specification for finding ingestion states by status."""
    
    def __init__(self, status: str):
        self.status = status
    
    def to_expression(self):
        return IngestionState.status == self.status

class ActiveIngestionStateSpecification(Specification[IngestionState]):
    """Specification for finding active ingestion states."""
    
    def to_expression(self):
        return IngestionState.status.in_(["pending", "running"])

# ScheduledJob specifications
class ScheduledJobByNameSpecification(Specification[ScheduledJob]):
    """Specification for finding scheduled job by name."""
    
    def __init__(self, name: str):
        self.name = name
    
    def to_expression(self):
        return ScheduledJob.name == self.name

class EnabledScheduledJobSpecification(Specification[ScheduledJob]):
    """Specification for finding enabled scheduled jobs."""
    
    def to_expression(self):
        return ScheduledJob.enabled == True

class RunningScheduledJobSpecification(Specification[ScheduledJob]):
    """Specification for finding running scheduled jobs."""
    
    def to_expression(self):
        return ScheduledJob.running == True

class DueScheduledJobSpecification(Specification[ScheduledJob]):
    """Specification for finding scheduled jobs that are due to run."""
    
    def __init__(self, reference_time: datetime = None):
        self.reference_time = reference_time or datetime.utcnow()
    
    def to_expression(self):
        return and_(
            ScheduledJob.enabled == True,
            ScheduledJob.running == False,
            ScheduledJob.next_run <= self.reference_time
        )

"""Unit tests for data models."""

import pytest
from datetime import datetime
from obc_connector_sdk.models import Document, Author


class TestAuthor:
    """Test cases for Author model."""

    def test_author_creation(self):
        """Test basic author creation."""
        author = Author(
            name="John Doe",
            orcid="0000-0000-0000-0000",
            email="john@example.com",
            affiliation="Test University"
        )
        
        assert author.name == "John Doe"
        assert author.orcid == "0000-0000-0000-0000"
        assert author.email == "john@example.com"
        assert author.affiliation == "Test University"

    def test_author_minimal(self):
        """Test author creation with minimal data."""
        author = Author(name="Jane Smith")
        
        assert author.name == "Jane Smith"
        assert author.orcid is None
        assert author.email is None
        assert author.affiliation is None

    def test_author_optional_fields(self):
        """Test author with some optional fields."""
        author = Author(
            name="Bob Wilson",
            orcid="0000-0000-0000-0001"
        )
        
        assert author.name == "Bob Wilson"
        assert author.orcid == "0000-0000-0000-0001"
        assert author.email is None
        assert author.affiliation is None


class TestDocument:
    """Test cases for Document model."""

    def test_document_creation(self):
        """Test basic document creation."""
        doc = Document(
            id="doc123",
            source="test_connector",
            title="Test Document"
        )
        
        assert doc.id == "doc123"
        assert doc.source == "test_connector"
        assert doc.title == "Test Document"
        assert doc.abstract is None
        assert doc.publication_date is None
        assert doc.doi is None
        assert doc.url is None
        assert doc.authors == []
        assert doc.keywords == []
        assert doc.document_type == "article"
        assert doc.full_text is None
        assert doc.content is None
        assert doc.metadata == {}

    def test_document_with_all_fields(self):
        """Test document creation with all fields."""
        pub_date = datetime(2023, 1, 1)
        authors = [
            Author(name="Author One"),
            Author(name="Author Two")
        ]
        
        doc = Document(
            id="doc456",
            source="test_connector",
            title="Complete Test Document",
            abstract="This is a test abstract",
            publication_date=pub_date,
            doi="10.1000/test.456",
            url="https://example.com/doc456",
            authors=authors,
            keywords=["test", "document", "complete"],
            document_type="research_article",
            full_text="Full text content here",
            content={"raw": "data"},
            metadata={"key": "value"}
        )
        
        assert doc.id == "doc456"
        assert doc.source == "test_connector"
        assert doc.title == "Complete Test Document"
        assert doc.abstract == "This is a test abstract"
        assert doc.publication_date == pub_date
        assert doc.doi == "10.1000/test.456"
        assert doc.url == "https://example.com/doc456"
        assert len(doc.authors) == 2
        assert doc.authors[0].name == "Author One"
        assert doc.authors[1].name == "Author Two"
        assert doc.keywords == ["test", "document", "complete"]
        assert doc.document_type == "research_article"
        assert doc.full_text == "Full text content here"
        assert doc.content == {"raw": "data"}
        assert doc.metadata == {"key": "value"}

    def test_document_default_values(self):
        """Test document default values."""
        doc = Document(
            id="doc789",
            source="test_connector",
            title="Default Test Document"
        )
        
        assert doc.document_type == "article"
        assert doc.authors == []
        assert doc.keywords == []
        assert doc.metadata == {}

    def test_document_with_string_content(self):
        """Test document with string content."""
        doc = Document(
            id="doc_string",
            source="test_connector",
            title="String Content Document",
            content="This is string content"
        )
        
        assert doc.content == "This is string content"

    def test_document_with_dict_content(self):
        """Test document with dictionary content."""
        content_dict = {"type": "json", "data": {"key": "value"}}
        doc = Document(
            id="doc_dict",
            source="test_connector",
            title="Dict Content Document",
            content=content_dict
        )
        
        assert doc.content == content_dict

    def test_document_with_bytes_content(self):
        """Test document with bytes content."""
        content_bytes = b"Binary content data"
        doc = Document(
            id="doc_bytes",
            source="test_connector",
            title="Bytes Content Document",
            content=content_bytes
        )
        
        assert doc.content == content_bytes

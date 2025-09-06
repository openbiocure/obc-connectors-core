#!/usr/bin/env python3
"""
PubMed Connector Example

This example demonstrates how to use the PubMed connector to search for
biomedical literature and retrieve detailed information about research papers.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from connectors.pubmed.connector import PubMedConnector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def basic_search_example():
    """Demonstrate basic search functionality."""
    print("=== Basic Search Example ===")

    connector = PubMedConnector()

    try:
        # Search for papers about cancer research
        results = await connector.search("cancer research", limit=5)

        print(f"Found {results['total_results']} total results")
        print(f"Retrieved {len(results['document_ids'])} document IDs:")

        for i, doc_id in enumerate(results['document_ids'], 1):
            print(f"  {i}. {doc_id}")

        return results['document_ids']

    finally:
        await connector.close()


async def document_retrieval_example(doc_ids):
    """Demonstrate document retrieval functionality."""
    print("\n=== Document Retrieval Example ===")

    connector = PubMedConnector()

    try:
        # Get detailed information for the first document
        if doc_ids:
            doc_id = doc_ids[0]
            print(f"Retrieving document: {doc_id}")

            doc = await connector.get_by_id(doc_id)

            if doc.get('error'):
                print(f"Error retrieving document: {doc['error']}")
                return

            print(f"Title: {doc['title']}")
            print(f"Journal: {doc.get('journal', 'N/A')}")
            print(f"Publication Date: {doc.get('publication_date', 'N/A')}")
            print(f"DOI: {doc.get('doi', 'N/A')}")
            print(f"PMID: {doc.get('pmid', 'N/A')}")
            print(f"URL: {doc.get('url', 'N/A')}")

            # Display authors
            authors = doc.get('authors', [])
            print(f"\nAuthors ({len(authors)}):")
            for i, author in enumerate(authors[:3], 1):  # Show first 3 authors
                print(f"  {i}. {author['name']}")
                if author.get('affiliation'):
                    print(f"     Affiliation: {author['affiliation']}")

            # Display MeSH terms
            mesh_terms = doc.get('metadata', {}).get('mesh_terms', [])
            if mesh_terms:
                print(f"\nMeSH Terms (top 5):")
                for i, term in enumerate(mesh_terms[:5], 1):
                    print(f"  {i}. {term}")

            # Display keywords
            keywords = doc.get('metadata', {}).get('keywords', [])
            if keywords:
                print(f"\nKeywords: {', '.join(keywords[:5])}")

            # Display publication type
            pub_type = doc.get('metadata', {}).get('publication_type', 'N/A')
            print(f"\nPublication Type: {pub_type}")

            # Display citation count
            citation_count = doc.get('metadata', {}).get('citation_count', 0)
            print(f"Citation Count: {citation_count}")

            # Display PMC ID if available
            pmc_id = doc.get('metadata', {}).get('pmc_id')
            if pmc_id:
                print(f"PMC ID: {pmc_id}")

    finally:
        await connector.close()


async def advanced_search_example():
    """Demonstrate advanced search functionality."""
    print("\n=== Advanced Search Example ===")

    connector = PubMedConnector()

    try:
        # Search with field tags
        query = "cancer[Title] AND 2023[Publication Date]"
        results = await connector.search(query, limit=3)

        print(f"Searching for: {query}")
        print(f"Found {results['total_results']} total results")
        print(f"Retrieved {len(results['document_ids'])} document IDs:")

        for i, doc_id in enumerate(results['document_ids'], 1):
            print(f"  {i}. {doc_id}")

    finally:
        await connector.close()


async def mesh_search_example():
    """Demonstrate MeSH term search functionality."""
    print("\n=== MeSH Term Search Example ===")

    connector = PubMedConnector()

    try:
        # Search using MeSH terms
        query = "Neoplasms[MeSH Terms] AND Therapy[MeSH Terms]"
        results = await connector.search(query, limit=3)

        print(f"Searching for: {query}")
        print(f"Found {results['total_results']} total results")
        print(f"Retrieved {len(results['document_ids'])} document IDs:")

        for i, doc_id in enumerate(results['document_ids'], 1):
            print(f"  {i}. {doc_id}")

    finally:
        await connector.close()


async def journal_search_example():
    """Demonstrate journal-specific search functionality."""
    print("\n=== Journal Search Example ===")

    connector = PubMedConnector()

    try:
        # Search within specific journal
        query = "cancer[Title] AND Nature[Journal]"
        results = await connector.search(query, limit=3)

        print(f"Searching for: {query}")
        print(f"Found {results['total_results']} total results")
        print(f"Retrieved {len(results['document_ids'])} document IDs:")

        for i, doc_id in enumerate(results['document_ids'], 1):
            print(f"  {i}. {doc_id}")

    finally:
        await connector.close()


async def incremental_updates_example():
    """Demonstrate incremental updates functionality."""
    print("\n=== Incremental Updates Example ===")

    connector = PubMedConnector()

    try:
        # Get papers published in the last 30 days
        since_date = datetime.now() - timedelta(days=30)
        print(f"Searching for papers published since: {since_date.strftime('%Y-%m-%d')}")

        results = await connector.get_updates(since_date)

        print(f"Found {results['total_results']} new papers")
        print(f"Retrieved {len(results['document_ids'])} document IDs:")

        for i, doc_id in enumerate(results['document_ids'][:5], 1):  # Show first 5
            print(f"  {i}. {doc_id}")

        if len(results['document_ids']) > 5:
            print(f"  ... and {len(results['document_ids']) - 5} more")

    finally:
        await connector.close()


async def configuration_example():
    """Demonstrate connector configuration."""
    print("\n=== Configuration Example ===")

    connector = PubMedConnector()

    try:
        # Configure with API key for higher rate limits
        config = {
            "api_key": "your-ncbi-api-key"  # Replace with your actual API key
        }

        await connector.authenticate(config)
        print("Connector configured with API key for higher rate limits")

        # Now perform a search with the configured connector
        results = await connector.search("machine learning in healthcare", limit=2)
        print(f"Search completed: Found {results['total_results']} results")

    except Exception as e:
        print(f"Configuration failed: {e}")
        print("Note: This is expected if you don't have a valid API key")

    finally:
        await connector.close()


async def error_handling_example():
    """Demonstrate error handling."""
    print("\n=== Error Handling Example ===")

    connector = PubMedConnector()

    try:
        # Try to get a non-existent document
        print("Attempting to retrieve non-existent document...")
        doc = await connector.get_by_id("99999999")

        if doc.get('error'):
            print(f"Expected error: {doc['error']}")
        else:
            print("Unexpected: Document found")

        # Try an invalid search query
        print("\nAttempting invalid search query...")
        results = await connector.search("", limit=1)

        if results.get('error'):
            print(f"Expected error: {results['error']}")
        else:
            print(f"Unexpected: Search succeeded with {results['total_results']} results")

    finally:
        await connector.close()


async def main():
    """Run all examples."""
    print("PubMed Connector Examples")
    print("=" * 50)

    try:
        # Run basic search and get document IDs
        doc_ids = await basic_search_example()

        # Retrieve detailed document information
        await document_retrieval_example(doc_ids)

        # Demonstrate advanced search
        await advanced_search_example()

        # Demonstrate MeSH term search
        await mesh_search_example()

        # Demonstrate journal search
        await journal_search_example()

        # Demonstrate incremental updates
        await incremental_updates_example()

        # Demonstrate configuration
        await configuration_example()

        # Demonstrate error handling
        await error_handling_example()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"\nError: {e}")
        print("This might be due to network issues or API rate limits.")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())

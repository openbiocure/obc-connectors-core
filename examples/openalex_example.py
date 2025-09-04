#!/usr/bin/env python3
"""
OpenAlex Connector Example

This example demonstrates how to use the OpenAlex connector to search for
academic papers and retrieve detailed information about them.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from connectors.openalex.connector import OpenAlexConnector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def basic_search_example():
    """Demonstrate basic search functionality."""
    print("=== Basic Search Example ===")
    
    connector = OpenAlexConnector()
    
    try:
        # Search for papers about machine learning
        results = await connector.search("machine learning", limit=5)
        
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
    
    connector = OpenAlexConnector()
    
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
            print(f"DOI: {doc.get('doi', 'N/A')}")
            print(f"Publication Date: {doc.get('publication_date', 'N/A')}")
            print(f"URL: {doc.get('url', 'N/A')}")
            
            # Display authors
            authors = doc.get('authors', [])
            print(f"\nAuthors ({len(authors)}):")
            for i, author in enumerate(authors[:3], 1):  # Show first 3 authors
                print(f"  {i}. {author['name']}")
                if author.get('orcid'):
                    print(f"     ORCID: {author['orcid']}")
                if author.get('affiliation'):
                    print(f"     Affiliation: {author['affiliation']}")
            
            # Display concepts/keywords
            concepts = doc.get('metadata', {}).get('concepts', [])
            if concepts:
                print(f"\nKey Concepts (top 5):")
                for i, concept in enumerate(concepts[:5], 1):
                    print(f"  {i}. {concept['display_name']} (score: {concept['score']:.3f})")
            
            # Display citation information
            cited_by = doc.get('metadata', {}).get('cited_by_count', 0)
            print(f"\nCitation Count: {cited_by}")
            
            # Display open access information
            is_oa = doc.get('metadata', {}).get('is_oa', False)
            print(f"Open Access: {'Yes' if is_oa else 'No'}")
            if is_oa:
                oa_url = doc.get('metadata', {}).get('oa_url')
                if oa_url:
                    print(f"Open Access URL: {oa_url}")
        
    finally:
        await connector.close()


async def author_search_example():
    """Demonstrate author search functionality."""
    print("\n=== Author Search Example ===")
    
    connector = OpenAlexConnector()
    
    try:
        # Search for works by a specific author
        author_name = "Seyedali Mirjalili"
        results = await connector.search_by_author(author_name, limit=3)
        
        print(f"Searching for works by: {author_name}")
        print(f"Found {results['total_results']} total works")
        print(f"Retrieved {len(results['document_ids'])} document IDs:")
        
        for i, doc_id in enumerate(results['document_ids'], 1):
            print(f"  {i}. {doc_id}")
        
    except Exception as e:
        print(f"Author search failed: {e}")
        print("Note: This might be due to API rate limits or query formatting")
    
    finally:
        await connector.close()


async def institution_search_example():
    """Demonstrate institution search functionality."""
    print("\n=== Institution Search Example ===")
    
    connector = OpenAlexConnector()
    
    try:
        # Search for works from a specific institution
        institution_name = "Stanford University"
        results = await connector.search_by_institution(institution_name, limit=3)
        
        print(f"Searching for works from: {institution_name}")
        print(f"Found {results['total_results']} total works")
        print(f"Retrieved {len(results['document_ids'])} document IDs:")
        
        for i, doc_id in enumerate(results['document_ids'], 1):
            print(f"  {i}. {doc_id}")
        
    except Exception as e:
        print(f"Institution search failed: {e}")
        print("Note: This might be due to API rate limits or query formatting")
    
    finally:
        await connector.close()


async def incremental_updates_example():
    """Demonstrate incremental updates functionality."""
    print("\n=== Incremental Updates Example ===")
    
    connector = OpenAlexConnector()
    
    try:
        # Get works published in the last 30 days
        since_date = datetime.now() - timedelta(days=30)
        print(f"Searching for works published since: {since_date.strftime('%Y-%m-%d')}")
        
        results = await connector.get_updates(since_date)
        
        print(f"Found {results['total_results']} new works")
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
    
    connector = OpenAlexConnector()
    
    try:
        # Configure with email for better rate limits
        config = {
            "email": "example@example.com"  # Replace with your email
        }
        
        await connector.authenticate(config)
        print("Connector configured with email for better rate limits")
        
        # Now perform a search with the configured connector
        results = await connector.search("artificial intelligence", limit=2)
        print(f"Search completed: Found {results['total_results']} results")
        
    finally:
        await connector.close()


async def main():
    """Run all examples."""
    print("OpenAlex Connector Examples")
    print("=" * 50)
    
    try:
        # Run basic search and get document IDs
        doc_ids = await basic_search_example()
        
        # Retrieve detailed document information
        await document_retrieval_example(doc_ids)
        
        # Demonstrate author search
        await author_search_example()
        
        # Demonstrate institution search
        await institution_search_example()
        
        # Demonstrate incremental updates
        await incremental_updates_example()
        
        # Demonstrate configuration
        await configuration_example()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"\nError: {e}")
        print("This might be due to network issues or API rate limits.")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())

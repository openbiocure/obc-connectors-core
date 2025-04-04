"""
Example demonstrating document processing with GROBID.
This example shows:
- Setting up the GROBID processor
- Processing a PDF document
- Extracting structured data
- Storing results
"""
import asyncio
from pathlib import Path
from herpai_ingestion.processors.grobid import GrobidProcessor
from herpai_ingestion.storage.azure import AzureStorage
from herpai_ingestion.services.processing import ProcessingService

async def main():
    # Initialize services
    processor = GrobidProcessor(
        grobid_url="http://localhost:8070",  # Default GROBID server URL
        timeout=300  # 5 minutes timeout for large documents
    )
    
    storage = AzureStorage(
        account_name="your_account",
        account_key="your_key",
        container_name="processed-papers"
    )
    
    # Create processing service
    processing_service = ProcessingService(
        processor=processor,
        storage=storage
    )
    
    # Example PDF path
    pdf_path = Path("path/to/your/paper.pdf")
    
    # Process document
    try:
        result = await processing_service.process_document(pdf_path)
        
        # Print extracted metadata
        print("Document processed successfully!")
        print(f"\nTitle: {result.title}")
        print(f"Authors: {', '.join(result.authors)}")
        print(f"Abstract: {result.abstract[:200]}...")
        print(f"\nReferences: {len(result.references)} found")
        
        # Print some extracted text sections
        print("\nSection Examples:")
        for section in result.sections[:3]:  # First 3 sections
            print(f"\n{section.title}:")
            print(f"{section.text[:200]}...")
        
        # Store processed result
        storage_path = await processing_service.store_processed_document(result)
        print(f"\nStored processed document at: {storage_path}")
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 
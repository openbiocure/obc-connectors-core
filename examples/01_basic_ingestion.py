"""
Basic example demonstrating how to use the ingestion service with PubMed.
This example shows:
- Using HerpAI-Lib for configuration and core functionality
- Connecting to PubMed
- Running a simple ingestion job
- Monitoring progress
"""
import asyncio
from pathlib import Path
from openbiocure_corelib.core.engine import Engine
from openbiocure_corelib.config.app_config import AppConfig
from herpai_ingestion.services.ingestion import IngestionService
from herpai_ingestion.connectors.pubmed import PubMedConnector
from herpai_ingestion.storage.azure import AzureStorage

async def main():
    # Initialize the core engine
    engine = Engine.initialize()
    await engine.start()
    
    try:
        # Get configuration using core library
        config = AppConfig.get_instance()
        
        # Initialize services using dependency injection
        connector = engine.resolve(PubMedConnector)
        storage = engine.resolve(AzureStorage)
        ingestion_service = engine.resolve(IngestionService)
        
        # Start ingestion job using config
        job_id = await ingestion_service.start_ingestion(
            source="pubmed",
            query=config.sources.pubmed.default_query,
            limit=config.sources.pubmed.max_results
        )
        
        # Monitor progress
        while True:
            status = await ingestion_service.get_job_status(job_id)
            print(f"Progress: {status.progress}%, Documents: {status.processed_count}")
            
            if status.is_complete:
                break
                
            await asyncio.sleep(5)
        
        # Get results
        results = await ingestion_service.get_job_results(job_id)
        print(f"\nCompleted! Found {len(results)} documents")
        
        # Print first document details
        if results:
            doc = results[0]
            print(f"\nExample document:")
            print(f"Title: {doc.title}")
            print(f"Authors: {', '.join(doc.authors)}")
            print(f"Abstract: {doc.abstract[:200]}...")
            
    finally:
        # Cleanup
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Example demonstrating how to set up and run workers for distributed processing.
This example shows:
- Using HerpAI-Lib for configuration and core functionality
- Setting up workers with retry and failure handling
- Monitoring worker status and progress
- Handling rate limits and batch sizes
"""
import asyncio
from pathlib import Path
from openbiocure_corelib.core.engine import Engine
from openbiocure_corelib.config.app_config import AppConfig
from herpai_ingestion.workers.ingestion_worker import IngestionWorker
from herpai_ingestion.workers.processing_worker import ProcessingWorker
from herpai_ingestion.repositories.ingestion_state_repository import IIngestionStateRepository
from herpai_ingestion.models.ingestion_state import IngestionState

async def run_workers():
    # Initialize the core engine
    engine = Engine.initialize()
    await engine.start()
    
    try:
        # Get configuration using core library
        config = AppConfig.get_instance()
        
        # Initialize services using dependency injection
        ingestion_worker = engine.resolve(IngestionWorker)
        processing_worker = engine.resolve(ProcessingWorker)
        state_repo = engine.resolve(IIngestionStateRepository)
        
        # Start workers
        print("Starting workers...")
        
        try:
            # Run both workers concurrently
            await asyncio.gather(
                ingestion_worker.run(),
                processing_worker.run(),
                monitor_ingestion_states(state_repo)  # Monitor ingestion states
            )
        except KeyboardInterrupt:
            print("\nShutting down workers...")
            await ingestion_worker.shutdown()
            await processing_worker.shutdown()
        except Exception as e:
            print(f"Error running workers: {str(e)}")
            raise
            
    finally:
        await engine.stop()

async def monitor_ingestion_states(state_repo: IIngestionStateRepository):
    """Monitor ingestion states and handle retries."""
    while True:
        try:
            # Get active ingestion states
            active_states = await state_repo.find_active()
            
            print("\nActive Ingestion States:")
            for state in active_states:
                # Print state details
                print(f"\nJob ID: {state.job_id}")
                print(f"Status: {state.status}")
                print(f"Progress: {state.documents_processed}/{state.documents_total or 'unknown'}")
                print(f"Retries: {state.retries}")
                
                if state.error_message:
                    print(f"Last Error: {state.error_message}")
                
                # Handle failed states that can be retried
                if (state.status == "failed" and 
                    state.retries < config.rabbitmq.retry.max_attempts):
                    print(f"Retrying failed job {state.job_id}")
                    await state_repo.increment_retry(state.id)
                    # Reset status to pending for retry
                    await state_repo.update_status(state.id, "pending")
            
            await asyncio.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"Error monitoring states: {str(e)}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_workers()) 
you are an Architect that is responsible to design a solution design document stored in Readme.md you job is to design the following system.

A flexible and scalable library for ingesting, processing, and storing biomedical data from various sources, built for the HerpAI Project to enrich AI Agents with domain-specific knowledge and power Retrieval-Augmented Generation (RAG) systems.


## Overview

HerpAI-Ingestion is a powerful toolkit designed for the extraction, transformation, and loading (ETL) of biomedical data from multiple public repositories. Built on top of the OpenBioCure-CoreLib, it implements a unified interface for accessing diverse data sources while maintaining a clean separation between business logic and deployment infrastructure.

### Purpose and Integration with HerpAI Project

This library serves as a critical component in the HerpAI ecosystem, with the primary purpose of:

1. **Knowledge Acquisition**: Systematically gathering domain-specific knowledge about herpes viruses and related treatments from authoritative sources
2. **Data Enrichment**: Processing and structuring this data for consumption by AI systems
3. **RAG Enablement**: Providing the knowledge foundation for Retrieval-Augmented Generation (RAG) systems that power HerpAI Agents
4. **Domain Specialization**: Ensuring HerpAI's AI capabilities are grounded in accurate, up-to-date biomedical information

The ingested data flows directly into HerpAI's knowledge stores, allowing AI agents to retrieve and reference specific scientific information when answering queries, making recommendations, or analyzing research trends.

## Architecture

HerpAI-Ingestion follows a modular, decoupled architecture with these key components:

1. **Connector SDK**: A lightweight SDK that defines interfaces and base classes for data source connectors
2. **Core Ingestion System**: The main application that orchestrates data ingestion and processing
3. **Connector Plugins**: Individual implementations for different data sources (PubMed, ClinicalTrials, etc.)
4. **Message Queue**: Optional RabbitMQ integration for distributed processing

### Connector Architecture

The system uses a plugin-based connector architecture:

- **Connector SDK**: Defines the `IConnector` interface and common functionality
- **Connector Specifications**: Each connector includes a YAML specification file that defines its capabilities and configuration
- **Connector Registry**: Discovers and loads available connectors at runtime
- **Decoupled Implementation**: Connectors depend only on the SDK, not on the ingestion system

This architecture ensures that:
- Connectors can be developed independently
- The ingestion system can evolve without breaking connectors
- New data sources can be added without modifying the core system


## Features

- **Multiple Source Connectors**: Unified interface for PubMed, Europe PMC, ClinicalTrials.gov, and more
- **Document Processing**: PDF parsing and structured extraction using GROBID
- **Data Lake Storage**: Support for S3, NFS, and Azure Blob Storage backends
- **Metadata Cataloging**: Database storage for structured metadata and querying
- **Deployment Flexibility**: Run locally, in containers, or in Kubernetes
- **Distributed Processing**: Optional RabbitMQ integration for scalable processing
- **Scheduled Ingestion**: Cron-based scheduling for automated data updates
- **Retry Mechanisms**: Comprehensive error handling with exponential backoff

## Directory Structure needs to follow this director

```sh
herpai-ingestion/
├── README.md
├── pyproject.toml
├── LICENSE
│
├── herpai_connector_sdk/        # The connector SDK (future separate package)
│   ├── __init__.py
│   ├── interfaces.py            # Core interfaces (IConnector)
│   ├── base.py                  # Base implementations (BaseConnector)
│   ├── models.py                # Data models (Document)
│   ├── exceptions.py            # Custom exceptions
│   └── utils/                   # Utilities for connectors
│
├── herpai_ingestion/            # Main ingestion system
│   ├── __init__.py
│   ├── cli/                     # Command-line interface
│   ├── services/                # Business logic services
│   ├── workers/                 # Background workers
│   └── utils/                   # Utility functions
│
├── connectors/                  # All connectors in one place for now
│   ├── pubmed/
│   │   ├── __init__.py
│   │   ├── connector.py         # PubMed connector implementation
│   │   └── connector.yaml       # Specification file
│   ├── clinicaltrials/
│   │   ├── __init__.py
│   │   ├── connector.py
│   │   └── connector.yaml
│   └── europepmc/
│       ├── __init__.py
│       ├── connector.py
│       └── connector.yaml
│
└── tests/                       # Centralized tests
    ├── sdk/
    ├── ingestion/
    └── connectors/
```


### Basic Usage

```python
from herpai_ingestion.services import IngestionService
from herpai_ingestion.workers import LocalProcessExecutor
import asyncio

async def main():

    ## find classes of connectors
    connectors = type_finder.find_classes_of_type(BaseConnector, only_concrete=True)

    # Create a local executor for direct processing
    executor = LocalProcessExecutor()

    # Resolve the storage
    azure_storage = engine.resolve(AzureStorage)

    # Resolve the connector registry
    connector_registry = engine.resolve(ConnectorRegistry)

    for connector in connectors:
        try:
            # get the connector
            connector_instance = connector_class()

             # Create ingestion service
            service = IngestionService(task_executor=executor)

            # ingest
            result = await service.ingest(
                    query="herpes simplex virus treatment",
                    limit=100
            )
            # log
            print(f"Processed {result['documents_processed']} documents")
        except Exception as e:
            logger.error(f"Error creating connector {connector_class.__name__}: {str(e)}")


print(f"Processed {result['documents_processed']} documents")

if __name__ == "__main__":
    asyncio.run(main())
```


### CLI Usage

```bash
# Basic ingestion (processes locally)
openbiocure ingest --source pubmed --query "HSV1 pathogenesis" --limit 100

# Enqueue task for asynchronous processing
openbiocure ingest --source pubmed --query "HSV2 vaccine" --limit 100 --async

# Start a worker to process queued tasks
openbiocure worker start --rabbitmq-url amqp://guest:guest@localhost/

# Schedule regular ingestion
openbiocure scheduler add --name "daily-pubmed" --source pubmed --query "herpes zoster" --schedule "0 0 * * *"
```

## Example Config

```yaml
## database section is handled by the openbiocure_corelib
database:
  type: sqlite
  connection: ":memory:"  # In-memory SQLite database

storage:
  type: azure
  azure:
    account_name: your_account_name
    account_key: your_account_key
    container_name: herpai-datalake
    prefix: documents/

## here we only check if a connector is enabled or not!
## detailed configuration about the connector is found in the connector.yaml
connectors:
  pubmed:
    enabled: true
  europepmc:
    enabled: true
  clinicaltrials:
    enabled: true

rabbitmq:
  host: localhost
  port: 5672
  username: guest
  password: guest

scheduler:
  enabled: true
  jobs:
    - source: pubmed
      query: "herpes simplex virus"
      schedule: "0 1 * * *"  # Daily at 1 AM
      limit: 1000
```

## Deployment Models

HerpAI-Ingestion supports multiple deployment models:

### Local Development

Run everything locally for development and testing:

```bash
# Start RabbitMQ (optional)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management

# Start workers locally
herpai worker start

# Run ingestion
herpai ingest --source pubmed --query "HSV transmission" --async
```

### Docker Compose

For a self-contained deployment:

```yaml
# docker-compose.yml
version: '3'

services:
  rabbitmq:
    image: rabbitmq:management
    ports:
      - "5672:5672"
      - "15672:15672"

  api:
    image: herpai-ingestion:latest
    command: python -m herpai_ingestion.api
    ports:
      - "8000:8000"
    environment:
      - RABBITMQ_HOST=rabbitmq
    volumes:
      - ./config.yaml:/app/config.yaml

  worker:
    image: herpai-ingestion:latest
    command: python -m herpai_ingestion.cli worker start
    environment:
      - RABBITMQ_HOST=rabbitmq
    volumes:
      - ./config.yaml:/app/config.yaml
```

### Kubernetes

For production environments:

```bash
# Deploy using Helm
helm install herpai-ingestion ./charts/herpai-ingestion
```

The Kubernetes deployment includes:
- API server deployment
- Worker deployment
- RabbitMQ StatefulSet (or external service)
- Configuration via ConfigMaps and Secrets

## Extending the System

### Adding a New Source


1. Create a connector class:

```python
# herpai_ingestion/connectors/new_source.py
from .base import BaseConnector

## The BaseConnector must cover all possible operations as they will be used by the orchestration class.

class NewSourceConnector(BaseConnector):
    async def install(self) -> None:
        """Install Europe PMC connector dependencies or setup."""
        ### call super here
        ### the idea is that the supper class will install the definition of the connector in the database.
        ### so that we can track runs, executions, and collect logs and audit them
        ### a custom connector might also have assets, or something am not aware of as of now
       pass;


    async def uninstall(self) -> None:
        """Cleanup Europe PMC connector resources."""
        pass;

    async def search(self, query, limit=None):
        # Implementation...
        pass

    async def get_by_id(self, id):
        # Implementation...
        pass

    async def authenticate(self, config):
        # Implementation
        pass
```

```yaml
name: pubmed_plus
display_name: PubMed Plus
description: Connects to the PubMed API with advanced functionality requiring authentication
version: 1.0.0

capabilities:
  supports_fulltext: true
  supports_advanced_search: true
  supports_date_filtering: true
  requires_authentication: true  # Indicates authentication is required

auth:
  type: api_key  # Type of authentication (options: none, api_key, oauth, basic)
  api_key_parameter: api_key  # Name of the parameter for API key
  api_key_location: query  # Where to place the API key (options: query, header, cookie)
  header_prefix: null  # Prefix for header-based auth (e.g., "Bearer" for Bearer tokens)

  # For OAuth authentication
  # oauth:
  #   auth_url: https://example.com/oauth/authorize
  #   token_url: https://example.com/oauth/token
  #   scope: "read write"

api:
  base_url: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
  rate_limit:
    requests_per_second: 3
    with_api_key: 10

configuration:
  properties:
    - name: api_key
      type: string
      required: true  # This is required since auth is needed
      description: NCBI API key for authentication and higher rate limits
      sensitive: true  # Indicates this is sensitive data that should be secured

    - name: batch_size
      type: integer
      required: false
      default: 100
      description: Number of items to retrieve in each batch

    # For OAuth or other more complex auth types
    # - name: client_id
    #   type: string
    #   required: true
    #   description: OAuth client ID
    #   sensitive: true
    #
    # - name: client_secret
    #   type: string
    #   required: true
    #   description: OAuth client secret
    #   sensitive: true
```


These specifications serve multiple purposes:
- **Documentation**: Clear description of connector capabilities
- **Validation**: Ensure connectors implement required features
- **Code Generation**: Auto-generate connector skeletons
- **Configuration**: Define configuration options and validation rules# HerpAI-Ingestion

## OpenBioCure Core Lib

The system uses the OpenBioCure_CoreLib and this is how it gets updated

```
update-corelib: check-venv ## Uninstall and reinstall openbiocure-corelib from local dist, pass VERSION=x.y.z
	@echo "$(BLUE)Updating openbiocure-corelib to version $(VERSION)...$(NC)"
	$(VENV_RUN) pip uninstall -y openbiocure-corelib
	$(VENV_RUN) pip install /Users/mohammad_shehab/develop/HerpAI-Lib/dist/openbiocure_corelib-$(VERSION)-py3-none-any.whl
	@echo "$(GREEN)openbiocure-corelib updated to version $(VERSION).$(NC)"
```

### Repository Pattern

```py
"""
Basic Todo Example

This example demonstrates the core repository pattern with entity creation and injection.
"""
import asyncio
import uuid
from typing import Optional, List, Protocol
from sqlalchemy.orm import Mapped, mapped_column

from examples.domain.todo_entity import Todo
from examples.repository.todo_repository import ITodoRepository, CompletedTodoSpecification, TitleContainsSpecification
from openbiocure_corelib import engine

async def main():

    import logging

    # Configure the root logger
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG to see all messages
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Output to console
        ]
    )

    # Get the engine logger specifically
    logger = logging.getLogger('openbiocure_corelib.core.engine')

    # Initialize and start the engine
    engine.initialize()
    await engine.start()

    # Resolve the todo repository
    todo_repository =  engine.resolve(ITodoRepository)

    # Create a Todo entity
    todo = Todo(
        id=str(uuid.uuid4()),
        title="Learn HerpAI-Lib",
        description="Implement repository pattern with dependency injection",
        completed=False
    )

    # Save the todo
    created_todo = await todo_repository.create(todo)
    print(f"Created Todo: {created_todo.title} (ID: {created_todo.id})")

    # Create another todo
    another_todo = Todo(
        title="Master HerpAI-Lib",
        description="Build a complete application",
        completed=False
    )
    created_another = await todo_repository.create(another_todo)

    # Update a todo by marking it completed
    created_todo.completed = True
    updated_todo = await todo_repository.update(created_todo)
    print(f"Updated Todo: {updated_todo.title} (Completed: {updated_todo.completed})")

    completed_todos = await todo_repository.find(CompletedTodoSpecification())
    print(f"Found {len(completed_todos)} completed todos")

    # Find todos by title
    learn_todos = await todo_repository.find(TitleContainsSpecification("Learn"))
    print(f"Found {len(learn_todos)} todos with 'Learn' in the title")

if __name__ == "__main__":
    asyncio.run(main())

```

### Create a startupTask

```py
"""
Custom Startup Task Example

This example demonstrates how to create and use custom startup tasks
with auto-discovery, ordering, and configuration.
"""
import asyncio
import logging
from openbiocure_corelib import engine
from openbiocure_corelib.core.startup import StartupTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Define a custom startup task
class DatabaseInitializationTask(StartupTask):
    """Custom startup task to initialize the database."""

    # Run after configuration is loaded (order 10-20)
    order = 30

    async def execute(self) -> None:
        """Execute the database initialization."""
        logger.info("Initializing database...")

        # Get configuration parameters from task config
        schema_name = self._config.get('schema', 'public')
        create_tables = self._config.get('create_tables', True)

        logger.info(f"Using schema: {schema_name}")
        logger.info(f"Create tables: {create_tables}")

        # In a real app, you'd create database tables here
        # ...

# Define another custom startup task
class ModelInitializationTask(StartupTask):
    """Custom startup task to initialize AI models."""

    # Run after database initialization
    order = 40

    async def execute(self) -> None:
        """Execute the model initialization."""
        logger.info("Initializing AI models...")

        # Get configuration parameters
        default_model = self._config.get('default_model', 'default')
        preload = self._config.get('preload', False)

        logger.info(f"Default model: {default_model}")
        logger.info(f"Preload models: {preload}")

        # In a real app, you'd initialize models here
        # ...

async def main():
    # Initialize and start the engine
    # The engine will auto-discover our tasks
    engine.initialize()
    await engine.start()

    # Print information about discovered tasks
    print("\nStartup Tasks:")
    for task_name, task in engine._startup_task_executor._tasks.items():
        status = "Enabled" if task.enabled else "Disabled"
        print(f"- {task_name} (Order: {task.order}, Status: {status})")

    # Print startup task configuration
    from openbiocure_corelib.config.yaml_config import YamlConfig
    config = engine.resolve(YamlConfig)

    print("\nStartup Task Configuration:")
    startup_tasks_config = config.get('startup_tasks', {})
    for task_name, task_config in startup_tasks_config.items():
        print(f"\n{task_name}:")
        for key, value in task_config.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())

```

### Database Operations

```py
"""
Database Operations Example

This example demonstrates how to perform more advanced
database operations using the repository pattern with entities.
"""
import asyncio
import uuid
from typing import Optional, List, Protocol
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from openbiocure_corelib import engine
from openbiocure_corelib.data.entity import BaseEntity
from openbiocure_corelib.data.repository import IRepository
from openbiocure_corelib.data.specification import Specification

# Define entities
class User(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(nullable=True)

class Post(BaseEntity):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    published: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

# Define repository interfaces
class IUserRepository(IRepository[User], Protocol):
    async def find_by_username(self, username: str) -> Optional[User]: ...
    async def find_by_email(self, email: str) -> Optional[User]: ...

class IPostRepository(IRepository[Post], Protocol):
    async def find_by_user_id(self, user_id: str) -> List[Post]: ...
    async def find_published(self) -> List[Post]: ...
    async def publish(self, post: Post) -> Post: ...

# Define specifications
class UserByUsernameSpecification(Specification[User]):
    def __init__(self, username: str):
        self.username = username

    def to_expression(self):
        return User.username == self.username

class UserByEmailSpecification(Specification[User]):
    def __init__(self, email: str):
        self.email = email

    def to_expression(self):
        return User.email == self.email

class PostByUserIdSpecification(Specification[Post]):
    def __init__(self, user_id: str):
        self.user_id = user_id

    def to_expression(self):
        return Post.user_id == self.user_id

class PublishedPostSpecification(Specification[Post]):
    def to_expression(self):
        return Post.published == True

async def main():
    # Initialize and start the engine
    engine.initialize()
    await engine.start()

    # Resolve repositories
    user_repository = engine.resolve(IUserRepository)
    post_repository = engine.resolve(IPostRepository)

    print("Database Operations Example:")
    print("===========================")

    # Create a user entity
    user = User(
        id=str(uuid.uuid4()),
        username="johndoe",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe"
    )

    # Save the user
    created_user = await user_repository.create(user)
    print(f"\nCreated user: {created_user.first_name} {created_user.last_name} ({created_user.username})")

    # Create post entities
    post1 = Post(
        id=str(uuid.uuid4()),
        title="First Post",
        content="This is my first post!",
        published=False,
        user_id=created_user.id
    )

    post2 = Post(
        title="Second Post",
        content="This is my second post!",
        published=False,
        user_id=created_user.id
    )

    # Save posts
    created_post1 = await post_repository.create(post1)
    created_post2 = await post_repository.create(post2)

    print(f"\nCreated posts: {created_post1.title}, {created_post2.title}")

    # Publish a post
    created_post1.published = True
    published_post = await post_repository.update(created_post1)
    print(f"\nPublished post: {published_post.title}")

    # Find posts by user
    user_posts = await post_repository.find(PostByUserIdSpecification(created_user.id))
    print(f"\nUser has {len(user_posts)} posts:")
    for post in user_posts:
        status = "Published" if post.published else "Draft"
        print(f"- {post.title} ({status})")

    # Find published posts
    published_posts = await post_repository.find(PublishedPostSpecification())
    print(f"\nPublished posts: {len(published_posts)}")

    # Find user by username
    found_user = await user_repository.find_one(UserByUsernameSpecification("johndoe"))
    if found_user:
        print(f"\nFound user by username: {found_user.first_name} {found_user.last_name}")

if __name__ == "__main__":
    asyncio.run(main())
```

# OpenBioCure CoreLib API Documentation

| Module                                                | Class                       | Class Description                       | Method                               | Method Description                    |
| ----------------------------------------------------- | --------------------------- | --------------------------------------- | ------------------------------------ | ------------------------------------- |
| `openbiocure_corelib.data.repository`                 | `IRepository`               | *No docstring*                          | *various*                            | *See source*                          |
| `openbiocure_corelib.data.repository`                 | `Repository`                | *No docstring*                          | *various*                            | *See source*                          |
| `openbiocure_corelib.data.entity`                     | `BaseEntity`                | *No docstring*                          | *various*                            | *See source*                          |
| `openbiocure_corelib.data.specification`              | `ISpecification`            | *No docstring*                          | `is_satisfied_by`                    | *Inline implementation*               |
| `openbiocure_corelib.data.specification`              | `Specification`             | *No docstring*                          | `is_satisfied_by`                    | Default implementation                |
|                                                       |                             |                                         | `to_expression`                      | Convert to SQLAlchemy expression      |
|                                                       |                             |                                         | `and_`                               | Combine with AND                      |
|                                                       |                             |                                         | `or_`                                | Combine with OR                       |
| `openbiocure_corelib.data.specification`              | `AndSpecification`          | *No docstring*                          | `__init__`                           | Initialize with two specs             |
|                                                       |                             |                                         | `is_satisfied_by`                    | Logical AND of specs                  |
|                                                       |                             |                                         | `to_expression`                      | SQLAlchemy AND expression             |
| `openbiocure_corelib.data.specification`              | `OrSpecification`           | *No docstring*                          | `__init__`                           | Initialize with two specs             |
|                                                       |                             |                                         | `is_satisfied_by`                    | Logical OR of specs                   |
|                                                       |                             |                                         | `to_expression`                      | SQLAlchemy OR expression              |
| `openbiocure_corelib.data.db_context`                 | `IDbContext`                | Database context interface              | *various*                            | *See source*                          |
| `openbiocure_corelib.data.db_context`                 | `DbContext`                 | Async SQLAlchemy context                | `session`                            | Get current session                   |
|                                                       |                             |                                         | `__init__`                           | Initialize DbContext                  |
|                                                       |                             |                                         | `_initialize_sync`                   | Sync init                             |
|                                                       |                             |                                         | `session` (static)                   | Get current session                   |
| `openbiocure_corelib.config.app_config`               | `ConfigError`               | Base exception for configuration errors | *None*                               | *None*                                |
| `openbiocure_corelib.config.app_config`               | `DatabaseConfig`            | Database configuration parameters       | `connection_string`                  | Generate SQLAlchemy connection string |
|                                                       |                             |                                         | `from_dict`                          | Create from dict                      |
| `openbiocure_corelib.config.app_config`               | `AgentConfig`               | Agent-specific configuration            | `from_dict`                          | Create from dict                      |
| `openbiocure_corelib.config.app_config`               | `AppConfig`                 | Application configuration container     | `get_instance`                       | Singleton accessor                    |
|                                                       |                             |                                         | `load`                               | Load from YAML                        |
|                                                       |                             |                                         | `get_agent`                          | Get agent config                      |
|                                                       |                             |                                         | `get_db_session`                     | Get DB session                        |
| `openbiocure_corelib.config.environment`              | `Environment`               | Helper for environment variables        | `get`                                | Get env var                           |
|                                                       |                             |                                         | `get_bool`                           | Get env var as bool                   |
|                                                       |                             |                                         | `get_int`                            | Get env var as int                    |
| `openbiocure_corelib.config.yaml_config`              | `YamlConfig`                | YAML-based config manager               | `get_instance`                       | Singleton accessor                    |
|                                                       |                             |                                         | `__init__`                           | Initialize                            |
|                                                       |                             |                                         | `load`                               | Load YAML config                      |
|                                                       |                             |                                         | `get`                                | Get config value                      |
|                                                       |                             |                                         | `get_connection_string`              | Generate DB connection string         |
|                                                       |                             |                                         | `get_agent_configs`                  | Get all agent configs                 |
|                                                       |                             |                                         | `get_agent_config`                   | Get specific agent config             |
| `openbiocure_corelib.config.settings`                 | `Settings`                  | *No docstring*                          | `__init__`                           | Initialize                            |
|                                                       |                             |                                         | `get`                                | Get setting                           |
|                                                       |                             |                                         | `set`                                | Set setting                           |
|                                                       |                             |                                         | `save`                               | Save settings                         |
| `openbiocure_corelib.core.service_collection`         | `ServiceCollection`         | *No docstring*                          | `__init__`                           | Initialize                            |
|                                                       |                             |                                         | `add_singleton`                      | Register singleton                    |
|                                                       |                             |                                         | `add_scoped`                         | Register scoped                       |
|                                                       |                             |                                         | `add_transient`                      | Register transient                    |
|                                                       |                             |                                         | `get_service`                        | Get service                           |
| `openbiocure_corelib.core.singleton`                  | `Singleton`                 | *No docstring*                          | `get_instance`                       | Get singleton instance                |
| `openbiocure_corelib.core.type_finder`                | `ITypeFinder`               | Interface for finding types             | `find_classes_of_type`               | Find classes                          |
|                                                       |                             |                                         | `find_generic_implementations`       | Find generic impls                    |
| `openbiocure_corelib.core.type_finder`                | `TypeFinder`                | *No docstring*                          | `__init__`                           | Initialize                            |
|                                                       |                             |                                         | `_is_likely_startup_module`          | Check startup module                  |
|                                                       |                             |                                         | `_scan_loaded_modules`               | Scan modules                          |
|                                                       |                             |                                         | `load_module`                        | Load module                           |
|                                                       |                             |                                         | `find_classes_of_type`               | Find classes                          |
|                                                       |                             |                                         | `find_generic_implementations`       | Find generic impls                    |
|                                                       |                             |                                         | `_is_assignable_to`                  | Check assignability                   |
| `openbiocure_corelib.core.engine`                     | `Engine`                    | *No docstring*                          | `__init__`                           | Initialize engine                     |
|                                                       |                             |                                         | `config`                             | Get config                            |
|                                                       |                             |                                         | `initialize`                         | Initialize singleton                  |
|                                                       |                             |                                         | `current`                            | Get current engine                    |
|                                                       |                             |                                         | `_complete_repository_registrations` | Register repos                        |
|                                                       |                             |                                         | `_create_repository_instance`        | Create repo instance                  |
|                                                       |                             |                                         | `_create_memory_session`             | Create memory session                 |
|                                                       |                             |                                         | `resolve`                            | Resolve service                       |
|                                                       |                             |                                         | `create_scope`                       | Create scope                          |
|                                                       |                             |                                         | `register`                           | Register service                      |
|                                                       |                             |                                         | `add_startup_task`                   | Add startup task                      |
|                                                       |                             |                                         | `register_module`                    | Register module                       |
|                                                       |                             |                                         | `_register_core_services`            | Register core services                |
|                                                       |                             |                                         | `_discover_and_register_entities`    | Discover entities                     |
| `openbiocure_corelib.core.service_scope`              | `ServiceScope`              | *No docstring*                          | `__init__`                           | Initialize scope                      |
|                                                       |                             |                                         | `resolve`                            | Resolve service                       |
| `openbiocure_corelib.core.configuration_startup_task` | `ConfigurationStartupTask`  | Loads YAML config                       | *various*                            | *See source*                          |
| `openbiocure_corelib.data.db_context_startup_task`    | `DatabaseSchemaStartupTask` | Creates DB schema                       | *various*                            | *See source*                          |
| `openbiocure_corelib.core.startup_task`               | `StartupTask`               | Base class for startup tasks            | `__init__`                           | Initialize                            |
|                                                       |                             |                                         | `name`                               | Name of task                          |
|                                                       |                             |                                         | `enabled`                            | Enabled status                        |
|                                                       |                             |                                         | `configure`                          | Configure task                        |
|                                                       |                             |                                         | `__init_subclass__`                  | Subclass hook                         |
| `openbiocure_corelib.core.startup_task_executor`      | `StartupTaskExecutor`       | Executes startup tasks                  | `__init__`                           | Initialize                            |
|                                                       |                             |                                         | `add_task`                           | Add task                              |
|                                                       |                             |                                         | `configure_tasks`                    | Configure tasks                       |
|                                                       |                             |                                         | `execute_all`                        | Execute tasks                         |
|                                                       |                             |                                         | `discover_tasks`                     | Discover tasks                        |
| `openbiocure_corelib.core.interfaces`                 | `IServiceScope`             | Interface for service scope             | *various*                            | *See source*                          |
|                                                       |                             |                                         | `IEngine`                            | Interface for engine                  | *various* | *See source* |


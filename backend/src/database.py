"""Database connection and utilities."""
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """Cosmos DB database wrapper."""

    def __init__(self):
        """Initialize Cosmos DB client."""
        self.client = CosmosClient(
            settings.cosmos_endpoint, credential=settings.cosmos_key
        )
        self.database = None
        self.containers = {}

    def initialize(self):
        """Initialize database and containers."""
        try:
            # Create database if not exists
            self.database = self.client.create_database_if_not_exists(
                id=settings.cosmos_database_name
            )
            logger.info(f"Database '{settings.cosmos_database_name}' ready")

            # Define containers
            container_definitions = [
                ("meetings", "/id"),
                ("tasks", "/id"),
                ("agents", "/id"),
                ("proposals", "/id"),
                ("decisions", "/id"),
                ("resources", "/id"),
                ("tech_radar_items", "/id"),
                ("code_patterns", "/id"),
                ("audit_logs", "/entity_type"),
                ("submissions", "/id"),
                ("platform_docs", "/category"),
                ("allowed_users", "/id"),
                ("access_requests", "/id"),
                ("budgets", "/id"),
                ("licenses", "/id"),
                # HMLR Memory System - Bridge Blocks (per-session topic organization)
                ("bridge_blocks", "/session_id"),
                # HMLR Memory System - User Profiles and Facts
                ("user_profiles", "/user_id"),
                ("user_facts", "/user_id"),
                # Feature Updates (What's New page)
                ("feature_updates", "/id"),
            ]

            # Create containers if not exists
            for container_name, partition_key_path in container_definitions:
                try:
                    container = self.database.create_container_if_not_exists(
                        id=container_name,
                        partition_key=PartitionKey(path=partition_key_path),
                        offer_throughput=400,
                    )
                    self.containers[container_name] = container
                    logger.info(f"Container '{container_name}' ready")
                except CosmosResourceExistsError:
                    container = self.database.get_container_client(container_name)
                    self.containers[container_name] = container
                    logger.info(f"Container '{container_name}' exists")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def get_container(self, container_name: str):
        """Get container client."""
        return self.containers.get(container_name)


# Global database instance
db = Database()

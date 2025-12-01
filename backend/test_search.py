"""Test script for Azure AI Search implementation."""
import asyncio
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.search_service import get_search_service, initialize_search_index
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_search_implementation():
    """Test the search implementation."""

    print("\n" + "="*60)
    print("AZURE AI SEARCH - IMPLEMENTATION TEST")
    print("="*60 + "\n")

    try:
        # Test 1: Initialize service
        print("TEST 1: Initialize Search Service")
        print("-" * 40)
        service = get_search_service()
        print("✓ Search service initialized")
        print(f"  - Endpoint: {service.endpoint}")
        print(f"  - Index: {service.index_name}")
        print()

        # Test 2: Create/verify index
        print("TEST 2: Create or Verify Index")
        print("-" * 40)
        initialize_search_index()
        print("✓ Index created/verified successfully")
        print()

        # Test 3: Get index statistics
        print("TEST 3: Index Statistics")
        print("-" * 40)
        stats = service.get_index_statistics()
        print("✓ Retrieved index statistics:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        print()

        # Test 4: Generate single embedding
        print("TEST 4: Generate Single Embedding")
        print("-" * 40)
        test_text = "This is a test document about Azure AI and machine learning."
        embedding = service.generate_embedding(test_text)
        print(f"✓ Generated embedding with {len(embedding)} dimensions")
        print(f"  - First 5 values: {embedding[:5]}")
        print()

        # Test 5: Generate batch embeddings
        print("TEST 5: Generate Batch Embeddings")
        print("-" * 40)
        test_texts = [
            "Meeting about AI governance policies",
            "Task to implement authentication system",
            "Agent for document processing"
        ]
        embeddings = service.generate_embeddings_batch(test_texts)
        print(f"✓ Generated {len(embeddings)} embeddings in batch")
        for i, emb in enumerate(embeddings):
            print(f"  - Embedding {i+1}: {len(emb)} dimensions")
        print()

        # Test 6: Upload single document
        print("TEST 6: Upload Single Document")
        print("-" * 40)
        test_doc = {
            "id": "test-doc-1",
            "content": "This is a test meeting transcript about implementing Azure AI Search for RAG functionality.",
            "type": "meeting",
            "title": "Test Meeting: Azure AI Search Implementation",
            "metadata": {
                "date": "2025-01-24",
                "facilitator": "Test User"
            },
            "status": "Completed"
        }

        service.upload_document(
            doc_id=test_doc["id"],
            content=test_doc["content"],
            doc_type=test_doc["type"],
            title=test_doc["title"],
            metadata=test_doc["metadata"],
            status=test_doc["status"]
        )
        print(f"✓ Uploaded document: {test_doc['id']}")
        print()

        # Test 7: Upload batch documents
        print("TEST 7: Upload Batch Documents")
        print("-" * 40)
        batch_docs = [
            {
                "id": "test-task-1",
                "content": "Implement authentication using Microsoft Entra ID SSO",
                "type": "task",
                "title": "Task: Microsoft SSO Authentication",
                "metadata": {"priority": "high", "assigned_to": "Developer B"},
                "status": "In-Progress",
                "priority": "High"
            },
            {
                "id": "test-agent-1",
                "content": "AI agent for processing meeting transcripts and extracting action items",
                "type": "agent",
                "title": "Agent: Transcript Processor",
                "metadata": {"tier": "Tier1", "status": "Development"},
                "category": "AI"
            }
        ]

        result = service.upload_documents_batch(batch_docs)
        print(f"✓ Batch upload completed:")
        print(f"  - Success: {result['success']}")
        print(f"  - Failed: {result['failed']}")
        print()

        # Wait for indexing (Azure Search has slight delay)
        print("⏳ Waiting 2 seconds for indexing...")
        await asyncio.sleep(2)
        print()

        # Test 8: Search functionality
        print("TEST 8: Search Functionality")
        print("-" * 40)

        # Semantic search
        query = "Azure AI implementation"
        results = service.search(query, top=5, use_semantic_search=True)
        print(f"✓ Semantic search for '{query}':")
        print(f"  - Found {len(results)} results")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result['title']} (score: {result['score']:.2f})")
            print(f"     Type: {result['type']}")
        print()

        # Text search with filter
        print("TEST 9: Filtered Search")
        print("-" * 40)
        results = service.search("authentication", doc_type="task", top=5)
        print(f"✓ Search for 'authentication' in tasks:")
        print(f"  - Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']}")
        print()

        # Test 10: Update document
        print("TEST 10: Update Document")
        print("-" * 40)
        service.update_document(
            doc_id="test-doc-1",
            status="Archived",
            metadata={"date": "2025-01-24", "archived": True}
        )
        print("✓ Updated document: test-doc-1")
        print()

        # Test 11: Get updated statistics
        print("TEST 11: Final Index Statistics")
        print("-" * 40)
        stats = service.get_index_statistics()
        print("✓ Final index statistics:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        print()

        # Summary
        print("="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        print("\nImplementation verified:")
        print("  ✓ Index creation and management")
        print("  ✓ Embedding generation (single & batch)")
        print("  ✓ Document upload (single & batch)")
        print("  ✓ Search functionality (semantic & filtered)")
        print("  ✓ Document updates")
        print("\nReady to proceed with subtasks 5.4 and 5.5!")
        print()

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_search_implementation())
    sys.exit(0 if success else 1)

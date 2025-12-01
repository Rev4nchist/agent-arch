"""Script to run bulk indexing of existing Cosmos DB data."""
import asyncio
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database import db
from src.indexer import index_all_data
from src.search_service import initialize_search_index
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run bulk indexing."""
    print("\n" + "="*60)
    print("BULK DATA INDEXING - Azure AI Search")
    print("="*60 + "\n")

    try:
        # Step 1: Initialize database
        print("STEP 1: Initialize Cosmos DB Connection")
        print("-" * 40)
        db.initialize()
        print("✓ Database connection established")
        print()

        # Step 2: Initialize search index
        print("STEP 2: Initialize Azure AI Search Index")
        print("-" * 40)
        initialize_search_index()
        print("✓ Search index ready")
        print()

        # Step 3: Run bulk indexing
        print("STEP 3: Bulk Index All Data")
        print("-" * 40)
        print("This will index all existing data from Cosmos DB...")
        print("  - Meetings (with chunking for long transcripts)")
        print("  - Tasks")
        print("  - Agents")
        print("  - Governance (Proposals & Decisions)")
        print()

        results = index_all_data()

        # Display results
        print("\n" + "="*60)
        print("INDEXING RESULTS")
        print("="*60)
        print()

        print(f"Meetings:    {results['meetings']['success']:3d} succeeded, {results['meetings']['failed']:3d} failed")
        print(f"Tasks:       {results['tasks']['success']:3d} succeeded, {results['tasks']['failed']:3d} failed")
        print(f"Agents:      {results['agents']['success']:3d} succeeded, {results['agents']['failed']:3d} failed")
        print(f"Governance:  {results['governance']['success']:3d} succeeded, {results['governance']['failed']:3d} failed")
        print()
        print(f"TOTAL:       {results['total']['success']:3d} succeeded, {results['total']['failed']:3d} failed")
        print()

        if results['total']['failed'] == 0:
            print("="*60)
            print("✓ ALL DOCUMENTS INDEXED SUCCESSFULLY!")
            print("="*60)
            return 0
        else:
            print("="*60)
            print(f"⚠ COMPLETED WITH {results['total']['failed']} FAILURES")
            print("="*60)
            return 1

    except Exception as e:
        print(f"\n❌ INDEXING FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

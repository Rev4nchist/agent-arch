#!/usr/bin/env python3
"""
HMLR Production Initialization Script.

Pre-deployment validation and setup for the HMLR memory system.

This script:
1. Validates configuration settings
2. Tests Azure service connectivity
3. Creates/updates the Azure AI Search index
4. Validates embedding generation
5. Runs a health check

Usage:
    python scripts/init_hmlr_production.py [--check-only] [--verbose]

Options:
    --check-only    Run validation only, don't create/update resources
    --verbose       Show detailed output
"""
import sys
import os
import argparse
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings


import platform

IS_WINDOWS = platform.system() == "Windows"

class Colors:
    GREEN = '\033[92m' if not IS_WINDOWS else ''
    RED = '\033[91m' if not IS_WINDOWS else ''
    YELLOW = '\033[93m' if not IS_WINDOWS else ''
    BLUE = '\033[94m' if not IS_WINDOWS else ''
    RESET = '\033[0m' if not IS_WINDOWS else ''
    BOLD = '\033[1m' if not IS_WINDOWS else ''


def print_status(message: str, status: str = "info"):
    symbols = {
        "ok": f"{Colors.GREEN}[OK]{Colors.RESET}",
        "fail": f"{Colors.RED}[FAIL]{Colors.RESET}",
        "warn": f"{Colors.YELLOW}[WARN]{Colors.RESET}",
        "info": f"{Colors.BLUE}[INFO]{Colors.RESET}",
    }
    print(f"  {symbols.get(status, symbols['info'])} {message}")


def print_header(message: str):
    print(f"\n{Colors.BOLD}{message}{Colors.RESET}")
    print("-" * len(message))


class HMLRProductionValidator:
    def __init__(self, verbose: bool = False, check_only: bool = False):
        self.verbose = verbose
        self.check_only = check_only
        self.errors = []
        self.warnings = []

    def log(self, message: str):
        if self.verbose:
            print(f"    {Colors.BLUE}>{Colors.RESET} {message}")

    def validate_config(self) -> bool:
        print_header("1. Configuration Validation")
        all_ok = True

        required_settings = [
            ("hmlr_enabled", True, "HMLR must be enabled"),
            ("azure_search_endpoint", None, "Azure Search endpoint required"),
            ("azure_search_api_key", None, "Azure Search API key required"),
            ("azure_openai_endpoint", None, "Azure OpenAI endpoint required"),
            ("azure_openai_api_key", None, "Azure OpenAI API key required"),
            ("azure_openai_embeddings_deployment", None, "Embeddings deployment required"),
        ]

        for setting_name, expected_value, error_msg in required_settings:
            value = getattr(settings, setting_name, None)

            if expected_value is not None:
                if value != expected_value:
                    print_status(f"{setting_name}: {value} (expected: {expected_value})", "fail")
                    self.errors.append(error_msg)
                    all_ok = False
                else:
                    print_status(f"{setting_name}: {value}", "ok")
            else:
                if not value:
                    print_status(f"{setting_name}: NOT SET", "fail")
                    self.errors.append(error_msg)
                    all_ok = False
                else:
                    masked_value = value[:10] + "..." if len(value) > 10 else value
                    print_status(f"{setting_name}: {masked_value}", "ok")

        optional_settings = [
            ("hmlr_vector_search_enabled", True),
            ("hmlr_search_index_name", "hmlr-memories"),
            ("hmlr_embedding_cache_size", 1000),
            ("hmlr_embedding_cache_ttl_minutes", 5),
            ("hmlr_topic_similarity_threshold", 0.7),
        ]

        print_status("Optional settings:", "info")
        for setting_name, default in optional_settings:
            value = getattr(settings, setting_name, default)
            self.log(f"  {setting_name}: {value}")

        return all_ok

    def validate_azure_search(self) -> bool:
        print_header("2. Azure AI Search Connectivity")

        try:
            from azure.search.documents.indexes import SearchIndexClient
            from azure.core.credentials import AzureKeyCredential

            client = SearchIndexClient(
                endpoint=settings.azure_search_endpoint,
                credential=AzureKeyCredential(settings.azure_search_api_key)
            )

            indexes = list(client.list_index_names())
            print_status(f"Connected to Azure Search ({len(indexes)} indexes found)", "ok")
            self.log(f"Existing indexes: {', '.join(indexes) if indexes else 'None'}")

            hmlr_index = settings.hmlr_search_index_name
            if hmlr_index in indexes:
                print_status(f"HMLR index '{hmlr_index}' exists", "ok")
            else:
                if self.check_only:
                    print_status(f"HMLR index '{hmlr_index}' does not exist (will create)", "warn")
                    self.warnings.append(f"Index '{hmlr_index}' needs to be created")
                else:
                    print_status(f"HMLR index '{hmlr_index}' will be created", "info")

            return True

        except Exception as e:
            print_status(f"Azure Search connection failed: {str(e)}", "fail")
            self.errors.append(f"Azure Search: {str(e)}")
            return False

    def validate_azure_openai(self) -> bool:
        print_header("3. Azure OpenAI Connectivity")

        try:
            from openai import AzureOpenAI

            client = AzureOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version
            )

            response = client.embeddings.create(
                model=settings.azure_openai_embeddings_deployment,
                input="HMLR initialization test"
            )

            embedding = response.data[0].embedding
            print_status(f"Embedding generation successful ({len(embedding)} dimensions)", "ok")
            self.log(f"Sample values: [{embedding[0]:.4f}, {embedding[1]:.4f}, ...]")

            if len(embedding) != 1536:
                print_status(f"Warning: Expected 1536 dimensions, got {len(embedding)}", "warn")
                self.warnings.append(f"Embedding dimensions: {len(embedding)} (expected 1536)")

            return True

        except Exception as e:
            print_status(f"Azure OpenAI connection failed: {str(e)}", "fail")
            self.errors.append(f"Azure OpenAI: {str(e)}")
            return False

    def create_or_update_index(self) -> bool:
        print_header("4. Index Setup")

        if self.check_only:
            print_status("Skipping index setup (--check-only mode)", "info")
            return True

        try:
            from src.hmlr.lattice_crawler import LatticeCrawler

            crawler = LatticeCrawler(
                index_name=settings.hmlr_search_index_name,
                endpoint=settings.azure_search_endpoint,
                api_key=settings.azure_search_api_key
            )

            crawler.ensure_index_exists()
            print_status(f"Index '{settings.hmlr_search_index_name}' ready", "ok")

            stats = crawler.get_index_statistics()
            self.log(f"Document count: {stats.get('document_count', 'N/A')}")
            self.log(f"Storage size: {stats.get('storage_size', 'N/A')} bytes")

            return True

        except Exception as e:
            print_status(f"Index setup failed: {str(e)}", "fail")
            self.errors.append(f"Index setup: {str(e)}")
            return False

    def run_health_check(self) -> bool:
        print_header("5. System Health Check")

        try:
            from src.hmlr.cache import TTLLRUCache

            cache = TTLLRUCache(
                maxsize=settings.hmlr_embedding_cache_size,
                ttl_minutes=settings.hmlr_embedding_cache_ttl_minutes
            )
            cache.set("health_check", [0.1] * 1536)
            result = cache.get("health_check")

            if result:
                print_status("Cache health check passed", "ok")
            else:
                print_status("Cache health check failed", "fail")
                return False

        except Exception as e:
            print_status(f"Cache check failed: {str(e)}", "fail")
            self.errors.append(f"Cache: {str(e)}")
            return False

        if settings.hmlr_sql_connection_string:
            try:
                import pyodbc
                conn = pyodbc.connect(settings.hmlr_sql_connection_string, timeout=5)
                conn.close()
                print_status("SQL connectivity check passed", "ok")
            except Exception as e:
                print_status(f"SQL connectivity failed: {str(e)}", "warn")
                self.warnings.append(f"SQL connection: {str(e)}")
        else:
            print_status("SQL connection string not configured (optional)", "info")

        return True

    def print_summary(self):
        print_header("Summary")

        if self.errors:
            print(f"\n{Colors.RED}ERRORS ({len(self.errors)}):{Colors.RESET}")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}WARNINGS ({len(self.warnings)}):{Colors.RESET}")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors:
            print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] All validation checks passed!{Colors.RESET}")
            if self.check_only:
                print("  Run without --check-only to create/update resources.")
            else:
                print("  HMLR system is ready for production use.")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}[FAILED] Validation failed. Fix errors before deployment.{Colors.RESET}")
            return False

    def run(self) -> bool:
        print(f"\n{Colors.BOLD}HMLR Production Initialization{Colors.RESET}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Mode: {'Validation only' if self.check_only else 'Full initialization'}")

        steps = [
            self.validate_config,
            self.validate_azure_search,
            self.validate_azure_openai,
            self.create_or_update_index,
            self.run_health_check,
        ]

        for step in steps:
            try:
                step()
            except Exception as e:
                print_status(f"Unexpected error: {str(e)}", "fail")
                self.errors.append(str(e))

        return self.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description="HMLR Production Initialization Script"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run validation only, don't create/update resources"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    validator = HMLRProductionValidator(
        verbose=args.verbose,
        check_only=args.check_only
    )

    success = validator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

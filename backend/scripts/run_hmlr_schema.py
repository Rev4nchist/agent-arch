"""Run HMLR Azure SQL schema setup."""

import pyodbc
import os
from pathlib import Path

# Connection string from environment or hardcoded for setup
CONNECTION_STRING = os.getenv(
    "HMLR_SQL_CONNECTION_STRING",
    "Driver={SQL Server};Server=tcp:agent-arch-sql.database.windows.net,1433;Database=hmlr-db;Uid=sqladmin;Pwd=***REMOVED***;Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
)

# SQL statements (separated by GO in original script)
SCHEMA_STATEMENTS = [
    # Create fact_store table (note: [key] escaped - reserved word)
    """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fact_store')
    BEGIN
        CREATE TABLE fact_store (
            fact_id INT IDENTITY(1,1) PRIMARY KEY,
            user_id NVARCHAR(255) NOT NULL,
            [key] NVARCHAR(255) NOT NULL,
            value NVARCHAR(MAX) NOT NULL,
            category NVARCHAR(50) NOT NULL,
            source_block_id NVARCHAR(255),
            source_chunk_id NVARCHAR(255),
            evidence_snippet NVARCHAR(MAX),
            confidence FLOAT DEFAULT 1.0,
            verified BIT DEFAULT 0,
            created_at DATETIME2 DEFAULT GETUTCDATE(),
            updated_at DATETIME2 DEFAULT GETUTCDATE()
        );
        CREATE INDEX IX_fact_key ON fact_store([key]);
        CREATE INDEX IX_fact_user ON fact_store(user_id);
        CREATE INDEX IX_fact_category ON fact_store(category);
        CREATE INDEX IX_fact_block ON fact_store(source_block_id);
    END
    """,

    # Create user_profiles table
    """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_profiles')
    BEGIN
        CREATE TABLE user_profiles (
            profile_id INT IDENTITY(1,1) PRIMARY KEY,
            user_id NVARCHAR(255) UNIQUE NOT NULL,
            preferences NVARCHAR(MAX),
            common_queries NVARCHAR(MAX),
            known_entities NVARCHAR(MAX),
            interaction_patterns NVARCHAR(MAX),
            created_at DATETIME2 DEFAULT GETUTCDATE(),
            last_updated DATETIME2 DEFAULT GETUTCDATE()
        );
        CREATE INDEX IX_profile_user ON user_profiles(user_id);
    END
    """,

    # Create fact_history table
    """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fact_history')
    BEGIN
        CREATE TABLE fact_history (
            history_id INT IDENTITY(1,1) PRIMARY KEY,
            fact_id INT NOT NULL,
            user_id NVARCHAR(255) NOT NULL,
            old_value NVARCHAR(MAX),
            new_value NVARCHAR(MAX),
            change_reason NVARCHAR(255),
            changed_at DATETIME2 DEFAULT GETUTCDATE(),
            FOREIGN KEY (fact_id) REFERENCES fact_store(fact_id) ON DELETE CASCADE
        );
        CREATE INDEX IX_history_fact ON fact_history(fact_id);
    END
    """,

    # Drop and recreate upsert_fact procedure
    "IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'upsert_fact') DROP PROCEDURE upsert_fact",

    """
    CREATE PROCEDURE upsert_fact
        @user_id NVARCHAR(255),
        @fact_key NVARCHAR(255),
        @value NVARCHAR(MAX),
        @category NVARCHAR(50),
        @source_block_id NVARCHAR(255) = NULL,
        @source_chunk_id NVARCHAR(255) = NULL,
        @evidence_snippet NVARCHAR(MAX) = NULL,
        @confidence FLOAT = 1.0
    AS
    BEGIN
        SET NOCOUNT ON;
        IF EXISTS (SELECT 1 FROM fact_store WHERE user_id = @user_id AND [key] = @fact_key)
        BEGIN
            INSERT INTO fact_history (fact_id, user_id, old_value, new_value, change_reason)
            SELECT fact_id, user_id, value, @value, 'Updated by extraction'
            FROM fact_store WHERE user_id = @user_id AND [key] = @fact_key;

            UPDATE fact_store
            SET value = @value, category = @category,
                source_block_id = COALESCE(@source_block_id, source_block_id),
                source_chunk_id = COALESCE(@source_chunk_id, source_chunk_id),
                evidence_snippet = COALESCE(@evidence_snippet, evidence_snippet),
                confidence = @confidence, updated_at = GETUTCDATE()
            WHERE user_id = @user_id AND [key] = @fact_key;
        END
        ELSE
        BEGIN
            INSERT INTO fact_store (user_id, [key], value, category, source_block_id, source_chunk_id, evidence_snippet, confidence)
            VALUES (@user_id, @fact_key, @value, @category, @source_block_id, @source_chunk_id, @evidence_snippet, @confidence);
        END
    END
    """,

    # Drop and recreate get_facts_by_keywords procedure
    "IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'get_facts_by_keywords') DROP PROCEDURE get_facts_by_keywords",

    """
    CREATE PROCEDURE get_facts_by_keywords
        @user_id NVARCHAR(255),
        @keywords NVARCHAR(MAX)
    AS
    BEGIN
        SET NOCOUNT ON;
        SELECT fact_id, user_id, [key], value, category, evidence_snippet, confidence, created_at
        FROM fact_store
        WHERE user_id = @user_id
          AND ([key] IN (SELECT value FROM STRING_SPLIT(@keywords, ','))
               OR value LIKE '%' + @keywords + '%')
        ORDER BY confidence DESC, created_at DESC;
    END
    """,

    # Drop and recreate upsert_user_profile procedure
    "IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'upsert_user_profile') DROP PROCEDURE upsert_user_profile",

    """
    CREATE PROCEDURE upsert_user_profile
        @user_id NVARCHAR(255),
        @preferences NVARCHAR(MAX) = NULL,
        @common_queries NVARCHAR(MAX) = NULL,
        @known_entities NVARCHAR(MAX) = NULL,
        @interaction_patterns NVARCHAR(MAX) = NULL
    AS
    BEGIN
        SET NOCOUNT ON;
        IF EXISTS (SELECT 1 FROM user_profiles WHERE user_id = @user_id)
        BEGIN
            UPDATE user_profiles
            SET preferences = COALESCE(@preferences, preferences),
                common_queries = COALESCE(@common_queries, common_queries),
                known_entities = COALESCE(@known_entities, known_entities),
                interaction_patterns = COALESCE(@interaction_patterns, interaction_patterns),
                last_updated = GETUTCDATE()
            WHERE user_id = @user_id;
        END
        ELSE
        BEGIN
            INSERT INTO user_profiles (user_id, preferences, common_queries, known_entities, interaction_patterns)
            VALUES (@user_id, @preferences, @common_queries, @known_entities, @interaction_patterns);
        END
    END
    """
]


def main():
    print("=" * 50)
    print("HMLR Azure SQL Schema Setup")
    print("=" * 50)

    print(f"\nConnecting to Azure SQL...")

    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        print("Connected successfully!")

        for i, stmt in enumerate(SCHEMA_STATEMENTS, 1):
            stmt = stmt.strip()
            if not stmt:
                continue

            try:
                cursor.execute(stmt)
                conn.commit()

                # Determine what was created
                if "CREATE TABLE" in stmt:
                    table_name = stmt.split("CREATE TABLE")[1].split("(")[0].strip()
                    print(f"  [{i}] Created table: {table_name}")
                elif "CREATE PROCEDURE" in stmt:
                    proc_name = stmt.split("CREATE PROCEDURE")[1].split()[0].strip()
                    print(f"  [{i}] Created procedure: {proc_name}")
                elif "DROP PROCEDURE" in stmt:
                    print(f"  [{i}] Dropped old procedure")
                else:
                    print(f"  [{i}] Executed statement")

            except pyodbc.Error as e:
                if "already exists" in str(e).lower():
                    print(f"  [{i}] Already exists (skipped)")
                else:
                    print(f"  [{i}] Error: {e}")

        # Verify tables exist
        print("\nVerifying tables...")
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Tables: {', '.join(tables)}")

        cursor.execute("SELECT name FROM sys.procedures")
        procs = [row[0] for row in cursor.fetchall()]
        print(f"  Procedures: {', '.join(procs)}")

        cursor.close()
        conn.close()

        print("\n" + "=" * 50)
        print("Schema setup complete!")
        print("=" * 50)

    except pyodbc.Error as e:
        print(f"\nConnection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if ODBC Driver 18 is installed")
        print("2. Verify firewall rules in Azure Portal")
        print("3. Check connection string in .env")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

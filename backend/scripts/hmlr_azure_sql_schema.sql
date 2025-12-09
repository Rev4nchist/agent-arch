-- HMLR Memory System - Azure SQL Database Schema
-- Run this script to create the required tables for fact storage and user profiles

-- ============================================================================
-- FACT STORE TABLE
-- Stores extracted hard facts (definitions, acronyms, entities, secrets)
-- Persists per-user across all sessions
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fact_store')
BEGIN
    CREATE TABLE fact_store (
        fact_id INT IDENTITY(1,1) PRIMARY KEY,
        user_id NVARCHAR(255) NOT NULL,
        key NVARCHAR(255) NOT NULL,
        value NVARCHAR(MAX) NOT NULL,
        category NVARCHAR(50) NOT NULL,  -- Definition | Acronym | Secret | Entity
        source_block_id NVARCHAR(255),    -- Bridge Block where fact was extracted
        source_chunk_id NVARCHAR(255),    -- Sentence-level chunk ID for provenance
        evidence_snippet NVARCHAR(MAX),   -- 10-20 word context around fact
        confidence FLOAT DEFAULT 1.0,     -- Extraction confidence (0.0 - 1.0)
        verified BIT DEFAULT 0,           -- User verified fact
        created_at DATETIME2 DEFAULT GETUTCDATE(),
        updated_at DATETIME2 DEFAULT GETUTCDATE()
    );

    -- Indexes for fast lookup
    CREATE INDEX IX_fact_key ON fact_store(key);
    CREATE INDEX IX_fact_user ON fact_store(user_id);
    CREATE INDEX IX_fact_category ON fact_store(category);
    CREATE INDEX IX_fact_block ON fact_store(source_block_id);

    PRINT 'Created table: fact_store';
END
GO

-- ============================================================================
-- USER PROFILES TABLE
-- Stores persistent user preferences and interaction patterns
-- Built up over time by the Scribe agent
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_profiles')
BEGIN
    CREATE TABLE user_profiles (
        profile_id INT IDENTITY(1,1) PRIMARY KEY,
        user_id NVARCHAR(255) UNIQUE NOT NULL,
        preferences NVARCHAR(MAX),          -- JSON: response_style, default values, etc.
        common_queries NVARCHAR(MAX),       -- JSON array: frequently asked queries
        known_entities NVARCHAR(MAX),       -- JSON array: {name, type, relationship}
        interaction_patterns NVARCHAR(MAX), -- JSON: avg_turns, common_intents, etc.
        created_at DATETIME2 DEFAULT GETUTCDATE(),
        last_updated DATETIME2 DEFAULT GETUTCDATE()
    );

    CREATE INDEX IX_profile_user ON user_profiles(user_id);

    PRINT 'Created table: user_profiles';
END
GO

-- ============================================================================
-- FACT HISTORY TABLE (Optional - for tracking fact changes over time)
-- ============================================================================
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

    PRINT 'Created table: fact_history';
END
GO

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- Upsert fact (insert or update if key already exists for user)
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'upsert_fact')
    DROP PROCEDURE upsert_fact;
GO

CREATE PROCEDURE upsert_fact
    @user_id NVARCHAR(255),
    @key NVARCHAR(255),
    @value NVARCHAR(MAX),
    @category NVARCHAR(50),
    @source_block_id NVARCHAR(255) = NULL,
    @source_chunk_id NVARCHAR(255) = NULL,
    @evidence_snippet NVARCHAR(MAX) = NULL,
    @confidence FLOAT = 1.0
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM fact_store WHERE user_id = @user_id AND key = @key)
    BEGIN
        -- Archive old value to history
        INSERT INTO fact_history (fact_id, user_id, old_value, new_value, change_reason)
        SELECT fact_id, user_id, value, @value, 'Updated by extraction'
        FROM fact_store WHERE user_id = @user_id AND key = @key;

        -- Update existing fact
        UPDATE fact_store
        SET value = @value,
            category = @category,
            source_block_id = COALESCE(@source_block_id, source_block_id),
            source_chunk_id = COALESCE(@source_chunk_id, source_chunk_id),
            evidence_snippet = COALESCE(@evidence_snippet, evidence_snippet),
            confidence = @confidence,
            updated_at = GETUTCDATE()
        WHERE user_id = @user_id AND key = @key;
    END
    ELSE
    BEGIN
        -- Insert new fact
        INSERT INTO fact_store (user_id, key, value, category, source_block_id, source_chunk_id, evidence_snippet, confidence)
        VALUES (@user_id, @key, @value, @category, @source_block_id, @source_chunk_id, @evidence_snippet, @confidence);
    END
END
GO

PRINT 'Created stored procedure: upsert_fact';

-- Get facts for user by keywords
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'get_facts_by_keywords')
    DROP PROCEDURE get_facts_by_keywords;
GO

CREATE PROCEDURE get_facts_by_keywords
    @user_id NVARCHAR(255),
    @keywords NVARCHAR(MAX)  -- Comma-separated keywords
AS
BEGIN
    SET NOCOUNT ON;

    SELECT fact_id, user_id, key, value, category, evidence_snippet, confidence, created_at
    FROM fact_store
    WHERE user_id = @user_id
      AND (
          key IN (SELECT value FROM STRING_SPLIT(@keywords, ','))
          OR value LIKE '%' + (SELECT TOP 1 value FROM STRING_SPLIT(@keywords, ',')) + '%'
      )
    ORDER BY confidence DESC, created_at DESC;
END
GO

PRINT 'Created stored procedure: get_facts_by_keywords';

-- Upsert user profile
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'upsert_user_profile')
    DROP PROCEDURE upsert_user_profile;
GO

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
GO

PRINT 'Created stored procedure: upsert_user_profile';

PRINT '';
PRINT '============================================';
PRINT 'HMLR Azure SQL Schema created successfully!';
PRINT '============================================';

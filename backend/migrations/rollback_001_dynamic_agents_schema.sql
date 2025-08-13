-- Rollback Script for Dynamic Agent Registry Schema Migration
-- Version: 001
-- Date: 2024-12-08
-- Description: Rollback script to revert the dynamic agent registry schema

-- ============================================
-- ROLLBACK PROCEDURE
-- ============================================
-- Execute this script to completely remove all tables and functions
-- created by migration 001_dynamic_agents_schema.sql

BEGIN;

-- ============================================
-- DROP VIEWS
-- ============================================
DROP VIEW IF EXISTS v_agent_performance_summary CASCADE;
DROP VIEW IF EXISTS v_agent_lineage CASCADE;
DROP VIEW IF EXISTS v_active_agents CASCADE;

-- ============================================
-- DROP TRIGGERS
-- ============================================
DROP TRIGGER IF EXISTS agent_audit_trigger ON agent_registry;
DROP TRIGGER IF EXISTS update_agent_registry_updated_at ON agent_registry;

-- ============================================
-- DROP FUNCTIONS
-- ============================================
DROP FUNCTION IF EXISTS calculate_agent_fitness(VARCHAR(100));
DROP FUNCTION IF EXISTS create_agent_audit_log();
DROP FUNCTION IF EXISTS update_updated_at_column();

-- ============================================
-- DROP TABLES IN REVERSE ORDER (Handle Dependencies)
-- ============================================

-- Drop audit and governance tables
DROP TABLE IF EXISTS agent_audit_log CASCADE;

-- Drop dependency tables
DROP TABLE IF EXISTS agent_dependencies CASCADE;
DROP TABLE IF EXISTS agent_capabilities CASCADE;

-- Drop interaction and monitoring tables
DROP TABLE IF EXISTS agent_interactions CASCADE;
DROP TABLE IF EXISTS agent_performance_metrics CASCADE;

-- Drop meta-agent tables
DROP TABLE IF EXISTS meta_agent_tasks CASCADE;

-- Drop evolution tables
DROP TABLE IF EXISTS evolution_history CASCADE;
DROP TABLE IF EXISTS agent_genomes CASCADE;

-- Drop version tracking
DROP TABLE IF EXISTS agent_versions CASCADE;

-- Drop core registry table
DROP TABLE IF EXISTS agent_registry CASCADE;

-- Drop migration tracking
DELETE FROM schema_migrations WHERE version = '001_dynamic_agents_schema';

-- If schema_migrations was created by this migration, drop it
DROP TABLE IF EXISTS schema_migrations CASCADE;

-- ============================================
-- VERIFICATION
-- ============================================
-- Run these queries to verify complete rollback:
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name LIKE 'agent_%' OR table_name LIKE 'meta_%' OR table_name LIKE 'evolution_%';

-- SELECT routine_name FROM information_schema.routines 
-- WHERE routine_schema = 'public' 
-- AND routine_name IN ('calculate_agent_fitness', 'create_agent_audit_log', 'update_updated_at_column');

-- SELECT table_name, view_name FROM information_schema.views 
-- WHERE table_schema = 'public' 
-- AND view_name LIKE 'v_%agent%';

COMMIT;

-- ============================================
-- POST-ROLLBACK NOTES
-- ============================================
-- After running this rollback:
-- 1. All agent registry related tables will be removed
-- 2. All associated functions and triggers will be dropped
-- 3. All views will be removed
-- 4. The database will be restored to pre-migration state
--
-- WARNING: This will permanently delete all data stored in these tables!
-- Make sure to backup any important data before running this rollback.
--
-- To re-apply the migration after rollback:
-- psql -U postgres -d t_developer < migrations/001_dynamic_agents_schema.sql
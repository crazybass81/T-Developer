-- T-Developer Evolution System - Initial Database Schema
-- PostgreSQL 15+ Required

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pgaudit";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS evolution;
CREATE SCHEMA IF NOT EXISTS agents;
CREATE SCHEMA IF NOT EXISTS metrics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set search path
SET search_path TO evolution, agents, metrics, audit, public;

-- =====================================================
-- AGENTS SCHEMA
-- =====================================================

-- Agent Registry Table
CREATE TABLE IF NOT EXISTS agents.agent_registry (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(255) NOT NULL UNIQUE,
    agent_type VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    size_kb DECIMAL(10,2) NOT NULL,
    instantiation_us DECIMAL(10,2) NOT NULL,
    capabilities JSONB DEFAULT '[]'::jsonb,
    constraints_met BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT chk_size_kb CHECK (size_kb >= 0 AND size_kb <= 6.5),
    CONSTRAINT chk_instantiation_us CHECK (instantiation_us >= 0),
    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'deprecated', 'evolving'))
);

CREATE INDEX idx_agent_registry_name ON agents.agent_registry(agent_name);
CREATE INDEX idx_agent_registry_type ON agents.agent_registry(agent_type);
CREATE INDEX idx_agent_registry_status ON agents.agent_registry(status);
CREATE INDEX idx_agent_registry_capabilities ON agents.agent_registry USING GIN (capabilities);

-- Agent Versions Table
CREATE TABLE IF NOT EXISTS agents.agent_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents.agent_registry(agent_id) ON DELETE CASCADE,
    version_number VARCHAR(20) NOT NULL,
    parent_version_id UUID REFERENCES agents.agent_versions(version_id),
    code_hash VARCHAR(64) NOT NULL,
    code_content TEXT,
    size_kb DECIMAL(10,2) NOT NULL,
    instantiation_us DECIMAL(10,2) NOT NULL,
    fitness_score DECIMAL(5,4) DEFAULT 1.0,
    generation INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    is_current BOOLEAN DEFAULT false,
    
    CONSTRAINT uk_agent_version UNIQUE(agent_id, version_number),
    CONSTRAINT chk_fitness_score CHECK (fitness_score >= 0 AND fitness_score <= 1)
);

CREATE INDEX idx_agent_versions_agent_id ON agents.agent_versions(agent_id);
CREATE INDEX idx_agent_versions_parent ON agents.agent_versions(parent_version_id);
CREATE INDEX idx_agent_versions_current ON agents.agent_versions(is_current) WHERE is_current = true;
CREATE INDEX idx_agent_versions_fitness ON agents.agent_versions(fitness_score DESC);

-- =====================================================
-- EVOLUTION SCHEMA
-- =====================================================

-- Evolution History Table
CREATE TABLE IF NOT EXISTS evolution.evolution_history (
    evolution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_agent_id UUID NOT NULL,
    parent_version_id UUID NOT NULL REFERENCES agents.agent_versions(version_id),
    child_agent_id UUID NOT NULL,
    child_version_id UUID NOT NULL REFERENCES agents.agent_versions(version_id),
    evolution_type VARCHAR(50) NOT NULL,
    mutation_params JSONB DEFAULT '{}'::jsonb,
    fitness_before DECIMAL(5,4),
    fitness_after DECIMAL(5,4),
    fitness_delta DECIMAL(5,4) GENERATED ALWAYS AS (fitness_after - fitness_before) STORED,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_evolution_type CHECK (evolution_type IN ('mutation', 'crossover', 'optimization', 'refactor', 'merge'))
);

CREATE INDEX idx_evolution_history_parent ON evolution.evolution_history(parent_agent_id, parent_version_id);
CREATE INDEX idx_evolution_history_child ON evolution.evolution_history(child_agent_id, child_version_id);
CREATE INDEX idx_evolution_history_type ON evolution.evolution_history(evolution_type);
CREATE INDEX idx_evolution_history_success ON evolution.evolution_history(success);
CREATE INDEX idx_evolution_history_created ON evolution.evolution_history(created_at DESC);

-- Evolution Rules Table
CREATE TABLE IF NOT EXISTS evolution.evolution_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(255) NOT NULL UNIQUE,
    rule_type VARCHAR(50) NOT NULL,
    condition JSONB NOT NULL,
    action JSONB NOT NULL,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_rule_type CHECK (rule_type IN ('safety', 'optimization', 'constraint', 'trigger'))
);

CREATE INDEX idx_evolution_rules_type ON evolution.evolution_rules(rule_type);
CREATE INDEX idx_evolution_rules_active ON evolution.evolution_rules(is_active);
CREATE INDEX idx_evolution_rules_priority ON evolution.evolution_rules(priority DESC);

-- Evolution Queue Table
CREATE TABLE IF NOT EXISTS evolution.evolution_queue (
    queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents.agent_registry(agent_id),
    version_id UUID NOT NULL REFERENCES agents.agent_versions(version_id),
    evolution_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_queue_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX idx_evolution_queue_status ON evolution.evolution_queue(status);
CREATE INDEX idx_evolution_queue_priority ON evolution.evolution_queue(priority DESC, created_at ASC);
CREATE INDEX idx_evolution_queue_agent ON evolution.evolution_queue(agent_id);

-- =====================================================
-- METRICS SCHEMA
-- =====================================================

-- Performance Metrics Table
CREATE TABLE IF NOT EXISTS metrics.performance_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents.agent_registry(agent_id),
    version_id UUID REFERENCES agents.agent_versions(version_id),
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20,6) NOT NULL,
    unit VARCHAR(20),
    constraint_name VARCHAR(100),
    constraint_met BOOLEAN,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT chk_metric_type CHECK (metric_type IN ('speed', 'memory', 'cpu', 'latency', 'throughput', 'error_rate', 'fitness'))
);

CREATE INDEX idx_performance_metrics_agent ON metrics.performance_metrics(agent_id, version_id);
CREATE INDEX idx_performance_metrics_type ON metrics.performance_metrics(metric_type);
CREATE INDEX idx_performance_metrics_timestamp ON metrics.performance_metrics(timestamp DESC);
CREATE INDEX idx_performance_metrics_constraint ON metrics.performance_metrics(constraint_met) WHERE constraint_met = false;

-- Partitioning for performance metrics (monthly)
CREATE TABLE metrics.performance_metrics_y2024m11 PARTITION OF metrics.performance_metrics
    FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
CREATE TABLE metrics.performance_metrics_y2024m12 PARTITION OF metrics.performance_metrics
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- Aggregated Metrics Table
CREATE TABLE IF NOT EXISTS metrics.aggregated_metrics (
    agg_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents.agent_registry(agent_id),
    metric_type VARCHAR(50) NOT NULL,
    period VARCHAR(20) NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    avg_value DECIMAL(20,6),
    min_value DECIMAL(20,6),
    max_value DECIMAL(20,6),
    p50_value DECIMAL(20,6),
    p95_value DECIMAL(20,6),
    p99_value DECIMAL(20,6),
    sample_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_period CHECK (period IN ('minute', 'hour', 'day', 'week', 'month')),
    CONSTRAINT uk_aggregated_metrics UNIQUE(agent_id, metric_type, period, period_start)
);

CREATE INDEX idx_aggregated_metrics_agent ON metrics.aggregated_metrics(agent_id);
CREATE INDEX idx_aggregated_metrics_period ON metrics.aggregated_metrics(period_start, period_end);

-- =====================================================
-- AUDIT SCHEMA
-- =====================================================

-- Audit Log Table
CREATE TABLE IF NOT EXISTS audit.audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    user_name VARCHAR(100),
    agent_id UUID,
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_operation CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE', 'TRUNCATE'))
);

CREATE INDEX idx_audit_log_table ON audit.audit_log(table_name);
CREATE INDEX idx_audit_log_operation ON audit.audit_log(operation);
CREATE INDEX idx_audit_log_timestamp ON audit.audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_agent ON audit.audit_log(agent_id);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_agent_registry_updated_at BEFORE UPDATE ON agents.agent_registry
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_evolution_rules_updated_at BEFORE UPDATE ON evolution.evolution_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to maintain current version flag
CREATE OR REPLACE FUNCTION maintain_current_version()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_current = true THEN
        UPDATE agents.agent_versions 
        SET is_current = false 
        WHERE agent_id = NEW.agent_id 
        AND version_id != NEW.version_id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER maintain_current_version_trigger 
    AFTER INSERT OR UPDATE OF is_current ON agents.agent_versions
    FOR EACH ROW EXECUTE FUNCTION maintain_current_version();

-- Function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.audit_log (
        table_name,
        operation,
        user_name,
        agent_id,
        record_id,
        old_values,
        new_values
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        current_user,
        COALESCE(NEW.agent_id, OLD.agent_id),
        COALESCE(NEW.agent_id, OLD.agent_id),
        to_jsonb(OLD),
        to_jsonb(NEW)
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply audit triggers to critical tables
CREATE TRIGGER audit_agent_registry 
    AFTER INSERT OR UPDATE OR DELETE ON agents.agent_registry
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_evolution_history 
    AFTER INSERT OR UPDATE OR DELETE ON evolution.evolution_history
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- =====================================================
-- VIEWS
-- =====================================================

-- Current agents view
CREATE OR REPLACE VIEW agents.v_current_agents AS
SELECT 
    ar.*,
    av.version_number,
    av.fitness_score,
    av.generation,
    av.created_at as version_created_at
FROM agents.agent_registry ar
JOIN agents.agent_versions av ON ar.agent_id = av.agent_id
WHERE av.is_current = true;

-- Evolution lineage view
CREATE OR REPLACE VIEW evolution.v_evolution_lineage AS
WITH RECURSIVE lineage AS (
    SELECT 
        av.version_id,
        av.agent_id,
        av.parent_version_id,
        av.generation,
        av.fitness_score,
        1 as depth
    FROM agents.agent_versions av
    WHERE av.parent_version_id IS NULL
    
    UNION ALL
    
    SELECT 
        av.version_id,
        av.agent_id,
        av.parent_version_id,
        av.generation,
        av.fitness_score,
        l.depth + 1
    FROM agents.agent_versions av
    JOIN lineage l ON av.parent_version_id = l.version_id
)
SELECT * FROM lineage;

-- Performance summary view
CREATE OR REPLACE VIEW metrics.v_performance_summary AS
SELECT 
    ar.agent_name,
    av.version_number,
    av.size_kb,
    av.instantiation_us,
    av.fitness_score,
    COUNT(DISTINCT pm.metric_id) as metric_count,
    AVG(CASE WHEN pm.metric_type = 'speed' THEN pm.metric_value END) as avg_speed,
    AVG(CASE WHEN pm.metric_type = 'memory' THEN pm.metric_value END) as avg_memory,
    SUM(CASE WHEN pm.constraint_met = false THEN 1 ELSE 0 END) as constraint_violations
FROM agents.agent_registry ar
JOIN agents.agent_versions av ON ar.agent_id = av.agent_id
LEFT JOIN metrics.performance_metrics pm ON ar.agent_id = pm.agent_id AND av.version_id = pm.version_id
WHERE av.is_current = true
GROUP BY ar.agent_name, av.version_number, av.size_kb, av.instantiation_us, av.fitness_score;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default evolution rules
INSERT INTO evolution.evolution_rules (rule_name, rule_type, condition, action, priority) VALUES
('Size Constraint', 'constraint', '{"max_size_kb": 6.5}', '{"reject": true, "message": "Agent exceeds size limit"}', 100),
('Speed Constraint', 'constraint', '{"max_instantiation_us": 3}', '{"warning": true, "message": "Agent instantiation slow"}', 90),
('Safety Check', 'safety', '{"dangerous_patterns": ["eval", "exec", "__import__"]}', '{"block": true, "quarantine": true}', 1000),
('Auto-optimize', 'optimization', '{"fitness_below": 0.5}', '{"trigger": "optimization", "priority": "high"}', 50);

-- Grant permissions
GRANT USAGE ON SCHEMA agents, evolution, metrics, audit TO t_developer_app;
GRANT ALL ON ALL TABLES IN SCHEMA agents, evolution, metrics TO t_developer_app;
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO t_developer_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA agents, evolution, metrics, audit TO t_developer_app;

-- Create indexes for foreign keys (performance optimization)
CREATE INDEX idx_fk_agent_versions_agent_id ON agents.agent_versions(agent_id);
CREATE INDEX idx_fk_evolution_history_parent_version ON evolution.evolution_history(parent_version_id);
CREATE INDEX idx_fk_evolution_history_child_version ON evolution.evolution_history(child_version_id);
CREATE INDEX idx_fk_performance_metrics_agent_id ON metrics.performance_metrics(agent_id);
CREATE INDEX idx_fk_performance_metrics_version_id ON metrics.performance_metrics(version_id);

-- Analyze tables for query optimization
ANALYZE agents.agent_registry;
ANALYZE agents.agent_versions;
ANALYZE evolution.evolution_history;
ANALYZE metrics.performance_metrics;

-- Migration complete message
DO $$ 
BEGIN 
    RAISE NOTICE 'T-Developer Evolution System database schema initialized successfully';
    RAISE NOTICE 'Version: 001_initial_schema';
    RAISE NOTICE 'Timestamp: %', CURRENT_TIMESTAMP;
END $$;
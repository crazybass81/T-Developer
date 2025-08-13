-- AI Evolution System Schema
-- Version: 002
-- Date: 2024-12-08
-- Description: Complete schema for AI-driven agent evolution system

-- ============================================
-- CREATE SCHEMAS
-- ============================================
CREATE SCHEMA IF NOT EXISTS agents;
CREATE SCHEMA IF NOT EXISTS evolution;
CREATE SCHEMA IF NOT EXISTS workflows;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- ============================================
-- AGENTS SCHEMA - Core Agent Registry
-- ============================================

-- Main agent registry table with AI analysis
CREATE TABLE IF NOT EXISTS agents.registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    code TEXT NOT NULL,
    code_hash VARCHAR(64) NOT NULL,
    
    -- AI Analysis Results (Real Data)
    ai_capabilities JSONB NOT NULL DEFAULT '{}',
    ai_quality_score NUMERIC(3,2) CHECK (ai_quality_score >= 0 AND ai_quality_score <= 1),
    ai_analysis_timestamp TIMESTAMP NOT NULL,
    ai_model_used VARCHAR(50) NOT NULL,
    ai_confidence_score NUMERIC(3,2) DEFAULT 0.0,
    ai_suggestions JSONB DEFAULT '{}',
    
    -- Performance Metrics (Real Measurements)
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_execution_time_ms NUMERIC(10,2),
    p95_execution_time_ms NUMERIC(10,2),
    p99_execution_time_ms NUMERIC(10,2),
    total_tokens_used BIGINT DEFAULT 0,
    total_cost_usd NUMERIC(10,4) DEFAULT 0,
    
    -- Resource Usage
    avg_memory_mb NUMERIC(10,2),
    avg_cpu_percent NUMERIC(5,2),
    max_memory_mb NUMERIC(10,2),
    max_cpu_percent NUMERIC(5,2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    last_executed_at TIMESTAMP,
    deprecated_at TIMESTAMP,
    deprecation_reason TEXT,
    
    -- Indexes
    INDEX idx_agent_id (agent_id),
    INDEX idx_quality_score (ai_quality_score DESC),
    INDEX idx_execution_count (execution_count DESC),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_last_executed (last_executed_at DESC)
);

-- Agent execution history
CREATE TABLE IF NOT EXISTS agents.execution_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) NOT NULL,
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Execution Details
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL, -- 'running', 'success', 'failed', 'timeout', 'cancelled'
    
    -- Input/Output
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    error_stack TEXT,
    
    -- Metrics
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    cost_usd NUMERIC(10,6),
    memory_used_mb NUMERIC(10,2),
    cpu_used_percent NUMERIC(5,2),
    
    -- Context
    workflow_id VARCHAR(100),
    user_id VARCHAR(100),
    environment VARCHAR(20),
    
    -- Indexes
    INDEX idx_exec_agent_id (agent_id),
    INDEX idx_exec_status (status),
    INDEX idx_exec_started (started_at DESC),
    FOREIGN KEY (agent_id) REFERENCES agents.registry(agent_id) ON DELETE CASCADE
);

-- ============================================
-- EVOLUTION SCHEMA - Genetic Evolution System
-- ============================================

-- Evolution populations
CREATE TABLE IF NOT EXISTS evolution.populations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    population_id VARCHAR(100) UNIQUE NOT NULL,
    generation INTEGER NOT NULL,
    
    -- Population Metrics
    size INTEGER NOT NULL,
    avg_fitness NUMERIC(5,4),
    max_fitness NUMERIC(5,4),
    min_fitness NUMERIC(5,4),
    diversity_score NUMERIC(5,4),
    
    -- Evolution Parameters
    mutation_rate NUMERIC(3,2),
    crossover_rate NUMERIC(3,2),
    elite_size INTEGER,
    selection_method VARCHAR(50),
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evolution_started_at TIMESTAMP,
    evolution_completed_at TIMESTAMP,
    
    -- Results
    best_individual_id VARCHAR(100),
    improvement_rate NUMERIC(5,4),
    convergence_score NUMERIC(5,4),
    
    INDEX idx_generation (generation DESC),
    INDEX idx_max_fitness (max_fitness DESC)
);

-- Individual agents in evolution
CREATE TABLE IF NOT EXISTS evolution.individuals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    individual_id VARCHAR(100) UNIQUE NOT NULL,
    population_id VARCHAR(100) NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    
    -- Genetic Information
    genome JSONB NOT NULL,
    phenotype JSONB,
    
    -- Fitness Scores
    fitness_score NUMERIC(5,4) NOT NULL,
    performance_score NUMERIC(5,4),
    quality_score NUMERIC(5,4),
    efficiency_score NUMERIC(5,4),
    innovation_score NUMERIC(5,4),
    
    -- Lineage
    parent1_id VARCHAR(100),
    parent2_id VARCHAR(100),
    mutation_count INTEGER DEFAULT 0,
    crossover_points JSONB,
    
    -- Status
    is_elite BOOLEAN DEFAULT FALSE,
    is_selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_fitness (fitness_score DESC),
    INDEX idx_population (population_id),
    FOREIGN KEY (population_id) REFERENCES evolution.populations(population_id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents.registry(agent_id) ON DELETE CASCADE
);

-- Evolution experiments tracking
CREATE TABLE IF NOT EXISTS evolution.experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Configuration
    config JSONB NOT NULL,
    target_fitness NUMERIC(5,4),
    max_generations INTEGER,
    early_stopping_patience INTEGER,
    
    -- Status
    status VARCHAR(20) NOT NULL, -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    current_generation INTEGER DEFAULT 0,
    best_fitness_achieved NUMERIC(5,4),
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_checkpoint_at TIMESTAMP,
    
    -- Results
    final_population_id VARCHAR(100),
    winner_agent_id VARCHAR(100),
    total_individuals_evaluated INTEGER,
    total_compute_hours NUMERIC(10,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    
    INDEX idx_exp_status (status),
    INDEX idx_exp_created (created_at DESC)
);

-- ============================================
-- WORKFLOWS SCHEMA - Workflow Management
-- ============================================

-- Workflow definitions
CREATE TABLE IF NOT EXISTS workflows.definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    
    -- Definition
    dag_definition JSONB NOT NULL,
    nodes_count INTEGER NOT NULL,
    edges_count INTEGER NOT NULL,
    max_depth INTEGER,
    
    -- Validation
    is_valid BOOLEAN DEFAULT FALSE,
    validation_errors JSONB,
    validated_at TIMESTAMP,
    
    -- AI Optimization
    ai_optimized BOOLEAN DEFAULT FALSE,
    optimization_suggestions JSONB,
    estimated_execution_time_ms INTEGER,
    estimated_cost_usd NUMERIC(10,4),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    
    INDEX idx_workflow_name (name),
    INDEX idx_workflow_created (created_at DESC)
);

-- Workflow executions
CREATE TABLE IF NOT EXISTS workflows.executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    workflow_id VARCHAR(100) NOT NULL,
    
    -- Execution State
    status VARCHAR(20) NOT NULL, -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    current_node VARCHAR(100),
    completed_nodes JSONB DEFAULT '[]',
    failed_nodes JSONB DEFAULT '[]',
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_execution_time_ms INTEGER,
    
    -- Resources
    total_tokens_used INTEGER,
    total_cost_usd NUMERIC(10,4),
    peak_memory_mb NUMERIC(10,2),
    
    -- Context
    input_data JSONB,
    output_data JSONB,
    execution_context JSONB,
    error_details JSONB,
    
    -- User Info
    initiated_by VARCHAR(100),
    environment VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_exec_workflow (workflow_id),
    INDEX idx_exec_status (status),
    INDEX idx_exec_started (started_at DESC),
    FOREIGN KEY (workflow_id) REFERENCES workflows.definitions(workflow_id) ON DELETE CASCADE
);

-- ============================================
-- MONITORING SCHEMA - Metrics and Monitoring
-- ============================================

-- Real-time metrics
CREATE TABLE IF NOT EXISTS monitoring.metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_unit VARCHAR(20),
    
    -- Dimensions
    dimensions JSONB NOT NULL,
    
    -- Source
    source_type VARCHAR(50) NOT NULL, -- 'agent', 'workflow', 'system', 'evolution'
    source_id VARCHAR(100),
    
    -- Timing
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    aggregation_period INTEGER, -- seconds
    
    -- Indexing for time-series queries
    INDEX idx_metric_name_time (metric_name, timestamp DESC),
    INDEX idx_source_time (source_type, source_id, timestamp DESC),
    INDEX idx_timestamp (timestamp DESC)
);

-- System health checks
CREATE TABLE IF NOT EXISTS monitoring.health_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'healthy', 'degraded', 'unhealthy'
    
    -- Check Details
    check_type VARCHAR(50),
    response_time_ms INTEGER,
    error_message TEXT,
    
    -- Thresholds
    warning_threshold NUMERIC,
    critical_threshold NUMERIC,
    current_value NUMERIC,
    
    -- Metadata
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_check_at TIMESTAMP,
    consecutive_failures INTEGER DEFAULT 0,
    
    INDEX idx_component_status (component, status),
    INDEX idx_checked_at (checked_at DESC)
);

-- Audit logs
CREATE TABLE IF NOT EXISTS monitoring.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    event_action VARCHAR(50) NOT NULL,
    
    -- Actor
    actor_type VARCHAR(50) NOT NULL, -- 'user', 'system', 'ai'
    actor_id VARCHAR(100),
    
    -- Target
    target_type VARCHAR(50),
    target_id VARCHAR(100),
    
    -- Details
    event_data JSONB,
    ip_address INET,
    user_agent TEXT,
    
    -- Result
    success BOOLEAN NOT NULL,
    error_message TEXT,
    
    -- Timing
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_event_type (event_type),
    INDEX idx_actor (actor_type, actor_id),
    INDEX idx_timestamp (timestamp DESC)
);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_agents_registry_updated_at
    BEFORE UPDATE ON agents.registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_definitions_updated_at
    BEFORE UPDATE ON workflows.definitions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate agent fitness
CREATE OR REPLACE FUNCTION calculate_agent_fitness(p_agent_id VARCHAR(100))
RETURNS NUMERIC AS $$
DECLARE
    v_fitness NUMERIC(5,4);
    v_quality NUMERIC(5,4);
    v_performance NUMERIC(5,4);
    v_reliability NUMERIC(5,4);
BEGIN
    SELECT 
        ai_quality_score,
        CASE 
            WHEN avg_execution_time_ms IS NULL THEN 0.5
            ELSE 1.0 - (avg_execution_time_ms / 10000.0) -- Normalize to 0-1
        END,
        CASE 
            WHEN execution_count = 0 THEN 0.5
            ELSE success_count::NUMERIC / execution_count::NUMERIC
        END
    INTO v_quality, v_performance, v_reliability
    FROM agents.registry
    WHERE agent_id = p_agent_id;
    
    -- Weighted average
    v_fitness := (v_quality * 0.4) + (v_performance * 0.3) + (v_reliability * 0.3);
    
    RETURN v_fitness;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- INITIAL DATA SEED
-- ============================================

-- Insert system agents
INSERT INTO agents.registry (
    agent_id, name, version, code, code_hash,
    ai_capabilities, ai_quality_score, ai_analysis_timestamp, ai_model_used
) VALUES 
(
    'system_health_monitor',
    'System Health Monitor',
    '1.0.0',
    '# System health monitoring agent',
    'hash_placeholder',
    '{"monitoring": true, "alerting": true}',
    0.95,
    CURRENT_TIMESTAMP,
    'gpt-4-turbo'
),
(
    'evolution_controller',
    'Evolution Controller',
    '1.0.0',
    '# Evolution control agent',
    'hash_placeholder',
    '{"evolution": true, "optimization": true}',
    0.90,
    CURRENT_TIMESTAMP,
    'claude-3-opus'
)
ON CONFLICT (agent_id) DO NOTHING;

-- ============================================
-- GRANTS (Adjust based on your users)
-- ============================================

-- GRANT USAGE ON SCHEMA agents, evolution, workflows, monitoring TO t_developer_app;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA agents, evolution, workflows, monitoring TO t_developer_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA agents, evolution, workflows, monitoring TO t_developer_app;
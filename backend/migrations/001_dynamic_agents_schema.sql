-- Dynamic Agent Registry Schema Migration
-- Version: 001
-- Date: 2024-12-08
-- Description: Initial schema for dynamic agent registry and evolution system

-- ============================================
-- CORE TABLES
-- ============================================

-- Agent Registry: Central repository of all agents
CREATE TABLE IF NOT EXISTS agent_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'core', 'meta', 'generated', 'evolved'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'deprecated', 'testing'
    capabilities JSONB NOT NULL,
    input_schema JSONB NOT NULL,
    output_schema JSONB NOT NULL,
    configuration JSONB,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100), -- Can be user_id or 'ai_system'
    parent_agent_id VARCHAR(100), -- For evolved/derived agents
    generation INTEGER DEFAULT 0, -- Evolution generation number
    fitness_score DECIMAL(5,4) DEFAULT 0.0, -- 0.0000 to 1.0000

    -- Constraints
    CONSTRAINT check_fitness_range CHECK (fitness_score >= 0 AND fitness_score <= 1),
    CONSTRAINT check_valid_status CHECK (status IN ('active', 'inactive', 'deprecated', 'testing')),
    CONSTRAINT check_valid_type CHECK (type IN ('core', 'meta', 'generated', 'evolved'))
);

-- Indexes for agent_registry
CREATE INDEX idx_agent_type ON agent_registry(type);
CREATE INDEX idx_agent_status ON agent_registry(status);
CREATE INDEX idx_agent_fitness ON agent_registry(fitness_score DESC);
CREATE INDEX idx_agent_generation ON agent_registry(generation);
CREATE INDEX idx_agent_parent ON agent_registry(parent_agent_id);

-- Agent Versions: Track all versions of agents
CREATE TABLE IF NOT EXISTS agent_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    code TEXT NOT NULL,
    dependencies JSONB,
    changelog TEXT,
    performance_metrics JSONB,
    deployment_status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'testing', 'production', 'retired'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),

    -- Constraints
    CONSTRAINT unique_agent_version UNIQUE(agent_id, version),
    CONSTRAINT fk_agent_id FOREIGN KEY (agent_id) REFERENCES agent_registry(agent_id) ON DELETE CASCADE
);

-- Indexes for agent_versions
CREATE INDEX idx_version_agent_id ON agent_versions(agent_id);
CREATE INDEX idx_version_status ON agent_versions(deployment_status);
CREATE INDEX idx_version_created ON agent_versions(created_at DESC);

-- ============================================
-- EVOLUTION SYSTEM TABLES
-- ============================================

-- Agent Genomes: Genetic representation of agents
CREATE TABLE IF NOT EXISTS agent_genomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) NOT NULL,
    genome_data JSONB NOT NULL, -- Genetic encoding of agent characteristics
    chromosome_count INTEGER DEFAULT 1,
    mutation_rate DECIMAL(5,4) DEFAULT 0.1,
    crossover_points JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_genome_agent FOREIGN KEY (agent_id) REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    CONSTRAINT check_mutation_rate CHECK (mutation_rate >= 0 AND mutation_rate <= 1)
);

-- Evolution History: Track evolution cycles
CREATE TABLE IF NOT EXISTS evolution_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evolution_id VARCHAR(100) UNIQUE NOT NULL,
    parent_agents JSONB NOT NULL, -- Array of parent agent_ids
    offspring_agents JSONB NOT NULL, -- Array of created agent_ids
    operation_type VARCHAR(50) NOT NULL, -- 'mutation', 'crossover', 'selection'
    fitness_improvement DECIMAL(5,4),
    parameters JSONB, -- Evolution parameters used
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT check_operation_type CHECK (operation_type IN ('mutation', 'crossover', 'selection', 'random'))
);

-- Indexes for evolution tables
CREATE INDEX idx_genome_agent ON agent_genomes(agent_id);
CREATE INDEX idx_evolution_created ON evolution_history(created_at DESC);
CREATE INDEX idx_evolution_type ON evolution_history(operation_type);
CREATE INDEX idx_evolution_success ON evolution_history(success);

-- ============================================
-- META-AGENT SYSTEM TABLES
-- ============================================

-- Meta Agent Tasks: Track meta-agent operations
CREATE TABLE IF NOT EXISTS meta_agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(100) UNIQUE NOT NULL,
    meta_agent_type VARCHAR(50) NOT NULL, -- 'builder', 'improver', 'orchestrator'
    task_type VARCHAR(50) NOT NULL, -- 'create', 'optimize', 'coordinate'
    input_data JSONB NOT NULL,
    output_data JSONB,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    priority INTEGER DEFAULT 5, -- 1-10, higher is more important
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT check_priority CHECK (priority >= 1 AND priority <= 10),
    CONSTRAINT check_meta_type CHECK (meta_agent_type IN ('builder', 'improver', 'orchestrator'))
);

-- Indexes for meta agent tasks
CREATE INDEX idx_meta_task_status ON meta_agent_tasks(status);
CREATE INDEX idx_meta_task_priority ON meta_agent_tasks(priority DESC);
CREATE INDEX idx_meta_task_type ON meta_agent_tasks(meta_agent_type, task_type);

-- ============================================
-- PERFORMANCE & MONITORING TABLES
-- ============================================

-- Agent Performance Metrics: Real-time performance tracking
CREATE TABLE IF NOT EXISTS agent_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'latency', 'throughput', 'accuracy', 'resource_usage'
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(20), -- 'ms', 'req/s', 'percent', 'MB'
    context JSONB, -- Additional context for the metric
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_metrics_agent FOREIGN KEY (agent_id) REFERENCES agent_registry(agent_id) ON DELETE CASCADE
);

-- Indexes for performance metrics
CREATE INDEX idx_metrics_agent ON agent_performance_metrics(agent_id);
CREATE INDEX idx_metrics_type ON agent_performance_metrics(metric_type);
CREATE INDEX idx_metrics_time ON agent_performance_metrics(measured_at DESC);

-- Agent Interactions: Track agent-to-agent communications
CREATE TABLE IF NOT EXISTS agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_agent_id VARCHAR(100) NOT NULL,
    target_agent_id VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL, -- 'request', 'response', 'event', 'error'
    payload_size_bytes INTEGER,
    latency_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_interaction_source FOREIGN KEY (source_agent_id) REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    CONSTRAINT fk_interaction_target FOREIGN KEY (target_agent_id) REFERENCES agent_registry(agent_id) ON DELETE CASCADE
);

-- Indexes for interactions
CREATE INDEX idx_interaction_source ON agent_interactions(source_agent_id);
CREATE INDEX idx_interaction_target ON agent_interactions(target_agent_id);
CREATE INDEX idx_interaction_time ON agent_interactions(created_at DESC);

-- ============================================
-- CAPABILITY MAPPING TABLES
-- ============================================

-- Agent Capabilities: Detailed capability breakdown
CREATE TABLE IF NOT EXISTS agent_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) NOT NULL,
    capability_name VARCHAR(100) NOT NULL,
    capability_category VARCHAR(50), -- 'processing', 'analysis', 'generation', 'integration'
    description TEXT,
    parameters JSONB,
    confidence_score DECIMAL(3,2) DEFAULT 1.0, -- 0.00 to 1.00
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_capability_agent FOREIGN KEY (agent_id) REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    CONSTRAINT unique_agent_capability UNIQUE(agent_id, capability_name),
    CONSTRAINT check_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Indexes for capabilities
CREATE INDEX idx_capability_agent ON agent_capabilities(agent_id);
CREATE INDEX idx_capability_category ON agent_capabilities(capability_category);
CREATE INDEX idx_capability_confidence ON agent_capabilities(confidence_score DESC);

-- Agent Dependencies: Track inter-agent dependencies
CREATE TABLE IF NOT EXISTS agent_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) NOT NULL,
    depends_on_agent_id VARCHAR(100) NOT NULL,
    dependency_type VARCHAR(50) NOT NULL, -- 'required', 'optional', 'fallback'
    dependency_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_dependency_agent FOREIGN KEY (agent_id) REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    CONSTRAINT fk_dependency_target FOREIGN KEY (depends_on_agent_id) REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    CONSTRAINT unique_dependency UNIQUE(agent_id, depends_on_agent_id),
    CONSTRAINT no_self_dependency CHECK (agent_id != depends_on_agent_id)
);

-- Indexes for dependencies
CREATE INDEX idx_dependency_agent ON agent_dependencies(agent_id);
CREATE INDEX idx_dependency_target ON agent_dependencies(depends_on_agent_id);

-- ============================================
-- AUDIT & GOVERNANCE TABLES
-- ============================================

-- Agent Audit Log: Track all changes to agents
CREATE TABLE IF NOT EXISTS agent_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'created', 'updated', 'evolved', 'deprecated', 'deleted'
    changes JSONB,
    performed_by VARCHAR(100), -- user_id or 'ai_system'
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for audit log
CREATE INDEX idx_audit_agent ON agent_audit_log(agent_id);
CREATE INDEX idx_audit_action ON agent_audit_log(action);
CREATE INDEX idx_audit_time ON agent_audit_log(created_at DESC);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for agent_registry updated_at
CREATE TRIGGER update_agent_registry_updated_at
    BEFORE UPDATE ON agent_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to create audit log entry
CREATE OR REPLACE FUNCTION create_agent_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO agent_audit_log (agent_id, action, changes, performed_by)
        VALUES (NEW.agent_id, 'created', to_jsonb(NEW), NEW.created_by);
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO agent_audit_log (agent_id, action, changes, performed_by)
        VALUES (NEW.agent_id, 'updated',
                jsonb_build_object('old', to_jsonb(OLD), 'new', to_jsonb(NEW)),
                NEW.created_by);
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO agent_audit_log (agent_id, action, changes, performed_by)
        VALUES (OLD.agent_id, 'deleted', to_jsonb(OLD), 'system');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for agent audit logging
CREATE TRIGGER agent_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON agent_registry
    FOR EACH ROW
    EXECUTE FUNCTION create_agent_audit_log();

-- Function to calculate agent fitness score
CREATE OR REPLACE FUNCTION calculate_agent_fitness(
    p_agent_id VARCHAR(100)
) RETURNS DECIMAL(5,4) AS $$
DECLARE
    v_fitness DECIMAL(5,4);
    v_performance_score DECIMAL(5,4);
    v_interaction_score DECIMAL(5,4);
    v_capability_score DECIMAL(5,4);
BEGIN
    -- Calculate performance score (based on latency and accuracy)
    SELECT
        CASE
            WHEN AVG(CASE WHEN metric_type = 'latency' THEN metric_value END) IS NULL THEN 0.5
            ELSE 1.0 - (AVG(CASE WHEN metric_type = 'latency' THEN metric_value END) / 1000.0)
        END INTO v_performance_score
    FROM agent_performance_metrics
    WHERE agent_id = p_agent_id
    AND measured_at > CURRENT_TIMESTAMP - INTERVAL '24 hours';

    -- Calculate interaction success rate
    SELECT
        CASE
            WHEN COUNT(*) = 0 THEN 0.5
            ELSE SUM(CASE WHEN success THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)
        END INTO v_interaction_score
    FROM agent_interactions
    WHERE source_agent_id = p_agent_id
    AND created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours';

    -- Calculate capability confidence average
    SELECT
        CASE
            WHEN AVG(confidence_score) IS NULL THEN 0.5
            ELSE AVG(confidence_score)
        END INTO v_capability_score
    FROM agent_capabilities
    WHERE agent_id = p_agent_id;

    -- Weighted average of all scores
    v_fitness := (
        v_performance_score * 0.4 +
        v_interaction_score * 0.3 +
        v_capability_score * 0.3
    );

    RETURN v_fitness;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS FOR EASIER QUERYING
-- ============================================

-- View: Active agents with their latest version
CREATE OR REPLACE VIEW v_active_agents AS
SELECT
    ar.agent_id,
    ar.name,
    ar.version,
    ar.type,
    ar.status,
    ar.fitness_score,
    ar.generation,
    av.code,
    av.deployment_status,
    COUNT(DISTINCT ac.capability_name) as capability_count,
    COUNT(DISTINCT ad.depends_on_agent_id) as dependency_count
FROM agent_registry ar
LEFT JOIN agent_versions av ON ar.agent_id = av.agent_id AND ar.version = av.version
LEFT JOIN agent_capabilities ac ON ar.agent_id = ac.agent_id
LEFT JOIN agent_dependencies ad ON ar.agent_id = ad.agent_id
WHERE ar.status = 'active'
GROUP BY ar.agent_id, ar.name, ar.version, ar.type, ar.status,
         ar.fitness_score, ar.generation, av.code, av.deployment_status;

-- View: Agent evolution lineage
CREATE OR REPLACE VIEW v_agent_lineage AS
WITH RECURSIVE agent_tree AS (
    -- Base case: agents with no parent
    SELECT
        agent_id,
        name,
        parent_agent_id,
        generation,
        fitness_score,
        ARRAY[agent_id] as lineage_path
    FROM agent_registry
    WHERE parent_agent_id IS NULL

    UNION ALL

    -- Recursive case: agents with parents
    SELECT
        ar.agent_id,
        ar.name,
        ar.parent_agent_id,
        ar.generation,
        ar.fitness_score,
        at.lineage_path || ar.agent_id
    FROM agent_registry ar
    INNER JOIN agent_tree at ON ar.parent_agent_id = at.agent_id
)
SELECT * FROM agent_tree;

-- View: Recent agent performance summary
CREATE OR REPLACE VIEW v_agent_performance_summary AS
SELECT
    agent_id,
    AVG(CASE WHEN metric_type = 'latency' THEN metric_value END) as avg_latency_ms,
    AVG(CASE WHEN metric_type = 'throughput' THEN metric_value END) as avg_throughput,
    AVG(CASE WHEN metric_type = 'accuracy' THEN metric_value END) as avg_accuracy,
    AVG(CASE WHEN metric_type = 'resource_usage' THEN metric_value END) as avg_resource_mb,
    COUNT(*) as metric_count,
    MAX(measured_at) as last_measured
FROM agent_performance_metrics
WHERE measured_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY agent_id;

-- ============================================
-- INITIAL DATA INSERTION
-- ============================================

-- Insert core agents into registry
INSERT INTO agent_registry (agent_id, name, version, type, status, capabilities, input_schema, output_schema)
VALUES
    ('nl_input_v1', 'NL Input Agent', '1.0.0', 'core', 'active',
     '{"nlp": true, "entity_extraction": true, "intent_recognition": true}',
     '{"type": "object", "properties": {"text": {"type": "string"}}}',
     '{"type": "object", "properties": {"requirements": {"type": "array"}}}'),

    ('ui_selection_v1', 'UI Selection Agent', '1.0.0', 'core', 'active',
     '{"framework_selection": true, "ui_library_recommendation": true}',
     '{"type": "object", "properties": {"requirements": {"type": "object"}}}',
     '{"type": "object", "properties": {"framework": {"type": "string"}}}'),

    ('parser_v1', 'Parser Agent', '1.0.0', 'core', 'active',
     '{"requirement_parsing": true, "specification_building": true}',
     '{"type": "object", "properties": {"requirements": {"type": "array"}}}',
     '{"type": "object", "properties": {"specifications": {"type": "object"}}}'),

    ('component_decision_v1', 'Component Decision Agent', '1.0.0', 'core', 'active',
     '{"architecture_design": true, "component_selection": true}',
     '{"type": "object", "properties": {"specifications": {"type": "object"}}}',
     '{"type": "object", "properties": {"components": {"type": "array"}}}'),

    ('match_rate_v1', 'Match Rate Agent', '1.0.0', 'core', 'active',
     '{"scoring": true, "ranking": true, "recommendation": true}',
     '{"type": "object", "properties": {"components": {"type": "array"}}}',
     '{"type": "object", "properties": {"scores": {"type": "object"}}}'),

    ('search_v1', 'Search Agent', '1.0.0', 'core', 'active',
     '{"semantic_search": true, "faceted_search": true, "caching": true}',
     '{"type": "object", "properties": {"query": {"type": "string"}}}',
     '{"type": "object", "properties": {"results": {"type": "array"}}}'),

    ('generation_v1', 'Generation Agent', '1.0.0', 'core', 'active',
     '{"code_generation": true, "test_generation": true, "documentation": true}',
     '{"type": "object", "properties": {"components": {"type": "array"}}}',
     '{"type": "object", "properties": {"files": {"type": "object"}}}'),

    ('assembly_v1', 'Assembly Agent', '1.0.0', 'core', 'active',
     '{"file_organization": true, "validation": true, "packaging": true}',
     '{"type": "object", "properties": {"files": {"type": "object"}}}',
     '{"type": "object", "properties": {"package": {"type": "string"}}}'),

    ('download_v1', 'Download Agent', '1.0.0', 'core', 'active',
     '{"secure_download": true, "cdn_integration": true}',
     '{"type": "object", "properties": {"package": {"type": "string"}}}',
     '{"type": "object", "properties": {"download_url": {"type": "string"}}}')
ON CONFLICT (agent_id) DO NOTHING;

-- Insert agent dependencies
INSERT INTO agent_dependencies (agent_id, depends_on_agent_id, dependency_type)
VALUES
    ('ui_selection_v1', 'nl_input_v1', 'required'),
    ('parser_v1', 'nl_input_v1', 'required'),
    ('component_decision_v1', 'parser_v1', 'required'),
    ('match_rate_v1', 'component_decision_v1', 'required'),
    ('search_v1', 'component_decision_v1', 'required'),
    ('generation_v1', 'search_v1', 'required'),
    ('assembly_v1', 'generation_v1', 'required'),
    ('download_v1', 'assembly_v1', 'required')
ON CONFLICT (agent_id, depends_on_agent_id) DO NOTHING;

-- ============================================
-- GRANT PERMISSIONS (adjust based on your user setup)
-- ============================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- ============================================
-- MIGRATION COMPLETION
-- ============================================

-- Record migration completion
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (version) VALUES ('001_dynamic_agents_schema')
ON CONFLICT (version) DO NOTHING;

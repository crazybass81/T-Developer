-- Agent Registry Schema Migration
-- Day 6: Agent Registry Data Model
-- Generated: 2024-11-18

-- Agents table for core agent metadata
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    size_kb DECIMAL(8,3) NOT NULL DEFAULT 0.0,
    instantiation_us DECIMAL(8,3) NOT NULL DEFAULT 0.0,
    capabilities JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    fitness_score DECIMAL(5,4) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT agents_size_limit CHECK (size_kb <= 6.5),
    CONSTRAINT agents_speed_limit CHECK (instantiation_us <= 3.0),
    CONSTRAINT agents_fitness_range CHECK (fitness_score >= 0.0 AND fitness_score <= 1.0),
    CONSTRAINT agents_unique_name_version UNIQUE (name, version)
);

-- Agent versions table for version management
CREATE TABLE IF NOT EXISTS agent_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    version_number VARCHAR(50) NOT NULL,
    code_hash VARCHAR(64) NOT NULL,
    changes TEXT[],
    is_stable BOOLEAN DEFAULT FALSE,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    rollback_from VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT agent_versions_unique UNIQUE (agent_id, version_number)
);

-- Evolution history table for tracking evolution events
CREATE TABLE IF NOT EXISTS evolution_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    generation INTEGER NOT NULL,
    parent_ids UUID[],
    mutations TEXT[],
    fitness_score DECIMAL(5,4) NOT NULL,
    constraints_met BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT evolution_generation_positive CHECK (generation >= 0),
    CONSTRAINT evolution_fitness_range CHECK (fitness_score >= 0.0 AND fitness_score <= 1.0)
);

-- AI analysis results table
CREATE TABLE IF NOT EXISTS ai_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    findings JSONB NOT NULL,
    confidence DECIMAL(3,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT ai_analysis_confidence_range CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

-- Gene pool table for evolution candidates
CREATE TABLE IF NOT EXISTS gene_pool (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    fitness DECIMAL(5,4) NOT NULL,
    genes JSONB DEFAULT '{}'::jsonb,
    age INTEGER DEFAULT 0,
    pool_name VARCHAR(100) DEFAULT 'default',
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT gene_pool_fitness_range CHECK (fitness >= 0.0 AND fitness <= 1.0),
    CONSTRAINT gene_pool_age_positive CHECK (age >= 0),
    CONSTRAINT gene_pool_unique_agent UNIQUE (agent_id, pool_name)
);

-- Fitness tracking table
CREATE TABLE IF NOT EXISTS fitness_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    generation INTEGER NOT NULL,
    fitness_score DECIMAL(5,4) NOT NULL,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fitness_generation_positive CHECK (generation >= 0),
    CONSTRAINT fitness_score_range CHECK (fitness_score >= 0.0 AND fitness_score <= 1.0)
);

-- Evolution patterns table for pattern analysis
CREATE TABLE IF NOT EXISTS evolution_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(100) NOT NULL,
    pattern_data JSONB NOT NULL,
    success_rate DECIMAL(5,4) NOT NULL,
    avg_improvement DECIMAL(5,4) NOT NULL,
    occurrences INTEGER DEFAULT 1,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT evolution_patterns_success_rate CHECK (success_rate >= 0.0 AND success_rate <= 1.0),
    CONSTRAINT evolution_patterns_improvement CHECK (avg_improvement >= -1.0 AND avg_improvement <= 1.0),
    CONSTRAINT evolution_patterns_occurrences CHECK (occurrences > 0),
    CONSTRAINT evolution_patterns_unique_type UNIQUE (pattern_type)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name);
CREATE INDEX IF NOT EXISTS idx_agents_fitness ON agents(fitness_score DESC);
CREATE INDEX IF NOT EXISTS idx_agents_size_speed ON agents(size_kb, instantiation_us);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);

CREATE INDEX IF NOT EXISTS idx_agent_versions_agent_id ON agent_versions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_versions_version ON agent_versions(version_number);
CREATE INDEX IF NOT EXISTS idx_agent_versions_stable ON agent_versions(is_stable);

CREATE INDEX IF NOT EXISTS idx_evolution_history_agent_id ON evolution_history(agent_id);
CREATE INDEX IF NOT EXISTS idx_evolution_history_generation ON evolution_history(generation);
CREATE INDEX IF NOT EXISTS idx_evolution_history_fitness ON evolution_history(fitness_score DESC);
CREATE INDEX IF NOT EXISTS idx_evolution_history_timestamp ON evolution_history(timestamp);

CREATE INDEX IF NOT EXISTS idx_ai_analysis_agent_id ON ai_analysis_results(agent_id);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_type ON ai_analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_model ON ai_analysis_results(ai_model);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_timestamp ON ai_analysis_results(timestamp);

CREATE INDEX IF NOT EXISTS idx_gene_pool_fitness ON gene_pool(fitness DESC);
CREATE INDEX IF NOT EXISTS idx_gene_pool_pool_name ON gene_pool(pool_name);
CREATE INDEX IF NOT EXISTS idx_gene_pool_agent_id ON gene_pool(agent_id);

CREATE INDEX IF NOT EXISTS idx_fitness_tracking_agent_id ON fitness_tracking(agent_id);
CREATE INDEX IF NOT EXISTS idx_fitness_tracking_generation ON fitness_tracking(generation);
CREATE INDEX IF NOT EXISTS idx_fitness_tracking_fitness ON fitness_tracking(fitness_score DESC);

CREATE INDEX IF NOT EXISTS idx_evolution_patterns_type ON evolution_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_evolution_patterns_success_rate ON evolution_patterns(success_rate DESC);

-- Triggers for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW agent_summary AS
SELECT
    a.id,
    a.name,
    a.version,
    a.size_kb,
    a.instantiation_us,
    a.fitness_score,
    a.created_at,
    CASE
        WHEN a.size_kb <= 6.5 AND a.instantiation_us <= 3.0 THEN TRUE
        ELSE FALSE
    END as meets_constraints,
    COUNT(eh.id) as evolution_count,
    AVG(eh.fitness_score) as avg_evolution_fitness
FROM agents a
LEFT JOIN evolution_history eh ON a.id = eh.agent_id
GROUP BY a.id, a.name, a.version, a.size_kb, a.instantiation_us, a.fitness_score, a.created_at;

CREATE OR REPLACE VIEW fitness_trends AS
SELECT
    agent_id,
    generation,
    fitness_score,
    LAG(fitness_score) OVER (PARTITION BY agent_id ORDER BY generation) as previous_fitness,
    fitness_score - LAG(fitness_score) OVER (PARTITION BY agent_id ORDER BY generation) as fitness_change
FROM fitness_tracking
ORDER BY agent_id, generation;

CREATE OR REPLACE VIEW top_performers AS
SELECT
    a.id,
    a.name,
    a.version,
    a.fitness_score,
    a.size_kb,
    a.instantiation_us,
    eh.generation,
    eh.mutations
FROM agents a
JOIN evolution_history eh ON a.id = eh.agent_id
WHERE a.fitness_score >= 0.8 AND eh.constraints_met = TRUE
ORDER BY a.fitness_score DESC, eh.generation DESC;

-- Comments for documentation
COMMENT ON TABLE agents IS 'Core agent metadata and properties';
COMMENT ON TABLE agent_versions IS 'Version control for agent code and metadata';
COMMENT ON TABLE evolution_history IS 'Track evolution events and lineage';
COMMENT ON TABLE ai_analysis_results IS 'Store AI model analysis results';
COMMENT ON TABLE gene_pool IS 'Pool of agents available for evolution';
COMMENT ON TABLE fitness_tracking IS 'Track fitness scores over generations';
COMMENT ON TABLE evolution_patterns IS 'Store successful evolution patterns';

COMMENT ON COLUMN agents.size_kb IS 'Agent size in kilobytes (constraint: <= 6.5KB)';
COMMENT ON COLUMN agents.instantiation_us IS 'Instantiation time in microseconds (constraint: <= 3μs)';
COMMENT ON COLUMN agents.fitness_score IS 'Overall fitness score (0.0 to 1.0)';
COMMENT ON COLUMN agents.capabilities IS 'JSON array of agent capabilities';
COMMENT ON COLUMN agents.metadata IS 'Additional metadata in JSON format';

-- Sample data for testing (optional)
INSERT INTO agents (name, description, version, size_kb, instantiation_us, capabilities, fitness_score) VALUES
    ('nl_input_agent', 'Natural Language Input Processing Agent', '1.0.0', 5.2, 2.1, '["text_processing", "intent_extraction"]', 0.85),
    ('ui_selection_agent', 'UI Component Selection Agent', '1.0.0', 4.8, 1.9, '["component_analysis", "ui_recommendation"]', 0.92),
    ('parser_agent', 'Code Parsing and Analysis Agent', '1.0.0', 6.1, 2.7, '["code_parsing", "syntax_analysis"]', 0.78)
ON CONFLICT (name, version) DO NOTHING;

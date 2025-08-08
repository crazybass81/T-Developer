#!/bin/bash

# Local Testing Script for Lambda Functions
# Test Lambda functions locally using SAM

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
AGENT=${1:-nl-input}
EVENT_FILE=${2:-events/test-event.json}

echo -e "${GREEN}T-Developer Lambda Local Testing${NC}"
echo "================================"
echo "Agent: ${AGENT}"
echo ""

# Create test events directory
mkdir -p events

# Create test event for NL Input Agent
create_nl_input_event() {
    cat > events/nl-input-event.json << EOF
{
    "body": {
        "user_input": "Create an e-commerce website with React, Next.js, and Stripe payment integration",
        "context": {
            "user_id": "test-user-123",
            "session_id": "test-session-456",
            "project_name": "my-ecommerce-site"
        }
    }
}
EOF
}

# Create test event for UI Selection Agent
create_ui_selection_event() {
    cat > events/ui-selection-event.json << EOF
{
    "body": {
        "requirements": {
            "ui_type": "web",
            "features": ["responsive", "modern", "accessible"],
            "performance_requirements": {
                "load_time": "< 3s",
                "bundle_size": "< 500KB"
            }
        }
    }
}
EOF
}

# Create test event for Parser Agent
create_parser_event() {
    cat > events/parser-event.json << EOF
{
    "body": {
        "nl_result": {
            "requirements": "E-commerce website with product catalog",
            "constraints": ["mobile-responsive", "SEO-optimized"]
        },
        "ui_selection": {
            "framework": "React",
            "styling": "Tailwind CSS"
        }
    }
}
EOF
}

# Create test event for Component Decision Agent
create_component_decision_event() {
    cat > events/component-decision-event.json << EOF
{
    "body": {
        "parsed_project": {
            "components": ["auth", "payment", "catalog"],
            "requirements": {
                "scalability": "high",
                "security": "enterprise"
            }
        },
        "ui_selection": {
            "framework": "React"
        }
    }
}
EOF
}

# Create test event for Match Rate Agent
create_match_rate_event() {
    cat > events/match-rate-event.json << EOF
{
    "body": {
        "requirements": {
            "features": ["authentication", "payment", "search"],
            "technologies": ["React", "Node.js"]
        },
        "technology_stack": {
            "frontend": "React",
            "backend": "Node.js",
            "database": "PostgreSQL"
        }
    }
}
EOF
}

# Create test event for Search Agent
create_search_event() {
    cat > events/search-event.json << EOF
{
    "body": {
        "requirements": {
            "components": ["authentication", "payment gateway"],
            "framework": "React"
        },
        "filters": {
            "min_stars": 100,
            "license": "MIT"
        }
    }
}
EOF
}

# Create test event for Generation Agent
create_generation_event() {
    cat > events/generation-event.json << EOF
{
    "body": {
        "parsed_project": {
            "name": "my-app",
            "components": ["HomePage", "ProductList", "ShoppingCart"]
        },
        "technology_stack": {
            "frontend": "React",
            "styling": "Tailwind CSS"
        },
        "search_results": {
            "templates": ["react-boilerplate"],
            "components": ["react-stripe-checkout"]
        }
    }
}
EOF
}

# Create test event for Assembly Agent
create_assembly_event() {
    cat > events/assembly-event.json << EOF
{
    "body": {
        "generation_result": {
            "files": [
                {"path": "src/App.js", "content": "// App code"},
                {"path": "package.json", "content": "{}"}
            ]
        },
        "technology_stack": {
            "build_tool": "webpack",
            "package_manager": "npm"
        }
    }
}
EOF
}

# Create test event for Download Agent
create_download_event() {
    cat > events/download-event.json << EOF
{
    "body": {
        "assembly_result": {
            "project_path": "/tmp/project-123",
            "manifest": {
                "name": "my-project",
                "version": "1.0.0",
                "files": ["src/", "package.json", "README.md"]
            }
        }
    }
}
EOF
}

# Create all test events
create_test_events() {
    echo -e "${YELLOW}Creating test events...${NC}"
    
    create_nl_input_event
    create_ui_selection_event
    create_parser_event
    create_component_decision_event
    create_match_rate_event
    create_search_event
    create_generation_event
    create_assembly_event
    create_download_event
    
    echo -e "${GREEN}Test events created${NC}"
}

# Start local API
start_local_api() {
    echo -e "${YELLOW}Starting local API...${NC}"
    
    sam local start-api \
        --env-vars env.json \
        --docker-network host \
        --warm-containers EAGER \
        --debug
}

# Invoke specific function
invoke_function() {
    local agent=$1
    local event_file=$2
    
    echo -e "${YELLOW}Invoking ${agent} function...${NC}"
    
    function_name=""
    case $agent in
        "nl-input")
            function_name="NLInputAgentFunction"
            event_file="events/nl-input-event.json"
            ;;
        "ui-selection")
            function_name="UISelectionAgentFunction"
            event_file="events/ui-selection-event.json"
            ;;
        "parser")
            function_name="ParserAgentFunction"
            event_file="events/parser-event.json"
            ;;
        "component-decision")
            function_name="ComponentDecisionAgentFunction"
            event_file="events/component-decision-event.json"
            ;;
        "match-rate")
            function_name="MatchRateAgentFunction"
            event_file="events/match-rate-event.json"
            ;;
        "search")
            function_name="SearchAgentFunction"
            event_file="events/search-event.json"
            ;;
        "generation")
            function_name="GenerationAgentFunction"
            event_file="events/generation-event.json"
            ;;
        "assembly")
            function_name="AssemblyAgentFunction"
            event_file="events/assembly-event.json"
            ;;
        "download")
            function_name="DownloadAgentFunction"
            event_file="events/download-event.json"
            ;;
        *)
            echo -e "${RED}Unknown agent: ${agent}${NC}"
            exit 1
            ;;
    esac
    
    # Invoke the function
    sam local invoke \
        "${function_name}" \
        --event "${event_file}" \
        --env-vars env.json \
        --docker-network host
}

# Test all functions
test_all_functions() {
    echo -e "${YELLOW}Testing all functions...${NC}"
    
    agents=("nl-input" "ui-selection" "parser" "component-decision" "match-rate" "search" "generation" "assembly" "download")
    
    for agent in "${agents[@]}"; do
        echo ""
        echo -e "${GREEN}Testing ${agent} agent...${NC}"
        invoke_function "${agent}"
        echo -e "${GREEN}✓ ${agent} test completed${NC}"
        sleep 2
    done
    
    echo ""
    echo -e "${GREEN}All function tests completed!${NC}"
}

# Create environment variables file
create_env_file() {
    cat > env.json << EOF
{
    "NLInputAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "nl_input"
    },
    "UISelectionAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "ui_selection"
    },
    "ParserAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "parser"
    },
    "ComponentDecisionAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "component_decision"
    },
    "MatchRateAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "match_rate"
    },
    "SearchAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "search"
    },
    "GenerationAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "generation"
    },
    "AssemblyAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "assembly"
    },
    "DownloadAgentFunction": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
        "AGENT_NAME": "download",
        "S3_BUCKET": "t-developer-downloads-dev"
    }
}
EOF
}

# Main menu
show_menu() {
    echo ""
    echo "Select an option:"
    echo "1) Create test events"
    echo "2) Start local API"
    echo "3) Test specific function"
    echo "4) Test all functions"
    echo "5) Exit"
    echo ""
    read -p "Enter choice [1-5]: " choice
    
    case $choice in
        1)
            create_test_events
            show_menu
            ;;
        2)
            start_local_api
            ;;
        3)
            echo "Available agents:"
            echo "  - nl-input"
            echo "  - ui-selection"
            echo "  - parser"
            echo "  - component-decision"
            echo "  - match-rate"
            echo "  - search"
            echo "  - generation"
            echo "  - assembly"
            echo "  - download"
            read -p "Enter agent name: " agent_name
            invoke_function "${agent_name}"
            show_menu
            ;;
        4)
            test_all_functions
            show_menu
            ;;
        5)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            show_menu
            ;;
    esac
}

# Initialize
echo -e "${GREEN}Initializing local test environment...${NC}"
create_env_file
create_test_events

# Show menu
show_menu
#!/usr/bin/env python3
"""
Analyze Todo App requirements using existing agents
"""
import asyncio
import json
from src.orchestration.production_pipeline import ProductionECSPipeline

async def analyze_todo_requirements():
    """Use Parser and Component Decision agents to analyze Todo app requirements"""
    
    # Initialize pipeline
    pipeline = ProductionECSPipeline()
    await pipeline.initialize()
    
    # Todo app requirements
    todo_requirements = {
        'name': 'Advanced Todo App',
        'description': '''
        Create a fully functional todo application with the following features:
        - Add new tasks with title, description, priority, and due date
        - Mark tasks as complete/incomplete
        - Edit existing tasks
        - Delete tasks
        - Filter tasks by status (all, active, completed)
        - Sort tasks by priority, due date, or creation date
        - Search tasks by keyword
        - Persist data in local storage
        - Categories/tags for tasks
        - Recurring tasks
        - Task reminders/notifications
        - Dark mode toggle
        - Responsive design for mobile and desktop
        - Keyboard shortcuts for power users
        - Export tasks to CSV/JSON
        - Import tasks from file
        - Statistics dashboard (completion rate, overdue tasks, etc.)
        ''',
        'framework': 'react',
        'features': [
            'Task CRUD operations',
            'Priority management',
            'Due date tracking',
            'Categories and tags',
            'Search and filter',
            'Local storage persistence',
            'Dark mode',
            'Export/Import',
            'Statistics dashboard',
            'Keyboard shortcuts'
        ],
        'requirements': [
            'Must handle large task lists efficiently',
            'Must work offline',
            'Must be accessible (WCAG compliant)',
            'Must have smooth animations',
            'Must support mobile touch gestures'
        ]
    }
    
    print("=" * 60)
    print("🔍 ANALYZING TODO APP REQUIREMENTS")
    print("=" * 60)
    
    # Run through specific agents
    agents_to_run = ['parser', 'component_decision']
    analysis_results = {}
    
    for agent_name in agents_to_run:
        if agent_name in pipeline.agents:
            print(f"\n📝 Running {agent_name} agent...")
            agent = pipeline.agents[agent_name]
            
            # Prepare input based on previous results
            if agent_name == 'parser':
                input_data = todo_requirements
            else:
                # Component decision needs parser output
                input_data = {
                    **todo_requirements,
                    'parsed_requirements': analysis_results.get('parser', {})
                }
            
            # Wrap input for agent
            wrapped_input = {
                'data': input_data,
                'context': {
                    'pipeline_id': 'analysis_pipeline',
                    'project_id': 'todo_app_analysis'
                }
            }
            
            try:
                # Use the fallback wrapper for compatibility
                from src.agents.unified.fallback_wrapper import safe_agent_execute
                result = await safe_agent_execute(agent, wrapped_input)
                analysis_results[agent_name] = result
                
                print(f"✅ {agent_name} completed")
                
                # Print key findings
                if agent_name == 'parser':
                    if 'entities' in result:
                        print(f"  - Found entities: {list(result.get('entities', {}).keys())}")
                    if 'requirements' in result:
                        print(f"  - Parsed {len(result.get('requirements', []))} requirements")
                    if 'specifications' in result:
                        print(f"  - Generated specifications: {list(result.get('specifications', {}).keys())}")
                
                elif agent_name == 'component_decision':
                    if 'components' in result:
                        print(f"  - Identified {len(result.get('components', []))} components")
                        for comp in result.get('components', [])[:5]:
                            if isinstance(comp, dict):
                                print(f"    • {comp.get('name', 'Unknown')}: {comp.get('type', 'N/A')}")
                            else:
                                print(f"    • {comp}")
                    if 'architecture' in result:
                        print(f"  - Architecture: {result.get('architecture', 'N/A')}")
                    if 'technology_stack' in result:
                        print(f"  - Technology stack: {result.get('technology_stack', {})}")
                
            except Exception as e:
                print(f"❌ {agent_name} failed: {str(e)[:100]}")
                analysis_results[agent_name] = {'error': str(e)}
    
    # Save analysis results
    output_file = '/home/ec2-user/T-DeveloperMVP/backend/todo_app_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    
    # Generate Agno agents based on analysis
    print("\n" + "=" * 60)
    print("🤖 RECOMMENDED AGNO AGENTS FOR TODO APP")
    print("=" * 60)
    
    # Extract required functionality
    components = analysis_results.get('component_decision', {}).get('components', [])
    
    recommended_agents = [
        {
            'name': 'TodoCRUDAgent',
            'purpose': 'Handle Create, Read, Update, Delete operations for tasks',
            'methods': ['create_task', 'get_task', 'update_task', 'delete_task', 'list_tasks']
        },
        {
            'name': 'TaskPriorityAgent',
            'purpose': 'Manage task priorities and sorting',
            'methods': ['set_priority', 'sort_by_priority', 'get_high_priority_tasks']
        },
        {
            'name': 'TaskSchedulingAgent',
            'purpose': 'Handle due dates and recurring tasks',
            'methods': ['set_due_date', 'check_overdue', 'create_recurring_task', 'get_upcoming_tasks']
        },
        {
            'name': 'TaskFilterAgent',
            'purpose': 'Filter and search tasks',
            'methods': ['filter_by_status', 'filter_by_category', 'search_tasks', 'apply_complex_filter']
        },
        {
            'name': 'TaskPersistenceAgent',
            'purpose': 'Handle data persistence to local storage',
            'methods': ['save_to_storage', 'load_from_storage', 'export_tasks', 'import_tasks']
        },
        {
            'name': 'TaskNotificationAgent',
            'purpose': 'Handle reminders and notifications',
            'methods': ['set_reminder', 'check_reminders', 'send_notification', 'schedule_notification']
        },
        {
            'name': 'TaskStatisticsAgent',
            'purpose': 'Generate statistics and analytics',
            'methods': ['calculate_completion_rate', 'count_overdue', 'generate_report', 'track_productivity']
        },
        {
            'name': 'TaskUIAgent',
            'purpose': 'Handle UI state and interactions',
            'methods': ['toggle_dark_mode', 'handle_keyboard_shortcut', 'manage_view_state', 'animate_transition']
        }
    ]
    
    for agent in recommended_agents:
        print(f"\n📦 {agent['name']}")
        print(f"   Purpose: {agent['purpose']}")
        print(f"   Methods: {', '.join(agent['methods'])}")
    
    return analysis_results, recommended_agents

if __name__ == "__main__":
    results, agents = asyncio.run(analyze_todo_requirements())
    print("\n✅ Analysis complete!")
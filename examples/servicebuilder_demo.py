#!/usr/bin/env python3
"""ServiceBuilder Demo - Complete service generation from requirements."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.meta_agents import ServiceBuilder, ServiceBuilderConfig


async def demo_simple_service():
    """Demo building a simple user management service."""

    print("\n" + "=" * 80)
    print("🏗️ SERVICEBUILDER DEMO: Simple User Management Service")
    print("=" * 80)

    # Configure ServiceBuilder
    config = ServiceBuilderConfig(
        enable_ai_analysis=False,  # Use template-based for demo
        auto_generate_agents=True,
        create_workflows=True,
        max_agents_per_service=5,
    )

    builder = ServiceBuilder(config)

    # Define service requirements
    service_request = {
        "name": "UserManagementService",
        "description": "Complete user management system with authentication",
        "requirements_text": """
        Create a user management service that can:
        1. Register new users with email validation
        2. Authenticate users with JWT tokens
        3. Manage user profiles and preferences
        4. Handle password reset functionality
        5. Implement role-based access control
        """,
    }

    print("📋 Service Request:")
    print(f"   Name: {service_request['name']}")
    print(f"   Description: {service_request['description']}")
    print("   Requirements: User registration, authentication, profiles, password reset, RBAC")

    # Build the service
    print("\n🔄 Building service...")
    result = await builder.build_service(service_request)

    if result["success"]:
        service = result["service"]
        print("✅ Service built successfully!")
        print(f"   Service ID: {service['id']}")
        print(f"   Agents generated: {result['agents_generated']}")
        print(f"   Workflow steps: {result['workflow_steps']}")
        print(f"   Requirements analyzed: {result['requirements_analyzed']}")

        # Show generated agents
        print("\n🤖 Generated Agents:")
        for i, agent in enumerate(service["agents"], 1):
            print(f"   {i}. {agent}")

        # Show workflow structure
        workflow = service.get("workflow", {})
        if workflow.get("steps"):
            print("\n🔄 Workflow Steps:")
            for i, step in enumerate(workflow["steps"], 1):
                step_name = step.get("name", step.get("id", f"Step {i}"))
                agent = step.get("agent", "Unknown")
                deps = step.get("dependencies", [])
                dep_info = f" (depends on: {', '.join(deps)})" if deps else ""
                print(f"   {i}. {step_name} - {agent}{dep_info}")

        # Get service metrics
        print("\n📊 Service Metrics:")
        metrics = await builder.get_metrics(service)
        print(f"   Complexity: {metrics['service_size']} ({metrics['complexity_score']} points)")
        print(f"   Estimated Duration: {metrics['estimated_duration']} minutes")
        print(f"   Agent Count: {metrics['agent_count']}")
        print(f"   Workflow Steps: {metrics['workflow_steps']}")

        # Show optimization potential
        print("\n⚡ Optimization Analysis:")
        optimization = await builder.optimize_service(service)
        if optimization.get("optimized"):
            print("   ✅ Workflow optimized for parallel execution")
            if optimization.get("parallel_groups"):
                print(f"   📈 Parallel groups: {len(optimization['parallel_groups'])}")
                print(
                    f"   ⏱️ Estimated duration: {optimization.get('estimated_duration', 'unknown')} minutes"
                )
        else:
            print("   ℹ️ No optimization opportunities found")

        return service

    else:
        print("❌ Service building failed:")
        print(f"   Error: {result['error']}")
        return None


async def demo_ecommerce_service():
    """Demo building a more complex e-commerce service."""

    print("\n" + "=" * 80)
    print("🏗️ SERVICEBUILDER DEMO: E-commerce Platform Service")
    print("=" * 80)

    config = ServiceBuilderConfig(enable_ai_analysis=False, max_agents_per_service=8)

    builder = ServiceBuilder(config)

    service_request = {
        "name": "EcommercePlatform",
        "description": "Complete e-commerce platform with inventory and payments",
        "requirements_text": """
        Build an e-commerce platform that includes:
        1. Product catalog management with categories and search
        2. Shopping cart functionality with session management
        3. Order processing and fulfillment tracking
        4. Payment processing with multiple payment methods
        5. Inventory management with stock tracking
        6. Customer reviews and ratings system
        7. Recommendation engine for personalized suggestions
        8. Admin dashboard for business analytics
        """,
    }

    print("📋 E-commerce Service Request:")
    print(f"   Name: {service_request['name']}")
    print(
        "   Features: Product catalog, cart, orders, payments, inventory, reviews, recommendations, analytics"
    )

    print("\n🔄 Building complex service...")
    result = await builder.build_service(service_request)

    if result["success"]:
        service = result["service"]
        print("✅ E-commerce service built successfully!")
        print(f"   Agents: {result['agents_generated']}")
        print(f"   Workflow complexity: {result['workflow_steps']} steps")

        # Show service complexity analysis
        metrics = await builder.get_metrics(service)
        print("\n📊 Complexity Analysis:")
        print(f"   Service Size: {metrics['service_size']}")
        print(f"   Complexity Score: {metrics['complexity_score']}")
        print(f"   Estimated Development Time: {metrics['estimated_duration']} minutes")

        return service

    else:
        print(f"❌ E-commerce service building failed: {result['error']}")
        return None


async def demo_service_persistence():
    """Demo saving and loading services."""

    print("\n" + "=" * 80)
    print("💾 SERVICEBUILDER DEMO: Service Persistence")
    print("=" * 80)

    builder = ServiceBuilder()

    # Create a simple service
    service_request = {
        "name": "BlogService",
        "description": "Simple blog management service",
        "requirements_text": """
        Create a blog service with:
        1. Post creation and editing
        2. Comment management
        3. User authentication
        """,
    }

    print("📝 Creating blog service...")
    result = await builder.build_service(service_request)

    if result["success"]:
        service = result["service"]
        print("✅ Blog service created")

        # Save service
        output_dir = Path("./demo_output")
        print(f"\n💾 Saving service to {output_dir}...")
        save_result = await builder.save_service(service, output_dir)

        if save_result["success"]:
            print("✅ Service saved successfully!")
            print(f"   Directory: {save_result['service_directory']}")
            print(f"   Files created: {len(save_result['files'])}")
            for file_path in save_result["files"]:
                print(f"   - {Path(file_path).name}")

            # Load service back
            print(f"\n📂 Loading service from {save_result['service_directory']}...")
            loaded_service = await builder.load_service(Path(save_result["service_directory"]))

            print("✅ Service loaded successfully!")
            print(f"   Name: {loaded_service['name']}")
            print(f"   Agents: {len(loaded_service.get('agents', []))}")
            print(f"   Has workflow: {'workflow' in loaded_service}")
            print(f"   Has agent code: {'agent_code' in loaded_service}")

        else:
            print(f"❌ Failed to save service: {save_result['error']}")
    else:
        print(f"❌ Failed to create blog service: {result['error']}")


async def demo_service_builder_capabilities():
    """Demo ServiceBuilder capabilities and features."""

    print("\n" + "=" * 80)
    print("🎯 SERVICEBUILDER CAPABILITIES")
    print("=" * 80)

    builder = ServiceBuilder()
    capabilities = builder.get_capabilities()

    print(f"🏗️ {capabilities['name']} v{capabilities['version']}")
    print(f"📝 {capabilities['description']}")
    print(f"🤖 AI-Powered: {capabilities['ai_powered']}")
    print(f"🔧 Max Agents per Service: {capabilities['max_agents_per_service']}")

    print("\n✨ Features:")
    for feature in capabilities["features"]:
        print(f"   ✅ {feature.replace('_', ' ').title()}")

    print("\n🗣️ Supported Languages:")
    for lang in capabilities["supported_languages"]:
        print(f"   📝 {lang.title()}")

    print("\n🧩 Meta Agents Integration:")
    meta_agents = capabilities["meta_agents"]
    for agent_type, agent_info in meta_agents.items():
        if isinstance(agent_info, dict):
            agent_name = agent_info.get("name", agent_type)
            print(f"   🤖 {agent_name} - {agent_type.replace('_', ' ').title()}")
        else:
            print(f"   🤖 {agent_info} - {agent_type.replace('_', ' ').title()}")


async def main():
    """Run all ServiceBuilder demos."""

    print("🚀 T-DEVELOPER SERVICEBUILDER DEMONSTRATION")
    print("Showcasing automatic service generation using meta agents")
    print("\nDemonstrations:")
    print("1. Simple User Management Service")
    print("2. Complex E-commerce Platform")
    print("3. Service Persistence (Save/Load)")
    print("4. ServiceBuilder Capabilities")

    try:
        # Demo 1: Simple service
        user_service = await demo_simple_service()

        # Demo 2: Complex service
        ecommerce_service = await demo_ecommerce_service()

        # Demo 3: Persistence
        await demo_service_persistence()

        # Demo 4: Capabilities
        await demo_service_builder_capabilities()

        print("\n" + "=" * 80)
        print("🎉 SERVICEBUILDER DEMONSTRATION COMPLETE!")
        print("=" * 80)

        print("\n📈 Summary:")
        if user_service:
            print(f"✅ User Management Service: {len(user_service['agents'])} agents")
        if ecommerce_service:
            print(f"✅ E-commerce Platform: {len(ecommerce_service['agents'])} agents")
        print("✅ Service Persistence: Save/Load functionality")
        print("✅ Capabilities: Full feature demonstration")

        print("\n🚀 ServiceBuilder is ready for:")
        print("- Automatic service generation from requirements")
        print("- AI-powered requirement analysis")
        print("- Agent code generation with templates")
        print("- Workflow orchestration and optimization")
        print("- Service validation and documentation")
        print("- Complete service lifecycle management")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

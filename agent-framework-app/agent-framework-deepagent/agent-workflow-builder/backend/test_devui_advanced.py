"""
Advanced DevUI API Test Script - Agent Framework Specific Tests

This script tests the agent's knowledge of Microsoft Agent Framework
with framework-specific queries and code generation requests.
"""

import json
import time
from datetime import datetime
import requests

# DevUI Configuration
DEVUI_URL = "http://localhost:8080"

# Advanced Agent Framework-specific test queries
ADVANCED_TEST_QUERIES = [
    {
        "id": 1,
        "name": "ChatAgent Creation Code",
        "query": "Show me Python code to create a ChatAgent with Azure OpenAI. Include the imports and explain each parameter."
    },
    {
        "id": 2,
        "name": "Sequential Workflow Implementation",
        "query": "Write Python code for a sequential workflow with 3 agents using Microsoft Agent Framework's WorkflowBuilder. Show the complete implementation."
    },
    {
        "id": 3,
        "name": "Agent with Custom Tools",
        "query": "Create a ChatAgent with custom tool/function calling capabilities. Show how to define tools and register them with the agent in Agent Framework."
    },
    {
        "id": 4,
        "name": "Concurrent Workflow Pattern",
        "query": "Implement a concurrent workflow pattern in Agent Framework where multiple agents can run in parallel. Show the Python code with WorkflowBuilder."
    },
    {
        "id": 5,
        "name": "Error Handling in Workflows",
        "query": "How do I implement proper error handling and retry logic in Agent Framework workflows? Provide code examples with try-catch patterns."
    },
    {
        "id": 6,
        "name": "Agent Context and Memory",
        "query": "Explain and show code for how to maintain conversation context and memory across multiple turns in Agent Framework ChatAgent."
    },
    {
        "id": 7,
        "name": "Streaming Responses",
        "query": "How do I implement streaming responses in Agent Framework? Show code for both creating an agent that streams and consuming the stream."
    },
    {
        "id": 8,
        "name": "Multi-Agent Coordination",
        "query": "Design a multi-agent system in Agent Framework where agents need to coordinate and pass data between each other. Show the workflow implementation."
    }
]


def get_entity_id():
    """Fetch the correct entity ID from DevUI."""
    try:
        response = requests.get(f"{DEVUI_URL}/v1/entities", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Handle both wrapped and unwrapped responses
        entities = data.get("entities", data) if isinstance(data, dict) else data
        
        if entities and len(entities) > 0:
            entity_id = entities[0].get("id")
            print(f"✓ Found entity: {entities[0].get('name')} (ID: {entity_id})")
            return entity_id
        else:
            print("⚠ No entities found in DevUI")
            return None
    except Exception as e:
        print(f"❌ Error fetching entities: {e}")
        return None


def test_query(query_data, entity_id):
    """Send a test query to DevUI and capture the response."""
    print(f"\n{'='*80}")
    print(f"Advanced Test #{query_data['id']}: {query_data['name']}")
    print(f"{'='*80}")
    print(f"Query: {query_data['query'][:100]}...")
    
    start_time = time.time()
    
    try:
        payload = {
            "model": "agent-framework",
            "input": query_data["query"],
            "extra_body": {
                "entity_id": entity_id
            }
        }
        
        response = requests.post(
            f"{DEVUI_URL}/v1/responses",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Increased timeout for complex queries
        )
        response.raise_for_status()
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = response.json()
        
        # Extract response text from nested structure
        response_text = ""
        if "output" in result and len(result["output"]) > 0:
            output = result["output"][0]
            if "content" in output and len(output["content"]) > 0:
                content = output["content"][0]
                response_text = content.get("text", "")
        
        print(f"\n✓ Response received in {duration:.2f}s")
        print("\nResponse Preview:")
        print("-" * 80)
        # Show more of the response for code-heavy answers
        preview_length = 800
        print(response_text[:preview_length] + ("..." if len(response_text) > preview_length else ""))
        print("-" * 80)
        
        # Check if response contains code
        has_code = "```python" in response_text or "from agent_framework" in response_text
        print(f"\n📊 Analysis: Contains Python code: {'✓ Yes' if has_code else '✗ No'}")
        
        return {
            "test_id": query_data["id"],
            "test_name": query_data["name"],
            "query": query_data["query"],
            "response": response_text,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "has_code": has_code,
            "response_length": len(response_text),
            "full_result": result
        }
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return {
            "test_id": query_data["id"],
            "test_name": query_data["name"],
            "query": query_data["query"],
            "error": "Timeout after 60 seconds",
            "status": "timeout",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "test_id": query_data["id"],
            "test_name": query_data["name"],
            "query": query_data["query"],
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Run all advanced tests and save results."""
    print("🚀 Advanced DevUI API Test Script - Agent Framework Specific")
    print("=" * 80)
    
    # Check if DevUI is running
    try:
        requests.get(f"{DEVUI_URL}/health", timeout=5)
        print(f"✓ DevUI is running at {DEVUI_URL}")
    except Exception:
        print(f"❌ Cannot connect to DevUI at {DEVUI_URL}")
        print("   Make sure DevUI is running with: uv run python test_devui.py")
        return
    
    # Get entity ID
    entity_id = get_entity_id()
    if not entity_id:
        print("❌ Cannot proceed without entity ID")
        return
    
    print("\n🎯 Running Advanced Agent Framework Tests...")
    print("   These tests evaluate framework-specific knowledge and code generation\n")
    
    # Run tests
    results = []
    for query_data in ADVANCED_TEST_QUERIES:
        result = test_query(query_data, entity_id)
        results.append(result)
        time.sleep(2)  # Longer pause between complex queries
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"devui_advanced_test_results_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print detailed summary
    print(f"\n{'='*80}")
    print("📊 Advanced Test Summary")
    print(f"{'='*80}")
    
    successful = sum(1 for r in results if r.get("status") == "success")
    failed = len(results) - successful
    has_code_count = sum(1 for r in results if r.get("has_code", False))
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {successful} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Responses with Code: {has_code_count}/{successful}")
    
    if successful > 0:
        avg_duration = sum(r.get("duration", 0) for r in results if r.get("status") == "success") / successful
        avg_length = sum(r.get("response_length", 0) for r in results if r.get("status") == "success") / successful
        print(f"Average Response Time: {avg_duration:.2f}s")
        print(f"Average Response Length: {avg_length:.0f} characters")
    
    print(f"\n📁 Results saved to: {filename}")
    
    # Quality assessment
    print(f"\n{'='*80}")
    print("🎯 Quality Assessment")
    print(f"{'='*80}")
    
    if has_code_count >= len(results) * 0.7:
        print("✅ EXCELLENT: Agent provides code examples consistently")
    elif has_code_count >= len(results) * 0.5:
        print("⚠️  GOOD: Agent provides some code examples")
    else:
        print("❌ NEEDS IMPROVEMENT: Agent rarely provides code examples")
    
    print("\n💡 Next Steps:")
    print("   1. Review the responses in the JSON file")
    print("   2. Check code quality and Agent Framework API usage")
    print("   3. Validate against official Agent Framework documentation")
    print("   4. Share interesting responses with GitHub Copilot for analysis")


if __name__ == "__main__":
    main()

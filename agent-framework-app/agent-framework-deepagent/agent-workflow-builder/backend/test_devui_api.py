"""
DevUI API Test Script with Response Logging

This script sends test queries to the DevUI API and logs all responses
for later review and analysis.
"""

import json
import time
from datetime import datetime
import requests

# DevUI Configuration
DEVUI_URL = "http://localhost:8080"
ENTITY_ID = "agent_in-memory_testagent_1bb5eb18"  # Update if needed

# Test queries from DEVUI_QUICK_TEST.md
TEST_QUERIES = [
    {
        "id": 1,
        "name": "Basic Test",
        "query": "Hello! Can you introduce yourself and explain what you can help me with?"
    },
    {
        "id": 2,
        "name": "Context Memory Test",
        "query": "My name is Alex. Please remember this. What's my name?"
    },
    {
        "id": 3,
        "name": "Workflow Design Test",
        "query": "I need to design a workflow with 3 agents: a research agent, an analysis agent, and a reporting agent. How should they work together?"
    },
    {
        "id": 4,
        "name": "Technical Question",
        "query": "What's the difference between sequential and concurrent workflow patterns? When should I use each?"
    },
    {
        "id": 5,
        "name": "Best Practices",
        "query": "What are the top 5 best practices for building production-ready agent workflows?"
    }
]


def get_entity_id():
    """Fetch the correct entity ID from DevUI."""
    try:
        response = requests.get(f"{DEVUI_URL}/v1/entities")
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
    print(f"Test #{query_data['id']}: {query_data['name']}")
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
            timeout=30
        )
        response.raise_for_status()
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = response.json()
        
        # Extract response text
        response_text = ""
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                response_text = choice["message"]["content"]
        
        print(f"\n✓ Response received in {duration:.2f}s")
        print(f"\nResponse Preview:")
        print("-" * 80)
        print(response_text[:500] + ("..." if len(response_text) > 500 else ""))
        print("-" * 80)
        
        return {
            "test_id": query_data["id"],
            "test_name": query_data["name"],
            "query": query_data["query"],
            "response": response_text,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "full_result": result
        }
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 30 seconds")
        return {
            "test_id": query_data["id"],
            "test_name": query_data["name"],
            "query": query_data["query"],
            "error": "Timeout after 30 seconds",
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
    """Run all tests and save results."""
    print("🚀 DevUI API Test Script")
    print("=" * 80)
    
    # Check if DevUI is running
    try:
        health = requests.get(f"{DEVUI_URL}/health", timeout=5)
        print(f"✓ DevUI is running at {DEVUI_URL}")
    except:
        print(f"❌ Cannot connect to DevUI at {DEVUI_URL}")
        print("   Make sure DevUI is running with: uv run python test_devui.py")
        return
    
    # Get entity ID
    entity_id = get_entity_id()
    if not entity_id:
        print("❌ Cannot proceed without entity ID")
        return
    
    # Run tests
    results = []
    for query_data in TEST_QUERIES:
        result = test_query(query_data, entity_id)
        results.append(result)
        time.sleep(1)  # Brief pause between tests
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"devui_test_results_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{'='*80}")
    print("📊 Test Summary")
    print(f"{'='*80}")
    
    successful = sum(1 for r in results if r.get("status") == "success")
    failed = len(results) - successful
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {successful} ✓")
    print(f"Failed: {failed} ✗")
    
    if successful > 0:
        avg_duration = sum(r.get("duration", 0) for r in results if r.get("status") == "success") / successful
        print(f"Average Response Time: {avg_duration:.2f}s")
    
    print(f"\n📁 Results saved to: {filename}")
    print("\nTo review responses, open the JSON file or paste them to GitHub Copilot for analysis.")


if __name__ == "__main__":
    main()

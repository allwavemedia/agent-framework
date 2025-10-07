"""
Automated API Endpoint Testing Suite
Tests all Agent Workflow Builder API endpoints following Microsoft Agent Framework patterns.
"""
import asyncio
import json
from typing import Dict, Any, List
import httpx
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
API_V1 = f"{BASE_URL}/api/v1"
TIMEOUT = 30.0

class APITestSuite:
    """Comprehensive API endpoint testing suite."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_v1 = f"{base_url}/api/v1"
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.test_results: List[Dict[str, Any]] = []
        self.created_resources: Dict[str, int] = {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test(self, name: str, method: str, endpoint: str, status: str, 
                 response_code: int = None, error: str = None):
        """Log test result."""
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_name": name,
            "method": method,
            "endpoint": endpoint,
            "status": status,
            "response_code": response_code,
            "error": error
        }
        self.test_results.append(result)
        
        # Color output
        status_emoji = "✅" if status == "PASS" else "❌"
        print(f"{status_emoji} {method:6} {endpoint:50} [{response_code}] - {name}")
        if error:
            print(f"   Error: {error}")
    
    async def test_health_check(self) -> bool:
        """Test: Health check endpoint."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            success = response.status_code == 200 and response.json().get("status") == "healthy"
            
            self.log_test(
                "Health Check",
                "GET",
                "/health",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("Health Check", "GET", "/health", "FAIL", error=str(e))
            return False
    
    async def test_create_agent(self) -> bool:
        """Test: Create a new agent."""
        payload = {
            "name": "Automated Test Agent",
            "description": "Agent created by automated test suite",
            "agent_type": "chat_agent",
            "instructions": "You are a helpful AI assistant for testing purposes.",
            "model_settings": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "tools": []
        }
        
        try:
            response = await self.client.post(
                f"{self.api_v1}/agents/",
                json=payload
            )
            success = response.status_code == 201
            
            if success:
                data = response.json()
                self.created_resources["agent_id"] = data["id"]
                print(f"   Created Agent ID: {data['id']}")
            
            self.log_test(
                "Create Agent",
                "POST",
                "/api/v1/agents/",
                "PASS" if success else "FAIL",
                response.status_code,
                error=response.text if not success else None
            )
            return success
        except Exception as e:
            self.log_test("Create Agent", "POST", "/api/v1/agents/", "FAIL", error=str(e))
            return False
    
    async def test_list_agents(self) -> bool:
        """Test: List all agents."""
        try:
            response = await self.client.get(f"{self.api_v1}/agents/")
            success = response.status_code == 200
            
            if success:
                agents = response.json()
                print(f"   Found {len(agents)} agent(s)")
            
            self.log_test(
                "List Agents",
                "GET",
                "/api/v1/agents/",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("List Agents", "GET", "/api/v1/agents/", "FAIL", error=str(e))
            return False
    
    async def test_get_agent(self) -> bool:
        """Test: Get agent by ID."""
        agent_id = self.created_resources.get("agent_id")
        if not agent_id:
            print("   ⚠️  Skipping: No agent ID available")
            return True
        
        try:
            response = await self.client.get(f"{self.api_v1}/agents/{agent_id}")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                print(f"   Retrieved Agent: {data['name']}")
            
            self.log_test(
                "Get Agent by ID",
                "GET",
                f"/api/v1/agents/{agent_id}",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("Get Agent by ID", "GET", f"/api/v1/agents/{agent_id}", "FAIL", error=str(e))
            return False
    
    async def test_update_agent(self) -> bool:
        """Test: Update agent."""
        agent_id = self.created_resources.get("agent_id")
        if not agent_id:
            print("   ⚠️  Skipping: No agent ID available")
            return True
        
        payload = {
            "description": "Updated description by automated test",
            "model_settings": {
                "model": "gpt-4",
                "temperature": 0.8
            }
        }
        
        try:
            response = await self.client.patch(
                f"{self.api_v1}/agents/{agent_id}",
                json=payload
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                print(f"   Updated Agent: temperature = {data['model_settings']['temperature']}")
            
            self.log_test(
                "Update Agent",
                "PATCH",
                f"/api/v1/agents/{agent_id}",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("Update Agent", "PATCH", f"/api/v1/agents/{agent_id}", "FAIL", error=str(e))
            return False
    
    async def test_create_workflow(self) -> bool:
        """Test: Create a new workflow."""
        payload = {
            "name": "Automated Test Workflow",
            "description": "Workflow created by automated test suite",
            "version": "1.0.0",
            "tags": ["test", "automated"],
            "is_template": False,
            "is_public": False
        }
        
        try:
            response = await self.client.post(
                f"{self.api_v1}/workflows/",
                json=payload
            )
            success = response.status_code == 201
            
            if success:
                data = response.json()
                self.created_resources["workflow_id"] = data["id"]
                print(f"   Created Workflow ID: {data['id']}")
            
            self.log_test(
                "Create Workflow",
                "POST",
                "/api/v1/workflows/",
                "PASS" if success else "FAIL",
                response.status_code,
                error=response.text if not success else None
            )
            return success
        except Exception as e:
            self.log_test("Create Workflow", "POST", "/api/v1/workflows/", "FAIL", error=str(e))
            return False
    
    async def test_list_workflows(self) -> bool:
        """Test: List all workflows."""
        try:
            response = await self.client.get(f"{self.api_v1}/workflows/")
            success = response.status_code == 200
            
            if success:
                workflows = response.json()
                print(f"   Found {len(workflows)} workflow(s)")
            
            self.log_test(
                "List Workflows",
                "GET",
                "/api/v1/workflows/",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("List Workflows", "GET", "/api/v1/workflows/", "FAIL", error=str(e))
            return False
    
    async def test_get_workflow(self) -> bool:
        """Test: Get workflow by ID."""
        workflow_id = self.created_resources.get("workflow_id")
        if not workflow_id:
            print("   ⚠️  Skipping: No workflow ID available")
            return True
        
        try:
            response = await self.client.get(f"{self.api_v1}/workflows/{workflow_id}")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                print(f"   Retrieved Workflow: {data['name']}")
            
            self.log_test(
                "Get Workflow by ID",
                "GET",
                f"/api/v1/workflows/{workflow_id}",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("Get Workflow by ID", "GET", f"/api/v1/workflows/{workflow_id}", "FAIL", error=str(e))
            return False
    
    async def test_create_workflow_node(self) -> bool:
        """Test: Create workflow node."""
        workflow_id = self.created_resources.get("workflow_id")
        agent_id = self.created_resources.get("agent_id")
        
        if not workflow_id or not agent_id:
            print("   ⚠️  Skipping: Missing workflow or agent ID")
            return True
        
        payload = {
            "workflow_id": workflow_id,
            "name": "Test Node",
            "executor_type": "agent",
            "agent_id": agent_id,
            "position_x": 100.0,
            "position_y": 100.0,
            "config": {},
            "is_start_node": True,
            "is_output_node": False
        }
        
        try:
            response = await self.client.post(
                f"{self.api_v1}/workflows/{workflow_id}/nodes",
                json=payload
            )
            success = response.status_code == 201
            
            if success:
                data = response.json()
                self.created_resources["node_id"] = data["id"]
                print(f"   Created Node ID: {data['id']}")
            
            self.log_test(
                "Create Workflow Node",
                "POST",
                f"/api/v1/workflows/{workflow_id}/nodes",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("Create Workflow Node", "POST", f"/api/v1/workflows/{workflow_id}/nodes", "FAIL", error=str(e))
            return False
    
    async def test_create_execution(self) -> bool:
        """Test: Create workflow execution."""
        workflow_id = self.created_resources.get("workflow_id")
        if not workflow_id:
            print("   ⚠️  Skipping: No workflow ID available")
            return True
        
        payload = {
            "workflow_id": workflow_id,
            "input_data": {
                "message": "Test execution input"
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.api_v1}/executions/",
                json=payload
            )
            success = response.status_code == 201
            
            if success:
                data = response.json()
                self.created_resources["execution_id"] = data["id"]
                print(f"   Created Execution ID: {data['id']}, Status: {data['status']}")
            
            self.log_test(
                "Create Execution",
                "POST",
                "/api/v1/executions/",
                "PASS" if success else "FAIL",
                response.status_code,
                error=response.text if not success else None
            )
            return success
        except Exception as e:
            self.log_test("Create Execution", "POST", "/api/v1/executions/", "FAIL", error=str(e))
            return False
    
    async def test_list_executions(self) -> bool:
        """Test: List workflow executions."""
        try:
            response = await self.client.get(f"{self.api_v1}/executions/")
            success = response.status_code == 200
            
            if success:
                executions = response.json()
                print(f"   Found {len(executions)} execution(s)")
            
            self.log_test(
                "List Executions",
                "GET",
                "/api/v1/executions/",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("List Executions", "GET", "/api/v1/executions/", "FAIL", error=str(e))
            return False
    
    async def test_get_execution(self) -> bool:
        """Test: Get execution by ID."""
        execution_id = self.created_resources.get("execution_id")
        if not execution_id:
            print("   ⚠️  Skipping: No execution ID available")
            return True
        
        try:
            response = await self.client.get(f"{self.api_v1}/executions/{execution_id}")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                print(f"   Execution Status: {data['status']}")
            
            self.log_test(
                "Get Execution by ID",
                "GET",
                f"/api/v1/executions/{execution_id}",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("Get Execution by ID", "GET", f"/api/v1/executions/{execution_id}", "FAIL", error=str(e))
            return False
    
    async def test_delete_agent(self) -> bool:
        """Test: Delete agent (cleanup)."""
        agent_id = self.created_resources.get("agent_id")
        if not agent_id:
            print("   ⚠️  Skipping: No agent ID to delete")
            return True
        
        try:
            response = await self.client.delete(f"{self.api_v1}/agents/{agent_id}")
            success = response.status_code == 204
            
            self.log_test(
                "Delete Agent",
                "DELETE",
                f"/api/v1/agents/{agent_id}",
                "PASS" if success else "FAIL",
                response.status_code
            )
            return success
        except Exception as e:
            self.log_test("Delete Agent", "DELETE", f"/api/v1/agents/{agent_id}", "FAIL", error=str(e))
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all API endpoint tests in sequence."""
        print("\n" + "="*80)
        print("  Agent Workflow Builder - API Endpoint Test Suite")
        print("="*80 + "\n")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Create Agent", self.test_create_agent),
            ("List Agents", self.test_list_agents),
            ("Get Agent by ID", self.test_get_agent),
            ("Update Agent", self.test_update_agent),
            ("Create Workflow", self.test_create_workflow),
            ("List Workflows", self.test_list_workflows),
            ("Get Workflow by ID", self.test_get_workflow),
            ("Create Workflow Node", self.test_create_workflow_node),
            ("Create Execution", self.test_create_execution),
            ("List Executions", self.test_list_executions),
            ("Get Execution by ID", self.test_get_execution),
            ("Delete Agent (Cleanup)", self.test_delete_agent),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = await test_func()
                results.append(result)
            except Exception as e:
                print(f"❌ {name} - Unexpected error: {str(e)}")
                results.append(False)
        
        # Summary
        print("\n" + "="*80)
        passed = sum(results)
        total = len(results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"  Test Summary: {passed}/{total} tests passed ({pass_rate:.1f}%)")
        print("="*80 + "\n")
        
        # Detailed results
        print("Created Resources:")
        for key, value in self.created_resources.items():
            print(f"  - {key}: {value}")
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": pass_rate,
            "results": self.test_results,
            "created_resources": self.created_resources
        }


async def main():
    """Main test runner."""
    async with APITestSuite() as suite:
        summary = await suite.run_all_tests()
        
        # Save results to file
        output_file = "test_results.json"
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nDetailed results saved to: {output_file}")
        
        # Exit with appropriate code
        exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())

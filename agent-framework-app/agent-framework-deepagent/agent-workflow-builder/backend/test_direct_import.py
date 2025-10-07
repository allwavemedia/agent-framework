"""
Direct import test to see actual error
"""
import sys
import traceback

try:
    print("Testing imports...")
    from app.models import Agent, AgentResponse
    from app.services.agent_service import AgentService
    from app.api.routes.agents import router
    
    print("✅ All imports successful!")
    print(f"Agent type: {Agent}")
    print(f"AgentResponse type: {AgentResponse}")
    
    # Test if AgentResponse can be created from Agent fields
    print("\nTesting field compatibility...")
    print(f"Agent fields: {Agent.__fields__.keys()}")
    print(f"AgentResponse fields: {AgentResponse.__fields__.keys()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

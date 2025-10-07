"""Quick test to diagnose list agents issue."""
import asyncio
import httpx

async def test_list_agents():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://127.0.0.1:8000/api/v1/agents/")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_list_agents())

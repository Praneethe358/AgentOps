import asyncio
import json
from httpx import AsyncClient, ASGITransport
from app.main import app

async def verify_phase_5():
    print("🚀 Initializing Phase 5 FastAPI & SSE Endpoints Test...")
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # 1. Health check
        res = await client.get("/health")
        print(f"\n--- Health Check --- Status: {res.status_code}, Body: {res.json()}")
        assert res.status_code == 200
        
        # 2. Submit task
        submit_payload = {
            "task_description": "Write a python function `is_prime(n)` to test if a number is prime.",
            "code_context": "def is_prime(n):\n    pass"
        }
        res = await client.post("/api/v1/tasks/submit", json=submit_payload)
        print(f"\n--- Submit Task --- Status: {res.status_code}")
        data = res.json()
        print(f"Response: {data}")
        thread_id = data["thread_id"]
        assert "thread_id" in data
        
        # 3. Fetch initial state
        res = await client.get(f"/api/v1/tasks/{thread_id}/state")
        print(f"\n--- Get Initial Task State --- Status: {res.status_code}")
        state_data = res.json()
        print(f"Is Paused: {state_data['is_paused']}")
        
        # 4. Stream task execution
        print(f"\n--- Streaming Task Execution for Thread {thread_id} ---")
        async with client.stream("GET", f"/api/v1/tasks/{thread_id}/stream") as response:
            assert response.status_code == 200
            async for line in response.aiter_lines():
                if line:
                    print(f"SSE Line: {line}")
                    
        # 5. Get state after streaming (should be paused for approval)
        res = await client.get(f"/api/v1/tasks/{thread_id}/state")
        print(f"\n--- State After Stream --- Status: {res.status_code}")
        state_data = res.json()
        print(f"Is Paused: {state_data['is_paused']}")
        print(f"Interrupt Payload: {state_data['interrupt_payload']}")
        
        # 6. Approve task
        approve_payload = {"approved": True}
        res = await client.post(f"/api/v1/tasks/{thread_id}/approve", json=approve_payload)
        print(f"\n--- Submit Approval --- Status: {res.status_code}, Response: {res.json()}")
        assert res.status_code == 200
        
        # Give async task time to finish execution
        await asyncio.sleep(2)
        
        # 7. Check final state
        res = await client.get(f"/api/v1/tasks/{thread_id}/state")
        print(f"\n--- Final Task State --- Status: {res.status_code}")
        final_data = res.json()
        print(f"Is Paused: {final_data['is_paused']}")
        print(f"Human Approved Value: {final_data['current_values'].get('human_approved')}")

        print("\n✅ Phase 5 FastAPI & SSE Endpoints verified successfully!")

if __name__ == "__main__":
    asyncio.run(verify_phase_5())

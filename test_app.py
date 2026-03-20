import os
from fastapi.testclient import TestClient
from app.main import app

def test_generate():
    client = TestClient(app)
    
    payload = {
        "prompt": "Hi, my name is Alice Smith. My email address is alice.smith@example.com and my phone number is 555-0199. Write a brief professional intro for me.",
        "target_model": "gemini"
    }

    print("Sending payload:", payload)
    response = client.post("/api/v1/generate", json=payload)
    
    if response.status_code != 200:
        print(f"FAILED with status {response.status_code}: {response.text}")
        return

    data = response.json()
    
    print("\n=== Sovereign Mesh Gateway Test Results ===\n")
    print(f"Original Prompt : {data['original_prompt']}")
    print(f"Redacted Prompt : {data['redacted_prompt']}")
    print(f"PII Mapping     : {data['pii_map']}")
    print(f"Cloud Response  : {data['cloud_response']}")
    print(f"Final Response  : {data['final_response']}")
    
    # Assertions
    try:
        assert "Alice" not in data['redacted_prompt'], "Failed: 'Alice' found in redacted prompt!"
        assert "alice.smith@example.com" not in data['redacted_prompt'], "Failed: Email found in redacted prompt!"
        print("\n✅ Verification Passed: PII successfully redacted before Cloud LLM.")
    except AssertionError as e:
        print(f"\n❌ Verification Failed: {e}")

if __name__ == "__main__":
    test_generate()

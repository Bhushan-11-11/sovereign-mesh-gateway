import httpx
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
LOCAL_MODEL = "llama3"

SYSTEM_PROMPT = """
You are a highly secure Data Privacy Filter. Your job is to extract any Personally Identifiable Information (PII) from the user's text.
PII includes: Names, Email Addresses, Phone Numbers, Social Security Numbers, Physical Addresses, etc.

Return the result EXACTLY as a valid JSON object where keys are the specific tags you will use to replace the text (e.g., "[NAME_1]", "[EMAIL_1]") and values are the original exact PII strings found in the text.
If no PII is found, return {}. Do not include any explanations or surrounding text. Output MUST be strictly JSON format.
"""

async def redact_pii(prompt: str) -> tuple[str, dict]:
    """
    Calls local Ollama model to identify PII, then replaces it in the original string.
    Returns the redacted string and the mapping of tags to original PII.
    """
    payload = {
        "model": LOCAL_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\nUser Text: {prompt}",
        "stream": False,
        "format": "json"  # Ensure it enforces JSON output if the model supports it
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(OLLAMA_URL, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "{}").strip()
            
            # Parse the JSON mapping
            try:
                pii_map = json.loads(response_text)
            except json.JSONDecodeError:
                pii_map = {}
            
            # Replace the PII in the prompt with the secure tags
            redacted_prompt = prompt
            for tag, original_val in pii_map.items():
                if isinstance(original_val, str) and original_val.strip():
                    redacted_prompt = redacted_prompt.replace(original_val, tag)
            
            return redacted_prompt, pii_map
        except httpx.RequestError as e:
            print(f"Error querying Ollama: {e}")
            raise Exception("Local Privacy Filter (Ollama) is unavailable. Failing securely to protect data.")

async def restore_pii(text: str, pii_map: dict) -> str:
    """
    Restores the original PII back into the text by replacing the secure tags.
    """
    restored_text = text
    for tag, original_val in pii_map.items():
        if isinstance(original_val, str):
            restored_text = restored_text.replace(tag, original_val)
    return restored_text

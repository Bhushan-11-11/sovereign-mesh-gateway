from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

from app.privacy_filter import redact_pii, restore_pii
from app.cloud_agent import query_cloud_llm

app = FastAPI(
    title="Sovereign Mesh Gateway",
    description="A privacy-preserving proxy gateway to cloud LLMs.",
    version="1.0.0"
)

class PromptRequest(BaseModel):
    prompt: str
    target_model: str = "gemini" # Defaults to Gemini

class PromptResponse(BaseModel):
    original_prompt: str
    redacted_prompt: str
    cloud_response: str
    final_response: str
    pii_map: Dict[str, str]

@app.post("/api/v1/generate", response_model=PromptResponse)
async def generate_response(request: PromptRequest):
    # Step 1: Privacy filter - locally extract and replace PII
    try:
        redacted_prompt, pii_map = await redact_pii(request.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Local privacy filter failed: {str(e)}")

    # Step 2: Cloud Inference - Send sanitized prompt to the Cloud LLM
    try:
        cloud_response = await query_cloud_llm(redacted_prompt, request.target_model)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Cloud LLM request failed: {str(e)}")

    # Step 3: De-anonymize / Restore PII - Restore the redacted values in the final response
    try:
        final_response = await restore_pii(cloud_response, pii_map)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore PII values: {str(e)}")

    return PromptResponse(
        original_prompt=request.prompt,
        redacted_prompt=redacted_prompt,
        cloud_response=cloud_response,
        final_response=final_response,
        pii_map=pii_map
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Sovereign Mesh Gateway"}

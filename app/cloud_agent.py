import os
import google.generativeai as genai

# Setup Gemini API key silently
api_key = os.environ.get("GEMINI_API_KEY", "")
def configure_gemini():
    if api_key:
        genai.configure(api_key=api_key)

configure_gemini()

async def query_cloud_llm(prompt: str, model_name: str = "gemini") -> str:
    """
    Sends the sanitized prompt to the chosen Cloud LLM.
    Presently, it supports Gemini models. We fallback to mock if no API key is provided for testing.
    """
    if not api_key:
        print("WARNING: GEMINI_API_KEY not found in environment. Returning a mock Cloud response.")
        return f"Mock Cloud Response based on sanitized prompt: '''{prompt}'''"

    if "gemini" in model_name.lower():
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        try:
            # Attempt async generation
            response = await model.generate_content_async(prompt)
            return response.text
        except AttributeError:
            # Fallback for older SDK versions
            response = model.generate_content(prompt)
            return response.text
    else:
        raise ValueError(f"Model {model_name} is not currently supported in this prototype.")

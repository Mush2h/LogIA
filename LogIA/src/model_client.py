import os
import re
from openai import OpenAI
from llama_index.llms.openai import OpenAI as LlamaOpenAI

DEEPINFRA_BASE_URL = "https://api.deepinfra.com/v1/openai"

# DeepInfra model identifiers
DEEPINFRA_MODELS = {
    "phi4":           "microsoft/phi-4",
    "deepseek-r1_32b": "deepseek-ai/DeepSeek-R1",
    "llama3.2":       "meta-llama/Llama-3.2-11B-Vision-Instruct",
}


def build_openai_model(temperature=0.1):
    """Build a GPT-4 model wrapper using llama_index (OpenAI)."""
    return LlamaOpenAI(
        model="gpt-4",
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY")
    )


def query_openai(llm, prompt):
    """Query OpenAI GPT-4 via llama_index wrapper."""
    return llm.complete(prompt).text


def build_deepinfra_client():
    """Build a DeepInfra client (OpenAI-compatible API)."""
    return OpenAI(
        api_key=os.getenv("DEEPINFRA_API_KEY"),
        base_url=DEEPINFRA_BASE_URL
    )


def query_deepinfra(prompt, model_key, temperature=0.0):
    """
    Query a model hosted on DeepInfra.

    Args:
        prompt (str): Input text prompt.
        model_key (str): Key from DEEPINFRA_MODELS (e.g. "phi4", "deepseek-r1_32b").
        temperature (float): Sampling temperature.

    Returns:
        str | None: Model response or None if request failed.
    """
    model_id = DEEPINFRA_MODELS.get(model_key)
    if not model_id:
        print(f"Unknown DeepInfra model key: {model_key}")
        return None

    client = build_deepinfra_client()
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error querying DeepInfra ({model_id}): {e}")
        return None


def clean_deepseek_response(response):
    """Remove <think>...</think> tags from DeepSeek model responses."""
    if response:
        return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
    return response

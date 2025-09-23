import os
import json
import requests
import re
from datetime import datetime
from lib.parse_logs import parse_logs
from dotenv import load_dotenv

# LlamaIndex import for OpenAI
from llama_index.llms.openai import OpenAI as LlamaOpenAI

# Local dataset handler
from src.dataset import Dataset

# 📁 Load environment variables (e.g., OpenAI API key)
load_dotenv()

# 📂 Output directory for model responses
output_dir = "model_responses"
os.makedirs(output_dir, exist_ok=True)


# 🔧 Utility functions ---------------------------------------------------------

def build_openai_model():
    """
    Initialize the OpenAI GPT-4 model via LlamaIndex wrapper.

    Returns:
        LlamaOpenAI: Configured GPT-4 model client.
    """
    return LlamaOpenAI(
        model="gpt-4",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )


def query_openai(llm, prompt):
    """
    Query OpenAI GPT-4 through LlamaIndex.

    Args:
        llm (LlamaOpenAI): GPT-4 client object.
        prompt (str): Text prompt to send to the model.

    Returns:
        str: Model response text.
    """
    response = llm.complete(prompt)
    return response.text


def query_ollama_api(prompt, model="phi4", base_url="http://localhost:11435"):
    """
    Query a local Ollama model API (streaming mode).

    Args:
        prompt (str): Input text prompt.
        model (str): Model identifier in Ollama (e.g., phi4, llama3.2).
        base_url (str): Base URL of the Ollama service.

    Returns:
        str | None: Full response text, or None if request failed.
    """
    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": 0.3,
        "stream": True
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=300)
        response.raise_for_status()

        # Collect streaming output
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    obj = json.loads(line)
                    if "response" in obj:
                        full_response += obj["response"]
                except json.JSONDecodeError:
                    print(f"⚠️ Could not decode a line: {line}")

        return full_response.strip()

    except requests.exceptions.RequestException as e:
        print(f"❌ Error querying Ollama API: {e}")
        return None


def select_models():
    """
    Interactive menu to select which models will be queried.

    Returns:
        list[str]: List of selected model identifiers.
    """
    print("\n📌 Select the model(s) you want to use to answer the questions:")
    print("1. All models")
    print("2. Only OpenAI GPT-4")
    print("3. Only Ollama - phi4")
    print("4. Only Ollama - deepseek-r1_32b")
    print("5. Only Ollama - llama3.2")

    option = input("Enter the number of your choice: ").strip()

    if option == "1":
        return ["openai", "phi4", "deepseek-r1_32b", "llama3.2"]
    elif option == "2":
        return ["openai"]
    elif option == "3":
        return ["phi4"]
    elif option == "4":
        return ["deepseek-r1_32b"]
    elif option == "5":
        return ["llama3.2"]
    else:
        print("❌ Invalid option. Using all models by default.")
        return ["openai", "phi4", "deepseek-r1_32b", "llama3.2"]


# 🚀 Main pipeline ------------------------------------------------------------

def main():
    """
    Main execution workflow:
    1. Parse raw log data.
    2. Generate a question prompt for the selected topic.
    3. Query selected models (OpenAI GPT-4 and/or Ollama backends).
    4. Save model responses to JSON files.
    5. Provide an interactive menu to inspect responses.
    """
    ds = Dataset("data/")
    topic = "Topic 1 - Basic Events"  # Default topic (can be modified)
    filename = "parsed_logs_by_unique_rule_description.json"

    # Parse log data into multiple JSON formats
    parse_logs("data/real_events.csv", "data/parsed_logs_filtered.json",
               "data/parsed_logs_all.json", "data/parsed_logs_by_unique_rule_description.json")

    # Generate a structured prompt for the selected topic
    prompt = ds.generate_prompt(filename, topic)
    print("\n📝 Generated prompt:\n")
    print(prompt)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    generated_answers = {}

    # Select models interactively
    models_to_use = select_models()

    # --- Query OpenAI GPT-4 --------------------------------------------------
    if "openai" in models_to_use:
        print("\n🤖 Querying model: OpenAI GPT-4...\n")
        try:
            llm_openai = build_openai_model()
            answer_openai = query_openai(llm_openai, prompt)

            output_path_openai = os.path.join(output_dir, f"response_openai_gpt4_{timestamp}.json")
            with open(output_path_openai, "w", encoding="utf-8") as f:
                json.dump({
                    "model": "openai_gpt4",
                    "file": filename,
                    "topic": topic,
                    "prompt": prompt,
                    "answer": answer_openai
                }, f, ensure_ascii=False, indent=2)

            print(f"✅ OpenAI response saved to: {output_path_openai}")
            generated_answers["1"] = output_path_openai

        except Exception as e:
            print(f"⚠️ Error querying OpenAI: {e}")

    # --- Query Ollama models -------------------------------------------------
    ollama_models = ["phi4", "deepseek-r1_32b", "llama3.2"]
    idx = 2
    for ollama_model in ollama_models:
        if ollama_model in models_to_use:
            print(f"\n🤖 Querying Ollama model: {ollama_model}...\n")
            model_api_name = ollama_model.replace('_', ':').replace('_', '.')
            answer_ollama = query_ollama_api(prompt, model=model_api_name)

            if answer_ollama:
                # Clean DeepSeek responses (remove <think>...</think> tags)
                if ollama_model == "deepseek-r1_32b":
                    answer_ollama = re.sub(r"<think>.*?</think>", "", answer_ollama, flags=re.DOTALL).strip()

                output_path_ollama = os.path.join(output_dir, f"response_{ollama_model}_{timestamp}.json")
                with open(output_path_ollama, "w", encoding="utf-8") as f:
                    json.dump({
                        "model": ollama_model,
                        "file": filename,
                        "topic": topic,
                        "prompt": prompt,
                        "answer": answer_ollama
                    }, f, ensure_ascii=False, indent=2)

                print(f"✅ Response from {ollama_model} saved to: {output_path_ollama}")
                generated_answers[str(idx)] = output_path_ollama
            else:
                print(f"⚠️ Could not get response from {ollama_model}")
            idx += 1

    # --- Interactive inspection menu ----------------------------------------
    while True:
        print("\n📋 Available responses:")
        for option, filepath in generated_answers.items():
            model_name = os.path.basename(filepath).replace("response_", "").replace(".json", "")
            print(f"{option}. {model_name}")

        print("0. Exit")

        choice = input("\nSelect an option to display the response: ")

        if choice == "0":
            print("👋 Exiting menu.")
            break
        elif choice in generated_answers:
            ds.show_formatted_answer(generated_answers[choice])
        else:
            print("❌ Invalid option, try again.")


if __name__ == "__main__":
    main()

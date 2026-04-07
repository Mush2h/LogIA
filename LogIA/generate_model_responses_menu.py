import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from src.dataset import Dataset
from src.model_client import (
    build_openai_model, query_openai,
    query_deepinfra, clean_deepseek_response
)
from lib.parse_logs import parse_logs

load_dotenv()

output_dir = "model_responses"
os.makedirs(output_dir, exist_ok=True)

ALL_MODELS = ["openai", "phi4", "deepseek-r1_32b", "llama3.2"]


# Utility functions ------------------------------------------------------------

def select_models():
    print("\nSelect the model(s) you want to use:")
    print("1. All models")
    print("2. Only OpenAI GPT-4")
    print("3. Only DeepInfra - phi4")
    print("4. Only DeepInfra - deepseek-r1:32b")
    print("5. Only DeepInfra - llama3.2")

    option = input("Enter the number of your choice: ").strip()
    mapping = {
        "1": ALL_MODELS,
        "2": ["openai"],
        "3": ["phi4"],
        "4": ["deepseek-r1_32b"],
        "5": ["llama3.2"],
    }
    if option not in mapping:
        print("Invalid option. Using all models by default.")
        return ALL_MODELS
    return mapping[option]


def query_model(model_id, prompt, llm=None):
    """Query a single model. Returns (model_id, response)."""
    if model_id == "openai":
        response = query_openai(llm, prompt)
    else:
        response = query_deepinfra(prompt, model_id)
        if model_id == "deepseek-r1_32b":
            response = clean_deepseek_response(response)
    return model_id, response


def save_response(model_id, filename, topic, prompt, answer, timestamp):
    output_path = os.path.join(output_dir, f"response_{model_id}_{timestamp}.json")
    display_name = "openai_gpt4" if model_id == "openai" else model_id
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": display_name,
            "file": filename,
            "topic": topic,
            "prompt": prompt,
            "answer": answer
        }, f, ensure_ascii=False, indent=2)
    print(f"Response from {display_name} saved to: {output_path}")
    return output_path


# Main pipeline ----------------------------------------------------------------

def main():
    ds = Dataset("data/")
    topic = "Topic 1 - Basic Events"
    filename = "simulated_parsed_logs_by_unique_rule_description.json"

    print("Parsing input logs...")
    parse_logs("data/simulated_events.csv", "simulated")

    prompt = ds.generate_prompt(filename, topic)
    print("\nGenerated prompt:\n")
    print(prompt)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    models_to_use = select_models()

    llm = build_openai_model() if "openai" in models_to_use else None

    generated_answers = {}

    # Query all selected models in parallel
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(query_model, m, prompt, llm): m
            for m in models_to_use
        }
        for future in as_completed(futures):
            model_id = futures[future]
            try:
                model_id, response = future.result()
                if response:
                    path = save_response(model_id, filename, topic, prompt, response, timestamp)
                    generated_answers[model_id] = path
                else:
                    print(f"Could not get response from {model_id}")
            except Exception as e:
                print(f"Error querying {model_id}: {e}")

    # Interactive inspection menu
    while True:
        print("\nAvailable responses:")
        options = list(generated_answers.keys())
        for i, model_id in enumerate(options, 1):
            print(f"{i}. {model_id}")
        print("0. Exit")

        choice = input("\nSelect an option to display the response: ").strip()
        if choice == "0":
            print("Exiting menu.")
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(options):
            ds.show_formatted_answer(generated_answers[options[int(choice) - 1]])
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()

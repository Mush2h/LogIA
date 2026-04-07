import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from src.dataset import Dataset, QUESTIONS
from src.model_client import (
    build_openai_model, query_openai,
    query_deepinfra, clean_deepseek_response, DEEPINFRA_MODELS
)
from lib.parse_logs import parse_logs

load_dotenv()

OUTPUT_DIR = "responses_by_topic"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# All available models: OpenAI GPT-4 + DeepInfra hosted models
MODELS = {
    "openai":          "openai_gpt4",
    "phi4":            "phi4",
    "deepseek-r1_32b": "deepseek-r1_32b",
    "llama3.2":        "llama3.2",
}


# Utility functions ------------------------------------------------------------

def format_model_response(model, file, topic, questions, response_text, timestamp):
    lines = [line.strip("- ").strip() for line in response_text.strip().split("\n") if line.strip()]
    questions_answers = {}
    for i, question in enumerate(questions):
        questions_answers[question] = lines[i] if i < len(lines) else "(No answer)"
    return {
        "model": model,
        "file": file,
        "topic": topic,
        "questions_answers": questions_answers,
        "timestamp": timestamp
    }


def save_response(model, topic, filename, questions, response, timestamp):
    topic_dir = os.path.join(OUTPUT_DIR, topic.replace(" ", "_").lower())
    os.makedirs(topic_dir, exist_ok=True)
    file_out = os.path.join(topic_dir, f"response_{model}_{timestamp}.json")
    structure = format_model_response(model, filename, topic, questions, response, timestamp)
    with open(file_out, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"Saved: {file_out}")


DATASETS = {
    "real":      ("data/real_events.csv",       "real_parsed_logs_by_unique_rule_description.json"),
    "simulated": ("data/simulated_events.csv",  "simulated_parsed_logs_by_unique_rule_description.json"),
}


def select_dataset():
    print("\nSelect the dataset to analyze:")
    print("1. Real logs")
    print("2. Simulated logs")
    print("3. Both")

    option = input("Enter the number of your choice: ").strip()
    if option == "1":
        return ["real"]
    elif option == "2":
        return ["simulated"]
    elif option == "3":
        return ["real", "simulated"]
    print("Invalid option. Using simulated by default.")
    return ["simulated"]


def select_topic(topics):
    print("\nSelect a topic to analyze:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    print(f"{len(topics)+1}. ALL topics")

    option = input("Enter the number of your choice: ").strip()
    if option.isdigit():
        idx = int(option)
        if 1 <= idx <= len(topics):
            return [topics[idx - 1]]
        elif idx == len(topics) + 1:
            return topics

    print("Invalid option. Running ALL topics by default.")
    return topics


def query_model(model_id, model_name, prompt, llm=None):
    """Query a single model and return (model_id, model_name, response)."""
    if model_id == "openai":
        response = query_openai(llm, prompt)
    else:
        response = query_deepinfra(prompt, model_id)
        if model_id == "deepseek-r1_32b":
            response = clean_deepseek_response(response)
    return model_id, model_name, response


# Main pipeline ----------------------------------------------------------------

def main():
    ds = Dataset("data")
    all_topics = list(QUESTIONS.keys())

    selected_datasets = select_dataset()
    selected_topics = select_topic(all_topics)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build OpenAI client once (reused across all datasets and topics)
    llm = build_openai_model()

    for dataset_key in selected_datasets:
        csv_path, filename = DATASETS[dataset_key]
        print(f"\nParsing {dataset_key} logs...")
        parse_logs(csv_path, dataset_key)
        print(f"Log file: {filename}")

        for topic in selected_topics:
            print(f"\nDataset: {dataset_key} | Topic: {topic}")
            prompt = ds.generate_prompt(filename, topic)
            questions = ds.get_questions_by_topic(topic)

            # Query all models in parallel
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(query_model, model_id, model_name, prompt, llm): model_name
                    for model_id, model_name in MODELS.items()
                }
                for future in as_completed(futures):
                    model_name = futures[future]
                    try:
                        model_id, model_name, response = future.result()
                        if response:
                            save_response(model_name, topic, filename, questions, response, timestamp)
                        else:
                            print(f"No response received from {model_name}.")
                    except Exception as e:
                        print(f"Error with model {model_name}: {e}")

    print("\nProcess completed.")


if __name__ == "__main__":
    main()

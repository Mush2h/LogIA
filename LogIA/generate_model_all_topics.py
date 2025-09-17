import os
import json
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI as LlamaOpenAI
from src.dataset import Dataset
from lib.parse_logs import parse_logs

load_dotenv()

OUTPUT_DIR = "responses_by_topic"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODELS = {
    "openai": "openai_gpt4",
    "phi4": "phi4",
    "deepseek-r1_32b": "deepseek-r1_32b",
    "llama3.2": "llama3.2"
}

# 🔧 New function to structure the response
def format_model_response(model, file, topic, questions, response_text, timestamp):
    lines = [line.strip("- ").strip() for line in response_text.strip().split("\n") if line.strip()]
    questions_answers = {}
    for i, question in enumerate(questions):
        if i < len(lines):
            questions_answers[question] = lines[i]
        else:
            questions_answers[question] = "(No answer)"
    return {
        "model": model,
        "file": file,
        "topic": topic,
        "questions_answers": questions_answers,
        "timestamp": timestamp
    }

def build_openai_model():
    return LlamaOpenAI(
        model="gpt-4",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )

def query_openai(llm, prompt):
    return llm.complete(prompt).text

def query_ollama_api(prompt, model="phi4", base_url="http://localhost:11435"):
    url = f"{base_url}/api/generate"
    payload = {"model": model, "prompt": prompt, "temperature": 0.1, "stream": True}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=300)
        response.raise_for_status()
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    obj = json.loads(line)
                    if "response" in obj:
                        full_response += obj["response"]
                except json.JSONDecodeError:
                    print(f"⚠️ Error decoding line: {line}")
        return full_response.strip()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error querying Ollama API: {e}")
        return None

def save_response(model, topic, filename, questions, response, timestamp):
    topic_dir = os.path.join(OUTPUT_DIR, topic.replace(" ", "_").lower())
    os.makedirs(topic_dir, exist_ok=True)

    file_out = os.path.join(topic_dir, f"response_{model}_{timestamp}.json")
    structure = format_model_response(
        model=model,
        file=filename,
        topic=topic,
        questions=questions,
        response_text=response,
        timestamp=timestamp
    )

    with open(file_out, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved: {file_out}")

def select_topic(topics):
    print("\n📚 Select a topic to analyze:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    print(f"{len(topics)+1}. ALL topics")

    option = input("👉 Enter the number of your choice: ").strip()

    if option.isdigit():
        idx = int(option)
        if 1 <= idx <= len(topics):
            return [topics[idx - 1]]
        elif idx == len(topics) + 1:
            return topics
    print("❌ Invalid option. Running ALL topics by default.")
    return topics

def main():
    ds = Dataset("data/")
    filename = "parsed_logs_by_unique_rule_description.json"  # Change if you want to evaluate another file

    print("🚀 Parsing input logs...")
    parse_logs("data/simulated_events.csv", "simulated")

    
    # print the log file to be analyzed
    print("\n📂 Log file to analyze:"
          f"\n{filename}")

    all_topics = list(ds._Dataset__questions.keys())
    selected_topics = select_topic(all_topics)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for topic in selected_topics:
        print(f"\n📂 Selected topic: {topic}")
        prompt = ds.generate_prompt(filename, topic)
        questions = ds.get_questions_by_topic(topic)

        for model_id, model_name in MODELS.items():
            print(f"🤖 Querying model: {model_name}")
            try:
                if model_id == "openai":
                    llm = build_openai_model()
                    response = query_openai(llm, prompt)
                else:
                    response = query_ollama_api(prompt, model=model_id.replace("_", ":"))

                if model_id == "deepseek-r1_32b":
                    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

                if response:
                    save_response(model_name, topic, filename, questions, response, timestamp)
                else:
                    print(f"⚠️ No response received from {model_name}.")
            except Exception as e:
                print(f"❌ Error with model {model_name}: {e}")

    print("\n✅ Process completed.")

if __name__ == "__main__":
    main()

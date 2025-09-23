import os
import json
import datetime
from dotenv import load_dotenv

from src.evaluator_human import GroundTruthEvaluator
from src.evaluator_openAI import Evaluator

# Load environment variables (e.g., OpenAI API key)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 📁 Path to ground truth file (for evaluation based on correct answers)
ground_truth_path = "eval/ground_truth_simulated.json"

# 📁 Directory containing model responses to evaluate
# Uncomment/change the desired topic folder as needed
# responses_dir = "responses_by_topic/topic_1_-_basic_events"
# responses_dir = "responses_by_topic/topic_2_-_content_summary"
# responses_dir = "responses_by_topic/topic_3_-_patterns_errors_anomalies"
# responses_dir = "responses_by_topic/topic_4_-_conclusions"
responses_dir = "responses_by_topic/topic_5_-_multiple_choice_questions"


# 🔧 Utility functions ---------------------------------------------------------

def load_responses_from_directory(directory):
    """
    Load model responses from JSON files within a given directory.

    Args:
        directory (str): Path to directory containing response files.

    Returns:
        dict: Dictionary mapping model name -> response content.
    """
    responses = {}
    for file_name in os.listdir(directory):
        if not file_name.endswith(".json"):
            continue
        path = os.path.join(directory, file_name)
        try:
            with open(path, encoding="utf-8") as f:
                content = json.load(f)
                model = content.get("model")
                if model:
                    responses[model] = content
        except Exception as e:
            print(f"❌ Error loading {file_name}: {e}")
    return responses


def load_ground_truth(path=ground_truth_path):
    """
    Load the ground truth file for evaluation.

    Args:
        path (str): Path to ground truth JSON file.

    Returns:
        dict: Parsed ground truth content.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ground truth file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(results, base_file_name):
    """
    Save evaluation results to a JSON file with timestamp.

    Args:
        results (dict): Evaluation results.
        base_file_name (str): Base name for the results file.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"results_{base_file_name}_{timestamp}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📝 Results saved to: {file_name}")


def evaluation_menu():
    """
    Interactive menu to select evaluation mode.

    Returns:
        str: One of ["groundtruth", "gpt", "gpt_vs_groundtruth"]
    """
    print("\n🔎 How do you want to evaluate the generated responses?")
    print("1. Use Ground Truth")
    print("2. Use GPT-4 as reference")
    print("3. Use GPT-4 comparing with Ground Truth")
    option = input("👉 Enter the number of your choice: ").strip()

    if option == "1":
        return "groundtruth"
    elif option == "2":
        return "gpt"
    elif option == "3":
        return "gpt_vs_groundtruth"
    else:
        print("❌ Invalid option. Using Ground Truth by default.")
        return "groundtruth"


# 🚀 Main pipeline ------------------------------------------------------------

def main():
    """
    Main evaluation workflow:
    1. Load responses from the selected topic directory.
    2. Ask the user to select evaluation mode.
    3. Run evaluation using:
       - Ground truth answers
       - GPT-4 as a reference model
       - GPT-4 comparing against ground truth
    4. Print results and save them to timestamped JSON files.
    """
    eval_mode = evaluation_menu()
    responses_dict = load_responses_from_directory(responses_dir)

    if eval_mode == "groundtruth":
        print("\n📊 Evaluation based on correct answers (Ground Truth)")
        ground_truth = load_ground_truth()
        evaluator = GroundTruthEvaluator(responses_dict, ground_truth)
        results = evaluator.evaluate_all_models()

        for model, result in results.items():
            print(f"\n🔍 Model: {model}")
            print(f"✅ Correct: {result['correct']}/{result['total']} | Score: {result['score']}/10")
            for question, detail in result["details"].items():
                print(f"\n❓ {question}\n{detail}")

        save_results(results, "groundtruth")

    elif eval_mode == "gpt":
        print("\n🤖 Evaluation based on GPT-4 as reference")
        reference_model = next((m for m in responses_dict if "gpt4" in m.lower()), None)
        if not reference_model:
            raise ValueError("❌ No GPT-4 reference response found.")

        print(f"🎯 Using '{reference_model}' as reference model.")
        evaluator = Evaluator(responses_dict, api_key, reference_model=reference_model)
        results = evaluator.evaluate_models_with_openai()

        for model, result in results.items():
            print(f"\n📊 Evaluation for {model}:\n")
            print(result.get("evaluation", "❌ Evaluation not available"))

        save_results(results, "gpt_vs_gpt")

    elif eval_mode == "gpt_vs_groundtruth":
        print("\n🤖 Evaluation performed by GPT-4 comparing against Ground Truth")
        ground_truth = load_ground_truth()

        evaluator = Evaluator(
            answers_dict=responses_dict,
            openai_api_key=api_key,
            ground_truth=ground_truth
        )
        results = evaluator.evaluate_models_with_groundtruth_openai()

        for model, result in results.items():
            print(f"\n📊 Evaluation for {model}:\n")
            print(result.get("evaluation", "❌ Evaluation not available"))

        save_results(results, "gpt_vs_groundtruth")


if __name__ == "__main__":
    main()

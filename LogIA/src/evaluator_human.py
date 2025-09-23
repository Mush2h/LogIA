import os
import json

class GroundTruthEvaluator:
    """
    Evaluator class for comparing model answers directly against a predefined ground truth.

    This evaluation does not use GPT-4; instead, it performs a strict comparison
    between each model's answers and the expected ground truth answers.

    Attributes:
        answers (dict): Dictionary with model responses.
        ground_truth (dict): Dictionary with ground truth answers, keyed by topic.
    """

    def __init__(self, answers_dict, ground_truth_dict):
        """
        Initialize the GroundTruthEvaluator.

        Args:
            answers_dict (dict): Model answers (per topic).
            ground_truth_dict (dict): Ground truth answers (per topic).
        """
        self.answers = answers_dict
        self.ground_truth = ground_truth_dict


    def evaluate_model_response(self, model_data):
        """
        Evaluate a single model's response against the ground truth.

        Args:
            model_data (dict): Response data for one model, containing:
                - topic (str): Topic being evaluated.
                - questions_answers (dict): Model's answers to questions.

        Returns:
            dict: Evaluation result including:
                - topic (str)
                - file (str)
                - score (float, 0–10 scale)
                - correct (int): Number of correct answers
                - total (int): Total number of expected answers
                - details (dict): Per-question evaluation (✅ correct / ❌ incorrect)
        """
        topic = model_data.get("topic")
        model_answers = model_data.get("questions_answers", {})
        expected_answers = self.ground_truth.get(topic, {})

        correct = 0
        total = len(expected_answers)
        details = {}

        # Compare each expected answer against the model answer
        for question, expected_answer in expected_answers.items():
            model_answer = model_answers.get(question, "").strip()

            if model_answer.lower() == expected_answer.lower():
                # Correct answer
                details[question] = (
                    f"✅ Correct\n    Expected: {expected_answer}\n    Model: {model_answer}"
                )
                correct += 1
            else:
                # Incorrect answer
                details[question] = (
                    f"❌ Incorrect\n    Expected: {expected_answer}\n    Model: {model_answer}"
                )

        # Compute score on a 0–10 scale
        score = round((correct / total) * 10, 2) if total > 0 else 0

        return {
            "topic": topic,
            "file": model_data.get("file"),
            "score": score,
            "correct": correct,
            "total": total,
            "details": details
        }


    def evaluate_all_models(self):
        """
        Evaluate all models contained in `self.answers`.

        Iterates over all models and compares their answers against ground truth.

        Returns:
            dict: Evaluation results for all models, keyed by model name.
        """
        results = {}
        for model, data in self.answers.items():
            print(f"📊 Evaluating model: {model}")
            results[model] = self.evaluate_model_response(data)
        return results

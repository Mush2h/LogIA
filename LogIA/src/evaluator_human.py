import os
import json

class GroundTruthEvaluator:
    def __init__(self, answers_dict, ground_truth_dict):
        self.answers = answers_dict
        self.ground_truth = ground_truth_dict

    def evaluate_model_response(self, model_data):
        topic = model_data.get("topic")
        model_answers = model_data.get("questions_answers", {})
        expected_answers = self.ground_truth.get(topic, {})

        correct = 0
        total = len(expected_answers)
        details = {}

        for question, expected_answer in expected_answers.items():
            model_answer = model_answers.get(question, "").strip()

            if model_answer.lower() == expected_answer.lower():
                # Show both the expected and model answers even if they match
                details[question] = (
                    f"✅ Correct\n    Expected: {expected_answer}\n    Model: {model_answer}"
                )
                correct += 1
            else:
                details[question] = (
                    f"❌ Incorrect\n    Expected: {expected_answer}\n    Model: {model_answer}"
                )

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
        results = {}
        for model, data in self.answers.items():
            print(f"📊 Evaluating model: {model}")
            results[model] = self.evaluate_model_response(data)
        return results

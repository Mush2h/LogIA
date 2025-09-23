
# 📑 Log Analysis & LLM Model Evaluation Framework


This repository provides a framework for **parsing real and simulated logs**, generating **responses from multiple LLMs**, and **evaluating model performance** against a ground truth dataset.  
It is designed for research and experimentation in the intersection of **log analysis, AI-assisted cybersecurity, and model benchmarking**.

---

## 📂 Repository Structure

```
├── data/                           # Real and simulated datasets
│   ├── real_events.csv
│   ├── real_parsed_logs_all.json
│   ├── real_parsed_logs_by_unique_rule_description.json
│   ├── real_parsed_logs_filtered.json
│   ├── simulated_events.csv
│   ├── simulated_parsed_logs_all.json
│   ├── simulated_parsed_logs_by_unique_rule_description.json
│   └── simulated_parsed_logs_filtered.json
│
├── eval/
│   └── ground_truth_simulated.json # Ground truth for evaluation
│
├── evaluate_models.py              # Main evaluation script
├── generate_model_all_topics.py    # Generate responses for all topics
├── generate_model_responses_menu.py# Generate responses via interactive menu
│
├── lib/
│   ├── parse_logs.py               # Log parsing utilities
│   └── __pycache__/                # Compiled Python files
│
├── model_responses/                # Generated model responses (JSON format)
│
├── requirements.txt                # Python dependencies
│
├── responses_by_topic/             # Responses organized by topic
│   └── topic_1_-_basic_events/
│       ├── response_deepseek-r1_32b_20250917_130244.json
│       ├── response_llama3.2_20250917_130244.json
│       ├── response_openai_gpt4_20250917_130157.json
│       ├── response_openai_gpt4_20250917_130244.json
│       └── response_phi4_20250917_130244.json
│
└── src/
    ├── dataset.py                  # Dataset handling and preprocessing
    ├── evaluator_human.py          # Human-based evaluation
    ├── evaluator_openAI.py         # Automated evaluation with OpenAI
    └── __pycache__/                # Compiled Python files
```

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mush2h/LogIA 
   cd LogIA
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧑‍💻 Usage

### 1. Generate Model Responses
- Generate responses for **all topics**:
  ```bash
  python generate_model_all_topics.py
  ```

- Generate responses via **interactive menu**:
  ```bash
  python generate_model_responses_menu.py
  ```

### 2. Evaluate Model Performance
- Compare generated responses against the ground truth:
  ```bash
  python evaluate_models.py
  ```

### 3. Log Parsing
- Import and use the log parsing utilities:
  ```python
  from lib.parse_logs import parse_logs
  ```

---

## 📊 Evaluation Methodology

- **Automated Evaluation**: `evaluator_openAI.py` leverages LLMs for consistency scoring.  
- **Human Evaluation**: `evaluator_human.py` enables manual assessment for subjective or qualitative aspects.  
- **Datasets**: Located under `data/`  
- **Ground Truth**: Defined in `eval/ground_truth_simulated.json`  

This dual evaluation approach ensures both **quantitative benchmarking** and **qualitative insights**.

---

## 🤝 Contributing

Contributions are welcome!  
To contribute:  

1. Fork this repository  
2. Create a new branch:  
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes  
4. Open a Pull Request 🚀  

---

## 📜 License

This project is distributed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

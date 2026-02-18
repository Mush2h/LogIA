
# 📑 LogIA – Log Intelligence & Evaluation Framework
<p align="center"> <img src="assets/logia_logo.jpg" alt="LogIA Logo" width="300"/> </p> <p align="center"> <strong>AI-Powered Log Analysis & LLM Evaluation</strong> </p>


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

4. Set up your OpenAI API key as an environment variable (required for automated evaluation with `evaluator_openAI.py`):
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
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


---
## 🧪 Evaluation Questions

The framework evaluates models across multiple analytical dimensions using the following structured question set:

### 📌 Topic 1 – Basic Events

How many events are in the log file summing the count field?

How many different agents appear and what are their names?

Which type of event is the most critical according to its level?

Which event is repeated the most times?

### 📌 Topic 2 – Content Summary

Summarize in one line what is happening in the system.

### 📌 Topic 3 – Patterns, Errors or Anomalies

Do you detect any anomalous behavior in these logs?

Are there failed access attempts? Which alert indicates this?

Are there problematic files? Which ones?

### 📌 Topic 4 – Conclusions

What could be causing the observed errors?

Suggest possible solutions for the detected errors.

Are there signs of any type of attack? Which one(s)?

What would be your general diagnosis of the system state according to these logs?

### 📌 Topic 5 – Multiple Choice Questions

What type of attack is detected in multiple log entries?
A) Port scan
B) Denial of Service (DoS)
C) SSH brute force
D) SQL injection
E) None of the above

Which file was identified with multiple malicious YARA rules?
A) /etc/passwd
B) /home/mirai
C) /var/log/auth.log
D) /home/unknown
E) None of the above

What is the highest severity level of the events detected by YARA rules?
A) 3
B) 12
C) 7
D) 10
E) None of the above

What is the most critical event related to sshd?
A) Successful password change
B) Authorized root access
C) Failed brute-force authentication
D) Session closed
E) None of the above

Which agent is logging all the events?
A) agent-centos
B) agent-debian
C) agent-ubuntu
D) agent-fedora
E) None of the above

What type of files were detected as malicious by YARA rules?
A) .docx files
B) .conf files
C) Suspicious files in /home/
D) System executable files
E) None of the above

## 📜 License

This project is distributed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

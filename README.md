
# 📑 LogIA – Log Intelligence & Evaluation Framework
<p align="center"> <img src="Logia.png" alt="LogIA Logo" width="400"/> </p> <p align="center">

This repository provides a framework for **parsing real and simulated logs** and generating **responses from multiple LLMs** to assist in AI-assisted cybersecurity research and log analysis.  
Evaluation is performed manually against a ground truth dataset.

---

## 📂 Repository Structure

```
├── data/                           # Simulated datasets
│   ├── simulated_events.csv
│   ├── simulated_parsed_logs_all.json
│   ├── simulated_parsed_logs_by_unique_rule_description.json
│   └── simulated_parsed_logs_filtered.json
│
├── eval/
│   ├── ground_truth_simulated.json # Ground truth for manual evaluation
│   └── ground_truth_real.json
│
├── generate_model_all_topics.py    # Generate responses for all topics
├── generate_model_responses_menu.py# Generate responses via interactive menu
│
├── lib/
│   └── parse_logs.py               # Log parsing utilities (CSV → JSON)
│
├── model_responses/                # Generated model responses (JSON format)
│
├── requirements.txt                # Python dependencies
│
├── responses_by_topic/             # Responses organized by topic
│
└── src/
    ├── dataset.py                  # Dataset handling and prompt generation
    └── model_client.py             # Unified client for OpenAI and DeepInfra
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

4. Create a `.env` file in the `LogIA/` directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DEEPINFRA_API_KEY=your_deepinfra_api_key_here
   ```

---

## 🤖 Models Used

| Model | Provider |
|---|---|
| GPT-4 | OpenAI |
| microsoft/phi-4 | DeepInfra |
| deepseek-ai/DeepSeek-R1 | DeepInfra |
| meta-llama/Llama-3.2-11B-Vision-Instruct | DeepInfra |

---

## 🧑‍💻 Usage

### Generate model responses for all topics
```bash
python generate_model_all_topics.py
```

### Generate responses via interactive menu (Topic 1)
```bash
python generate_model_responses_menu.py
```

Responses are saved as JSON files in `responses_by_topic/` and `model_responses/`.

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

---

## 📜 License

This project is distributed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

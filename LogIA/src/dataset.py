import json
from pathlib import Path
from typing import List, Dict

# --------------------------
#  Questions per topic
# --------------------------
QUESTIONS = {
    "Topic 1 - Basic Events": [
        "How many events are in the log file summing the count field?",
        "How many different agents appear and what are their names?",
        "Which type of event is the most critical according to its level?",
        "Which event is repeated the most times?",
    ],
    "Topic 2 - Content Summary": [
        "Summarize in one line what is happening in the system."
    ],
    "Topic 3 - Patterns, Errors or Anomalies": [
        "Do you detect any anomalous behavior in these logs?",
        "Are there failed access attempts? Which alert indicates this?",
        "Are there problematic files? Which ones?"
    ],
    "Topic 4 - Conclusions": [
        "What could be causing the observed errors?",
        "Suggest possible solutions for the detected errors.",
        "Are there signs of any type of attack? Which one(s)?",
        "What would be your general diagnosis of the system state according to these logs?"
    ],
    "Topic 5 - Multiple Choice Questions": [
    "What type of attack is detected in multiple log entries?\nA) Port scan\nB) Denial of Service (DoS)\nC) SSH brute force\nD) SQL injection\nE) None of the above",
    "Which file was identified with multiple malicious YARA rules?\nA) /etc/passwd\nB) /home/mirai\nC) /var/log/auth.log\nD) /home/unknown\nE) None of the above",
    "What is the highest severity level of the events detected by YARA rules?\nA) 3\nB) 12\nC) 7\nD) 10\nE) None of the above",
    "What is the most critical event related to sshd?\nA) Successful password change\nB) Authorized root access\nC) Failed brute-force authentication\nD) Session closed\nE) None of the above",
    "Which agent is logging all the events?\nA) agent-centos\nB) agent-debian\nC) agent-ubuntu\nD) agent-fedora\nE) None of the above",
    "What type of files were detected as malicious by YARA rules?\nA) .docx files\nB) .conf files\nC) Suspicious files in /home/\nD) System executable files\nE) None of the above"
    ]
}

# --------------------------
# Response styles per topic
# --------------------------
RESPONSE_STYLES = {
    "Topic 1 - Basic Events": (
        "Answer briefly and directly. Use the following format exclusively without adding extra:\n"
        "There are X events.\n"
        "There are Y agents: name1, name2...\n"
        "The most critical event is DESCRIPTION with level N.\n\n"
        "The most repeated event is DESCRIPTION , N times\n\n"
    ),
    "Topic 2 - Content Summary": (
        "Be as precise as possible, do not add an introduction\n"
    ),
    "Topic 3 - Patterns, Errors or Anomalies": (
        "Answer briefly and directly, omit unnecessary characters, and write in one line without introduction. Use the following format:\n"
        "Choose Yes or No and explain what it is\n"
        "Choose Yes or No and indicate which alert\n"
        "List problematic file names\n\n"
    ),
    "Topic 4 - Conclusions": (
        "Answer using this template format as briefly as possible, omitting unnecessary characters and without an introduction, in one line:\n"
        "Possible cause of errors: ...\n"
        "Suggested solutions: ...\n"
        "Signs of attack: Yes/No, type: ...\n"
        "General diagnosis: ...\n\n"
    ),
    "Topic 5 - Multiple Choice Questions": (
    "Responde exclusivamente con la letra para cada pregunta, sin justificación, omitiendo caracteres innecesarios y escribiendo directamente:\n"
    "1: A/B/C/D/E\n"
    "2: A/B/C/D/E\n"
    "3: A/B/C/D/E\n"
    "4: A/B/C/D/E\n"
    "5: A/B/C/D/E\n"
    "6: A/B/C/D/E\n"
    )
}

# --------------------------
# One-shot example of input logs + expected answer
# --------------------------
ONE_SHOT_EXAMPLES = {
    "Topic 1 - Basic Events": {
        "logs": [
            {
                "timestamp": 1749969974273,
                "agent.name": "clavo.ugr.es",
                "rule.level": 11,
                "rule.id": 521,
                "rule.description": "Possible kernel level rootkit",
                "recuento": 6
            },
            {
                "timestamp": 1749465036918,
                "agent.name": "hera.ugr.es",
                "rule.level": 10,
                "rule.id": 2502,
                "rule.description": "syslog: User missed the password more than one time",
                "recuento": 1
            },
            {
                "timestamp": 1750758711146,
                "agent.name": "hera.ugr.es",
                "rule.level": 10,
                "rule.id": 80711,
                "rule.description": "Auditd: Process ended abnormally.",
                "recuento": 1
            }
        ],
        "respuesta": (
            "There are 8 events.\n"
            "There are 2 agents: clavo.ugr.es, hera.ugr.es\n"
            "The most critical event is Possible kernel level rootkit with level 11.\n"
            "The most repeated event is syslog: Possible kernel level rootkit with a count of 6.\n"
        )
    }
}

# --------------------------
# Main Dataset class
# --------------------------
class Dataset:
    def __init__(self, data_path: str):
        """
        Initialize the Dataset class, validating the existence of the directory with .json files.
        """
        self.data_path = Path(data_path).resolve()
        if not self.data_path.exists():
            raise FileNotFoundError("The path does not exist. Verify the JSON files.")
        self.files = self._get_json_files()

    def _get_json_files(self) -> List[Path]:
        """
        Get all JSON files in the specified directory.
        """
        return list(self.data_path.glob("*.json"))

    def load_logs(self, file_name: str) -> List[Dict]:
        """
        Load logs from a JSON file line by line.
        """
        file_path = self.data_path / file_name
        with file_path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def get_questions_by_topic(self, topic: str) -> List[str]:
        """
        Return the list of questions associated with a topic.
        """
        return QUESTIONS.get(topic, [])

    def _get_response_style(self, topic: str) -> str:
        """
        Get the response style for the given topic.
        """
        return RESPONSE_STYLES.get(topic, "")

    def generate_prompt(self, file_name: str, topic: str) -> str:
        """
        Generate the prompt for the model combining:
        - Real logs (sample)
        - A one-shot example (if applicable)
        - The required style
        - The topic questions
        """
        logs = self.load_logs(file_name)[:44]
        style = self._get_response_style(topic)
        questions = "\n".join(self.get_questions_by_topic(topic))
        prompt = "Answer the questions strictly following the templates as precisely as possible.\n"

        # If there is a one-shot example for the topic, include it
        if one_shot := ONE_SHOT_EXAMPLES.get(topic):
            prompt += "\n### Example:\n"
            prompt += json.dumps(one_shot["logs"], indent=2) + "\n"
            prompt += one_shot["respuesta"] + "\n"

        # Add real logs + style + questions
        prompt += "\n### Real logs:\n"
        prompt += json.dumps(logs, indent=2) + "\n\n"
        prompt += style + questions
        return prompt

    def show_formatted_answer(self, answer_file: str):
        """
        Print a generated answer from a JSON file with the following format:
        {
            "model": "...",
            "file": "...",
            "topic": "...",
            "answer": "..."
        }
        """
        file_path = Path(answer_file)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        print("\n📄 File Information:")
        print(f"Model: {data.get('model', 'Unknown')}")
        print(f"Analyzed file: {data.get('file', 'Unknown')}")
        print(f"Topic: {data.get('topic', 'Unknown')}")

        print("\n📝 Questions and Answers:")
        answer = data.get("answer", "")
        if isinstance(answer, str):
            print("\n" + answer)
        else:
            print("\n(No text-formatted answer was found.)")
